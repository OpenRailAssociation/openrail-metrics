"""Markdown report rendering."""

from typing import Dict, List
from pathlib import Path


def render_report(config, metrics: Dict, projects: List[Dict], output_path: Path, graphics_dir: Path = None):
    """Generate Markdown report with three sections: Quarterly Snapshot, Progress Data, Per-Project Details."""
    
    report = config.report
    
    md = f"""# The State of OpenRail

**Quarterly Metrics Report - {report['quarter']}**

Scope: {report['from']} to {report['to']}  
Issue date: {report['issue_date']}

---

## 1. Quarterly Snapshot

This section shows metrics for the reporting quarter only.

**Summary Statistics ({report['from']} to {report['to']}):**

- Active committers this quarter: **{metrics.get('quarter_committers', 0)}**
- Human commits this quarter: **{metrics.get('quarter_commits', 0)}**
- Contributing organizations this quarter: **{metrics.get('quarter_orgs', 0)}**

"""
    
    # Add quarter org chart if available
    if graphics_dir:
        quarter_org_chart = graphics_dir / 'quarter_org_distribution.png'
        if quarter_org_chart.exists():
            md += f'<img src="graphics/quarter_org_distribution.png" class="small-chart" alt="Commits by Organization (This Quarter)" />\n\n'
    
    md += """**Code-committing Organizations:**

"""
    
    # List organizations
    if metrics.get('quarter_org_stats'):
        for org in sorted(metrics['quarter_org_stats'].keys()):
            md += f"- {org}\n"
        md += "\n*Some freelancers and individuals have contributed code too, but are not listed as organizations.*\n\n"
    
    md += """---

## 2. Progress Data (12-Month View)

This section shows activity trends over the past 12 months for context.

**Overall Activity:**

- Total committers (12 months): **{total_committers}**
- Total commits (12 months): **{total_commits}**
- Total organizations (12 months): **{total_orgs}**

""".format(
        total_committers=metrics['total_committers'],
        total_commits=metrics['total_commits'],
        total_orgs=metrics.get('total_orgs', 0)
    )
    
    # Add 12-month graphics if available
    if graphics_dir:
        heatmap_chart = graphics_dir / 'activity_heatmap.png'
        
        if heatmap_chart.exists():
            md += f"![Activity Trend: Commits per Project per Month](graphics/activity_heatmap.png)\n\n"
    
    md += "---\n\n## 3. Project Details\n\n"
    md += "Activity trends and organization contributions for each project over the past 12 months.\n\n"
    
    # Group projects by stage
    stages = {
        'qualified': [],
        'onboarded': []
    }
    
    for project in projects:
        stage = project['stage']
        if stage in stages:
            stages[stage].append(project)
    
    # Stage 2 - Qualified
    if stages['qualified']:
        md += "### Stage 2 - Qualified\n\n"
        for project in stages['qualified']:
            md += render_project(project, metrics, graphics_dir)
    
    # Stage 1 - Onboarded
    if stages['onboarded']:
        md += "### Stage 1 - Onboarded\n\n"
        for project in stages['onboarded']:
            md += render_project(project, metrics, graphics_dir)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md)


def render_project(project: Dict, metrics: Dict, graphics_dir: Path = None) -> str:
    """Render a single project section with 12-month activity trend."""
    project_id = project['id']
    project_metrics = metrics['projects'].get(project_id, {
        'commits': 0,
        'committers': 0,
        'orgs': 0,
        'monthly': {}
    })
    
    md = f"""#### {project['name']}

**12-Month Statistics:**

- Total commits: **{project_metrics['commits']}**
- Total committers: **{project_metrics['committers']}**
- Contributing organizations: **{project_metrics.get('orgs', 0)}**

**Repositories:**
"""
    
    for repo in project['repos']:
        md += f"- {repo}\n"
    
    # Add per-project charts if they exist
    if project_metrics['commits'] > 0 and graphics_dir:
        trend_chart = graphics_dir / f'{project_id}_trend.png'
        
        if trend_chart.exists():
            md += f"\n![{project['name']} - 12-Month Activity Trend by Organization](graphics/{project_id}_trend.png)\n"
    
    md += "\n---\n\n"
    
    return md
