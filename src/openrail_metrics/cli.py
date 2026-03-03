"""CLI entry point."""

import click
from pathlib import Path
from . import config, git_ops, identity, aggregation, rendering, graphics, attribution
from . import pdf as pdf_module


class OrderedGroup(click.Group):
    """Click group that preserves command order."""
    def list_commands(self, ctx):
        return list(self.commands)


def get_default_path(filename):
    """Get default path for config files in repo root."""
    return Path(__file__).parent.parent.parent / filename


@click.group(cls=OrderedGroup)
def cli():
    """OpenRail Metrics - Quarterly metrics reporting tool."""
    pass


def _sync_repos(projects_path, cache_dir):
    """Internal function to sync repositories."""
    import click
    cfg = config.load_config(projects_path, get_default_path('report.yml'))

    click.echo(f"Syncing {len(cfg.projects)} projects...")

    for project in cfg.projects:
        click.echo(f"\nProject: {project['name']}")

        for repo_url in project['repos']:
            click.echo(f"  Syncing {repo_url}...")
            git_ops.sync_repo(repo_url, cache_dir)

    click.echo("\nSync complete!")


def _extract_metrics(projects_path, report_path, cache_dir, org_map, output_path):
    """Internal function to extract and aggregate metrics."""
    import click
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import json

    click.echo("Loading configuration...")
    cfg = config.load_config(projects_path, report_path)

    extended_from_date = cfg.from_date - relativedelta(months=9)

    org_mapping = None
    if org_map:
        click.echo(f"Loading organization mapping from {org_map}...")
        org_mapping = attribution.load_org_mapping(org_map)
        click.echo(f"  Loaded mappings for {len(org_mapping)} email addresses")

    click.echo(f"Processing {len(cfg.projects)} projects...")
    click.echo(f"Extracting commits from {extended_from_date} to {cfg.to_date} (12-month view)")

    commit_events = []
    unmapped_emails = set()

    for project in cfg.projects:
        project_id = project['id']
        click.echo(f"\nProject: {project['name']}")

        for repo_url in project['repos']:
            click.echo(f"  Extracting {repo_url}...")
            repo_name = git_ops.sanitize_repo_name(repo_url)
            repo_path = cache_dir / f"{repo_name}.git"

            commits = git_ops.extract_commits(repo_path, extended_from_date, cfg.to_date)
            commits = [c for c in commits if not c['is_merge']]
            click.echo(f"    Found {len(commits)} human commits")

            for commit in commits:
                canonical = identity.get_canonical_identity(commit['email'])
                committer_id = identity.pseudonymize(canonical)
                org = attribution.get_organization(commit['email'], project_id, org_mapping)

                if org == "Unknown":
                    unmapped_emails.add(commit['email'])

                commit_events.append({
                    'project_id': project_id,
                    'repo_url': repo_url,
                    'committer_id': committer_id,
                    'org': org,
                    'date': commit['date'],
                    'hash': commit['hash']
                })

    click.echo(f"\nTotal commit events: {len(commit_events)}")
    
    if unmapped_emails:
        click.echo(f"\nWarning: {len(unmapped_emails)} email(s) not found in organization mapping:", err=True)
        for email in sorted(unmapped_emails):
            click.echo(f"  - {email}", err=True)
        click.echo(f"These commits will be attributed to 'Unknown' organization.", err=True)
    
    click.echo("Aggregating metrics...")
    metrics = aggregation.aggregate_metrics(commit_events, cfg.from_date, cfg.to_date)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        click.echo(f"Metrics saved to {output_path}")

    click.echo(f"Total commits: {metrics['total_commits']}")
    click.echo(f"Total contributors: {metrics['total_contributors']}")

    return metrics


def _render_report(projects_path, metrics_data, output_dir):
    """Internal function to render report."""
    import click

    click.echo("Loading configuration...")
    cfg = config.load_config(projects_path, get_default_path('report.yml'))

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
@click.option('--projects', type=Path, default=None, help='Projects configuration file (default: projects.yml in repo)')
@click.option('--report', type=Path, default=None, help='Report configuration file (default: report.yml in repo)')
@click.option('--cache-dir', type=Path, default=None, help='Repository cache directory (default: repos-cache in repo)')
@click.option('--output-dir', type=Path, default=None, help='Output directory for report and graphics (default: out in repo)')
@click.option('--org-map', type=Path, required=True, help='Organization mapping file (SSV format)')
@click.option('--skip-sync', is_flag=True, help='Skip repository sync step')
def all(projects, report, cache_dir, output_dir, org_map, skip_sync):
    """Run complete pipeline: sync → extract → render → pdf. Requires: org-map file."""
    if projects is None:
        projects = get_default_path('projects.yml')
    if report is None:
        report = get_default_path('report.yml')
    if cache_dir is None:
        cache_dir = get_default_path('repos-cache')
    if output_dir is None:
        output_dir = get_default_path('out')

    # Step 1: Sync
    if not skip_sync:
        _sync_repos(projects, cache_dir)
    else:
        click.echo("Skipping repository sync...")

    # Step 2: Extract and aggregate
    metrics = _extract_metrics(projects, report, cache_dir, org_map, None)

    # Step 3: Render report
    _render_report(projects, metrics, output_dir)

    # Step 4: Generate PDF
    click.echo("Generating PDF...")
    pdf_path = output_dir / 'report.pdf'
    report_path = output_dir / 'report.md'
    try:
        pdf_module.generate_pdf(report_path, pdf_path)
        click.echo(f"PDF generated: {pdf_path}")
    except Exception as e:
        click.echo(f"Warning: PDF generation failed: {e}", err=True)


