"""Markdown report rendering."""

from typing import Dict, List
from pathlib import Path


def render_report(config, metrics: Dict, projects: List[Dict], output_path: Path):
    """Generate Markdown report."""
    
    report = config.report
    
    md = f"""# OpenRail Metrics Report

**{report['quarter']}**

Scope: {report['from']} to {report['to']}  
Issue date: {report['issue_date']}

---

## OpenRail-Wide Project Statistics

**Summary Statistics:**

- Total active committers: **{metrics['total_committers']}**
- Number of human commits across all projects: **{metrics['total_commits']}**

---

## Project Overview

"""
    
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
            md += render_project(project, metrics)
    
    # Stage 1 - Onboarded
    if stages['onboarded']:
        md += "### Stage 1 - Onboarded\n\n"
        for project in stages['onboarded']:
            md += render_project(project, metrics)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md)


def render_project(project: Dict, metrics: Dict) -> str:
    """Render a single project section."""
    project_id = project['id']
    project_metrics = metrics['projects'].get(project_id, {
        'commits': 0,
        'committers': 0,
        'monthly': {}
    })
    
    md = f"""#### {project['name']}

**Commits:** {project_metrics['commits']}  
**Committers:** {project_metrics['committers']}

**Repositories:**
"""
    
    for repo in project['repos']:
        md += f"- {repo}\n"
    
    # Monthly breakdown
    if project_metrics['monthly']:
        md += "\n**Monthly Activity:**\n\n"
        for month in sorted(project_metrics['monthly'].keys()):
            count = project_metrics['monthly'][month]
            md += f"- {month}: {count} commits\n"
    
    md += "\n---\n\n"
    
    return md
