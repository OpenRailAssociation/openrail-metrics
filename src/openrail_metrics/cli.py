"""CLI entry point."""

import click
from pathlib import Path
from . import config, git_ops, identity, aggregation, rendering, graphics, pdf, attribution


def get_default_path(filename):
    """Get default path for config files in repo root."""
    return Path(__file__).parent.parent.parent / filename


@click.group()
def cli():
    """OpenRail Metrics - Quarterly metrics reporting tool."""
    pass


@cli.command()
@click.option('--projects', type=Path, default=None, help='Projects configuration file (default: projects.yml in repo)')
@click.option('--cache-dir', type=Path, default=None, help='Repository cache directory (default: repos-cache in repo)')
def sync(projects, cache_dir):
    """Sync all project repositories to local cache."""
    if projects is None:
        projects = get_default_path('projects.yml')
    if cache_dir is None:
        cache_dir = get_default_path('repos-cache')

    click.echo("Loading configuration...")
    cfg = config.load_config(projects, get_default_path('report.yml'))

    click.echo(f"Syncing {len(cfg.projects)} projects...")

    for project in cfg.projects:
        click.echo(f"\nProject: {project['name']}")

        for repo_url in project['repos']:
            click.echo(f"  Syncing {repo_url}...")
            git_ops.sync_repo(repo_url, cache_dir)

    click.echo("\nSync complete!")


@cli.command()
@click.option('--projects', type=Path, default=None, help='Projects configuration file (default: projects.yml in repo)')
@click.option('--report', type=Path, default=None, help='Report configuration file (default: report.yml in repo)')
@click.option('--cache-dir', type=Path, default=None, help='Repository cache directory (default: repos-cache in repo)')
@click.option('--org-map', type=Path, required=True, help='Organization mapping file (SSV format)')
@click.option('--output', type=Path, default='metrics.json', help='Output metrics JSON file')
def extract(projects, report, cache_dir, org_map, output):
    """Extract commits and aggregate metrics. Requires: synced repos, org-map file."""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import json

    if projects is None:
        projects = get_default_path('projects.yml')
    if report is None:
        report = get_default_path('report.yml')
    if cache_dir is None:
        cache_dir = get_default_path('repos-cache')

    click.echo("Loading configuration...")
    cfg = config.load_config(projects, report)

    extended_from_date = cfg.from_date - relativedelta(months=9)

    org_mapping = None
    if org_map:
        click.echo(f"Loading organization mapping from {org_map}...")
        org_mapping = attribution.load_org_mapping(org_map)
        click.echo(f"  Loaded mappings for {len(org_mapping)} email addresses")

    click.echo(f"Processing {len(cfg.projects)} projects...")
    click.echo(f"Extracting commits from {extended_from_date} to {cfg.to_date} (12-month view)")

    commit_events = []

    for project in cfg.projects:
        project_id = project['id']
        click.echo(f"\nProject: {project['name']}")

        for repo_url in project['repos']:
            click.echo(f"  Extracting {repo_url}...")
            repo_path = cache_dir / git_ops.sanitize_repo_name(repo_url) / f"{git_ops.sanitize_repo_name(repo_url)}.git"

            commits = git_ops.extract_commits(repo_path, extended_from_date, cfg.to_date)
            commits = [c for c in commits if not c['is_merge']]
            click.echo(f"    Found {len(commits)} human commits")

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
    click.echo("Aggregating metrics...")
    metrics = aggregation.aggregate_metrics(commit_events, cfg.from_date, cfg.to_date)

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w') as f:
        json.dump(metrics, f, indent=2)

    click.echo(f"Metrics saved to {output}")
    click.echo(f"Total commits: {metrics['total_commits']}")
    click.echo(f"Total contributors: {metrics['total_contributors']}")


@cli.command()
@click.option('--projects', type=Path, default=None, help='Projects configuration file (default: projects.yml in repo)')
@click.option('--metrics', type=Path, default='metrics.json', help='Input metrics JSON file')
@click.option('--output-dir', type=Path, default=None, help='Output directory for report and graphics (default: out in repo)')
def render(projects, metrics, output_dir):
    """Generate graphics and markdown report. Requires: metrics.json."""
    import json

    if projects is None:
        projects = get_default_path('projects.yml')
    if output_dir is None:
        output_dir = get_default_path('out')

    click.echo("Loading configuration...")
    cfg = config.load_config(projects, get_default_path('report.yml'))

    click.echo(f"Loading metrics from {metrics}...")
    with open(metrics, 'r') as f:
        metrics_data = json.load(f)

    click.echo("Generating graphics...")
    graphics_dir = output_dir / 'graphics'
    graphics_dir.mkdir(parents=True, exist_ok=True)

    graphics.generate_monthly_chart(metrics_data, graphics_dir / 'monthly_activity.png')
    graphics.generate_activity_heatmap(metrics_data, cfg.projects, graphics_dir / 'activity_heatmap.png', months=12)
    graphics.generate_project_chart(metrics_data, cfg.projects, graphics_dir / 'project_distribution.png')

    if metrics_data.get('quarter_org_stats'):
        graphics.generate_org_pie_chart(metrics_data, graphics_dir / 'quarter_org_distribution.png', quarter_only=True)

    for project in cfg.projects:
        project_id = project['id']
        project_data = metrics_data['projects'].get(project_id, {})

        if project_data.get('commits', 0) > 0:
            graphics.generate_project_monthly_chart(
                project_id, project['name'], metrics_data,
                graphics_dir / f'{project_id}_monthly.png', months=12
            )
            graphics.generate_project_org_stacked_chart(
                project_id, project['name'], metrics_data,
                graphics_dir / f'{project_id}_trend.png', months=12
            )

    click.echo("Rendering report...")
    report_path = output_dir / 'report.md'
    rendering.render_report(cfg, metrics_data, cfg.projects, report_path, graphics_dir)

    from pathlib import Path as PathLib
    logo_src = PathLib(__file__).parent.parent.parent / 'assets' / 'openrail-logo.png'
    if logo_src.exists():
        import shutil
        shutil.copy(logo_src, output_dir / 'openrail-logo.png')

    click.echo(f"Report generated: {report_path}")


