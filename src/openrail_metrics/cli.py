"""CLI entry point."""

import click
from pathlib import Path
from . import config, git_ops, identity, aggregation, rendering, graphics, pdf, attribution


@click.group()
def cli():
    """OpenRail Metrics - Quarterly metrics reporting tool."""
    pass


@cli.command()
@click.option('--projects', type=Path, default='projects.yml', help='Projects configuration file')
@click.option('--report', type=Path, default='report.yml', help='Report configuration file')
@click.option('--cache-dir', type=Path, default='repos-cache', help='Repository cache directory')
@click.option('--output-dir', type=Path, default='out', help='Output directory')
@click.option('--org-map', type=Path, help='Organization mapping file (SSV)')
def all(projects, report, cache_dir, output_dir, org_map):
    """Run complete pipeline: sync, extract, aggregate, render."""
    
    click.echo("Loading configuration...")
    cfg = config.load_config(projects, report)
    
    # Load org mapping if provided
    org_mapping = None
    if org_map:
        click.echo(f"Loading organization mapping from {org_map}...")
        org_mapping = attribution.load_org_mapping(org_map)
        click.echo(f"  Loaded mappings for {len(org_mapping)} email addresses")
    
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
                org = attribution.get_organization(commit['email'], project_id, org_mapping)
                
                commit_events.append({
                    'project_id': project_id,
                    'repo_url': repo_url,
                    'committer_id': committer_id,
                    'org': org,
                    'date': commit['date'],
                    'hash': commit['hash']
                })
    
    click.echo(f"\nTotal commit events: {len(commit_events)}")
    
    # Aggregate metrics
    click.echo("Aggregating metrics...")
    metrics = aggregation.aggregate_metrics(commit_events)
    
    # Generate graphics
    click.echo("Generating graphics...")
    graphics_dir = output_dir / 'graphics'
    graphics_dir.mkdir(parents=True, exist_ok=True)
    
    graphics.generate_monthly_chart(metrics, graphics_dir / 'monthly_activity.png')
    graphics.generate_project_chart(metrics, cfg.projects, graphics_dir / 'project_distribution.png')
    
    # Generate per-project charts
    for project in cfg.projects:
        project_id = project['id']
        if metrics['projects'].get(project_id, {}).get('commits', 0) > 0:
            graphics.generate_project_monthly_chart(
                project_id, 
                project['name'], 
                metrics, 
                graphics_dir / f'{project_id}_monthly.png'
            )
    
    # Render report
    click.echo("Rendering report...")
    report_path = output_dir / 'report.md'
    rendering.render_report(cfg, metrics, cfg.projects, report_path, graphics_dir)
    
    # Generate PDF
    click.echo("Generating PDF...")
    pdf_path = output_dir / 'report.pdf'
    try:
        pdf.generate_pdf(report_path, pdf_path)
        click.echo(f"PDF generated: {pdf_path}")
    except Exception as e:
        click.echo(f"Warning: PDF generation failed: {e}", err=True)
    
    click.echo(f"\nReport generated: {report_path}")
    click.echo(f"Total commits: {metrics['total_commits']}")
    click.echo(f"Total committers: {metrics['total_committers']}")


if __name__ == '__main__':
    cli()