@cli.command()
@click.option('--projects', type=Path, default=None, help='Projects configuration file (default: projects.yml in repo)')
@click.option('--cache-dir', type=Path, default=None, help='Repository cache directory (default: repos-cache in repo)')
def sync(projects, cache_dir):
    """Sync all project repositories to local cache."""
    if projects is None:
        projects = get_default_path('projects.yml')
    if cache_dir is None:
        cache_dir = get_default_path('repos-cache')

    _sync_repos(projects, cache_dir)


@cli.command()
@click.option('--projects', type=Path, default=None, help='Projects configuration file (default: projects.yml in repo)')
@click.option('--report', type=Path, default=None, help='Report configuration file (default: report.yml in repo)')
@click.option('--cache-dir', type=Path, default=None, help='Repository cache directory (default: repos-cache in repo)')
@click.option('--org-map', type=Path, required=True, help='Organization mapping file (SSV format)')
@click.option('--output', type=Path, default=None, help='Output metrics JSON file')
def extract(projects, report, cache_dir, org_map, output):
    """Extract commits and aggregate metrics. Requires: synced repos, org-map file."""
    if projects is None:
        projects = get_default_path('projects.yml')
    if report is None:
        report = get_default_path('report.yml')
    if cache_dir is None:
        cache_dir = get_default_path('repos-cache')
    if output is None:
        output = get_default_path('out') / 'metrics.json'

    _extract_metrics(projects, report, cache_dir, org_map, output)


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

    click.echo(f"Loading metrics from {metrics}...")
    with open(metrics, 'r') as f:
        metrics_data = json.load(f)

    _render_report(projects, metrics_data, output_dir)


@cli.command()
@click.option('--input', type=Path, default='out/report.md', help='Input markdown report file')
@click.option('--output', type=Path, default='out/report.pdf', help='Output PDF file')
def pdf(input, output):
    """Generate PDF from markdown report. Requires: report.md."""
    click.echo(f"Generating PDF from {input}...")
    try:
        pdf_module.generate_pdf(input, output)
        click.echo(f"PDF generated: {output}")
    except Exception as e:
        click.echo(f"Error: PDF generation failed: {e}", err=True)


@cli.command()
@click.option('--projects', type=Path, default=None, help='Projects configuration file (default: projects.yml in repo)')
@click.option('--cache-dir', type=Path, default=None, help='Repository cache directory (default: repos-cache in repo)')
@click.option('--org-map', type=Path, required=True, help='Organization mapping file (SSV format)')
def update_org_map(projects, cache_dir, org_map):
    """Update organization mapping file with new committers and projects."""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from collections import defaultdict
    
    if projects is None:
        projects = get_default_path('projects.yml')
    if cache_dir is None:
        cache_dir = get_default_path('repos-cache')
    
    click.echo("Loading configuration...")
    cfg = config.load_config(projects, get_default_path('report.yml'))
    
    click.echo(f"Loading existing organization mapping from {org_map}...")
    existing_mapping = attribution.load_org_mapping(org_map)
    click.echo(f"  Found {len(existing_mapping)} existing mappings")
    
    # Extract all commits to find email addresses and their projects
    click.echo("Extracting committer information from repositories...")
    email_projects = defaultdict(set)
    
    # Use a wide date range to capture all historical commits
    start_date = datetime.now().date() - relativedelta(years=10)
    end_date = datetime.now().date()
    
    for project in cfg.projects:
        project_id = project['id']
        click.echo(f"  Processing {project['name']}...")
        
        for repo_url in project['repos']:
            repo_name = git_ops.sanitize_repo_name(repo_url)
            repo_path = cache_dir / f"{repo_name}.git"
            
            if not repo_path.exists():
                click.echo(f"    Warning: {repo_path} not found, skipping", err=True)
                continue
            
            commits = git_ops.extract_commits(repo_path, start_date, end_date)
            for commit in commits:
                email = commit['email'].lower().strip()
                email_projects[email].add(project_id)
    
    click.echo(f"\nFound {len(email_projects)} unique email addresses across all projects")
    
    # Read existing file to preserve format
    with open(org_map, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse all entries (existing and new)
    all_entries = {}
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split(';')
        if len(parts) != 3:
            continue
        
        committer, projects_str, org = parts
        
        # Extract email
        if '<' in committer and '>' in committer:
            email = committer.split('<')[1].split('>')[0]
        else:
            email = committer
        
        email = email.lower().strip()
        
        # Update projects list if email is in our extracted data
        if email in email_projects:
            new_projects = sorted(email_projects[email])
            all_entries[email] = (committer, ','.join(new_projects), org)
        else:
            all_entries[email] = (committer, projects_str, org)
    
    # Add new entries
    new_emails = set(email_projects.keys()) - set(all_entries.keys())
    if new_emails:
        click.echo(f"\nAdding {len(new_emails)} new email addresses:")
        for email in new_emails:
            projects_list = sorted(email_projects[email])
            all_entries[email] = (email, ','.join(projects_list), 'Unknown')
            click.echo(f"  + {email} ({', '.join(projects_list)})")
    
    # Write sorted entries
    with open(org_map, 'w', encoding='utf-8') as f:
        f.write(lines[0])  # Header
        for email in sorted(all_entries.keys()):
            committer, projects, org = all_entries[email]
            f.write(f"{committer};{projects};{org}\n")
    
    click.echo(f"\nOrganization mapping file updated: {org_map}")
    click.echo(f"  Total entries: {len(all_entries)}")
    click.echo(f"  New entries: {len(new_emails)}")
    click.echo(f"  Updated entries: {len(set(all_entries.keys()) & set(email_projects.keys()) - new_emails)}")


if __name__ == '__main__':
    cli()