@cli.command()
@click.option('--input', type=Path, default='out/report.md', help='Input markdown report file')
@click.option('--output', type=Path, default='out/report.pdf', help='Output PDF file')
def generate_pdf(input, output):
    """Generate PDF from markdown report. Requires: report.md."""
    click.echo(f"Generating PDF from {input}...")
    try:
        pdf.generate_pdf(input, output)
        click.echo(f"PDF generated: {output}")
    except Exception as e:
        click.echo(f"Error: PDF generation failed: {e}", err=True)


@cli.command()
@click.option('--projects', type=Path, default=None, help='Projects configuration file (default: projects.yml in repo)')
@click.option('--report', type=Path, default=None, help='Report configuration file (default: report.yml in repo)')
@click.option('--cache-dir', type=Path, default=None, help='Repository cache directory (default: repos-cache in repo)')
@click.option('--output-dir', type=Path, default=None, help='Output directory for report and graphics (default: out in repo)')
@click.option('--org-map', type=Path, required=True, help='[REQUIRED] Organization mapping file (SSV format)')
def all(projects, report, cache_dir, output_dir, org_map):
    """Run complete pipeline: sync → extract → render → PDF. Requires: org-map file."""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    if projects is None:
        projects = get_default_path('projects.yml')
    if report is None:
        report = get_default_path('report.yml')
    if cache_dir is None:
        cache_dir = get_default_path('repos-cache')
    if output_dir is None:
        output_dir = get_default_path('out')

    click.echo("Loading configuration...")
    cfg = config.load_config(projects, report)

    # Extend extraction period by 9 months before for 12-month view (9 + 3 quarter months = 12)
    extended_from_date = cfg.from_date - relativedelta(months=9)

    # Load org mapping if provided
    org_mapping = None
    if org_map:
        click.echo(f"Loading organization mapping from {org_map}...")
        org_mapping = attribution.load_org_mapping(org_map)
        click.echo(f"  Loaded mappings for {len(org_mapping)} email addresses")

    click.echo(f"Processing {len(cfg.projects)} projects...")
    click.echo(f"Extracting commits from {extended_from_date} to {cfg.to_date} (12-month view)")

    # Collect all commit events
    commit_events = []

    for project in cfg.projects:
        project_id = project['id']
        click.echo(f"\nProject: {project['name']}")

        for repo_url in project['repos']:
            click.echo(f"  Syncing {repo_url}...")
            repo_path = git_ops.sync_repo(repo_url, cache_dir)

            click.echo(f"  Extracting commits...")
            commits = git_ops.extract_commits(repo_path, extended_from_date, cfg.to_date)

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
    metrics = aggregation.aggregate_metrics(commit_events, cfg.from_date, cfg.to_date)

    # Generate graphics
    click.echo("Generating graphics...")
    graphics_dir = output_dir / 'graphics'
    graphics_dir.mkdir(parents=True, exist_ok=True)

    graphics.generate_monthly_chart(metrics, graphics_dir / 'monthly_activity.png')
    graphics.generate_activity_heatmap(metrics, cfg.projects, graphics_dir / 'activity_heatmap.png', months=12)
    graphics.generate_project_chart(metrics, cfg.projects, graphics_dir / 'project_distribution.png')

    # Generate organization pie chart if org mapping was provided
    if org_mapping and metrics.get('quarter_org_stats'):
        graphics.generate_org_pie_chart(metrics, graphics_dir / 'quarter_org_distribution.png', quarter_only=True)

    # Generate per-project charts
    for project in cfg.projects:
        project_id = project['id']
        project_data = metrics['projects'].get(project_id, {})

        if project_data.get('commits', 0) > 0:
            graphics.generate_project_monthly_chart(
                project_id,
                project['name'],
                metrics,
                graphics_dir / f'{project_id}_monthly.png',
                months=12
            )

            graphics.generate_project_org_stacked_chart(
                project_id,
                project['name'],
                metrics,
                graphics_dir / f'{project_id}_trend.png',
                months=12
            )

            # Remove per-project org pie chart generation

    # Render report
    click.echo("Rendering report...")
    report_path = output_dir / 'report.md'
    rendering.render_report(cfg, metrics, cfg.projects, report_path, graphics_dir)

    # Copy logo to output directory
    from pathlib import Path as PathLib
    logo_src = PathLib(__file__).parent.parent.parent / 'assets' / 'openrail-logo.png'
    if logo_src.exists():
        import shutil
        shutil.copy(logo_src, output_dir / 'openrail-logo.png')

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
    click.echo(f"Total contributors: {metrics['total_contributors']}")


if __name__ == '__main__':
    cli()
