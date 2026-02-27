"""CLI entry point."""

import click
from pathlib import Path
from . import config, git_ops, identity, aggregation, rendering


@click.group()
def cli():
    """OpenRail Metrics - Quarterly metrics reporting tool."""
    pass


@cli.command()
@click.option('--projects', type=Path, default='projects.yml', help='Projects configuration file')
@click.option('--report', type=Path, default='report.yml', help='Report configuration file')
@click.option('--cache-dir', type=Path, default='repos-cache', help='Repository cache directory')
@click.option('--output-dir', type=Path, default='out', help='Output directory')
def all(projects, report, cache_dir, output_dir):
    """Run complete pipeline: sync, extract, aggregate, render."""
    
    click.echo("Loading configuration...")
    cfg = config.load_config(projects, report)
    
    click.echo(f"Processing {len(cfg.projects)} projects...")
    
    # Collect all commit events
    commit_events = []
    
    for project in cfg.projects:
        project_id = project['id']
        click.echo(f"\nProject: {project['name']}")
        
        for repo_url in project['repos']:
            click.echo(f"  Syncing {repo_url}...")
            repo_path = git_ops.sync_repo(repo_url, cache_dir)
            
            click.echo(f"  Extracting commits...")
            commits = git_ops.extract_commits(repo_path, cfg.from_date, cfg.to_date)
            
            # Filter merge commits
            commits = [c for c in commits if not c['is_merge']]
            
            click.echo(f"    Found {len(commits)} human commits")
            
            # Process commits into events
            for commit in commits:
                canonical = identity.get_canonical_identity(commit['email'])
                committer_id = identity.pseudonymize(canonical)
                
                commit_events.append({
                    'project_id': project_id,
                    'repo_url': repo_url,
                    'committer_id': committer_id,
                    'date': commit['date'],
                    'hash': commit['hash']
                })
    
    click.echo(f"\nTotal commit events: {len(commit_events)}")
    
    # Aggregate metrics
    click.echo("Aggregating metrics...")
    metrics = aggregation.aggregate_metrics(commit_events)
    
    # Render report
    click.echo("Rendering report...")
    report_path = output_dir / 'report.md'
    rendering.render_report(cfg, metrics, cfg.projects, report_path)
    
    click.echo(f"\nReport generated: {report_path}")
    click.echo(f"Total commits: {metrics['total_commits']}")
    click.echo(f"Total committers: {metrics['total_committers']}")


if __name__ == '__main__':
    cli()
