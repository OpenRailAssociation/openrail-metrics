"""Markdown report rendering."""

from typing import Dict, List
from pathlib import Path


def load_template(template_name: str) -> str:
    """Load a template file."""
    template_path = Path(__file__).parent.parent.parent / 'templates' / template_name
    return template_path.read_text()


def render_report(config, metrics: Dict, projects: List[Dict], output_path: Path, graphics_dir: Path = None):
    """Generate Markdown report using template."""
    
    report = config.report
    template = load_template('report.md.template')
    
    # Prepare quarter org chart
    quarter_org_chart = ""
    if graphics_dir:
        quarter_org_chart_path = graphics_dir / 'quarter_org_distribution.png'
        if quarter_org_chart_path.exists():
            quarter_org_chart = '<img src="graphics/quarter_org_distribution.png" class="small-chart" alt="Commits by Organization (This Quarter)" />\n'
    
    # Prepare quarter orgs list (exclude Bot from display)
    quarter_orgs_list = ""
    if metrics.get('quarter_org_stats'):
        for org in sorted(metrics['quarter_org_stats'].keys()):
            if org != 'Bot':
                quarter_orgs_list += f"- {org}\n"
    
    # Prepare activity heatmap
    activity_heatmap = ""
    if graphics_dir:
        heatmap_path = graphics_dir / 'activity_heatmap.png'
        if heatmap_path.exists():
            activity_heatmap = "![Activity Trend: Commits per Project per Month](graphics/activity_heatmap.png)\n"
    
    # Render projects by stage
    stages = {'qualified': [], 'onboarded': [], 'administrative': []}
    for project in projects:
        stage = project['stage']
        if stage in stages:
            stages[stage].append(project)
    
    qualified_projects = ""
    for project in stages['qualified']:
        qualified_projects += render_project(project, metrics, graphics_dir)
    
    onboarded_projects = ""
    for project in stages['onboarded']:
        onboarded_projects += render_project(project, metrics, graphics_dir)
    
    administrative_projects = ""
    for project in stages['administrative']:
        administrative_projects += render_project(project, metrics, graphics_dir)
    
    # Fill template
    content = template.format(
        quarter=report['quarter'],
        from_date=report['from'],
        to_date=report['to'],
        issue_date=report['issue_date'],
        quarter_contributors=metrics.get('quarter_contributors', 0),
        quarter_commits=metrics.get('quarter_commits', 0),
        quarter_orgs=metrics.get('quarter_orgs', 0),
        quarter_org_chart=quarter_org_chart,
        quarter_orgs_list=quarter_orgs_list,
        total_contributors=metrics['total_contributors'],
        total_commits=metrics['total_commits'],
        total_orgs=metrics.get('total_orgs', 0),
        activity_heatmap=activity_heatmap,
        qualified_projects=qualified_projects,
        onboarded_projects=onboarded_projects,
        administrative_projects=administrative_projects
    )
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)


def render_project(project: Dict, metrics: Dict, graphics_dir: Path = None) -> str:
    """Render a single project section using template."""
    template = load_template('project.md.template')
    
    project_id = project['id']
    project_metrics = metrics['projects'].get(project_id, {
        'commits': 0,
        'contributors': 0,
        'orgs': 0,
    })
    
    # Get project description
    project_description = project.get('description', '')
    
    # Prepare repositories list with clickable links
    repositories = ""
    for repo in project['repos']:
        repositories += f"- [{repo}]({repo})\n"
    
    # Prepare trend chart
    trend_chart = ""
    if project_metrics['commits'] > 0 and graphics_dir:
        trend_chart_path = graphics_dir / f'{project_id}_trend.png'
        if trend_chart_path.exists():
            trend_chart = f"![{project['name']} - 12-Month Activity Trend by Organization](graphics/{project_id}_trend.png)\n"
    
    return template.format(
        project_name=project['name'],
        project_description=project_description,
        commits=project_metrics['commits'],
        contributors=project_metrics['contributors'],
        orgs=project_metrics.get('orgs', 0),
        repositories=repositories,
        trend_chart=trend_chart
    )
