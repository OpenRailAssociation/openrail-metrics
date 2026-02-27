"""Graphics generation for reports."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict


def generate_monthly_chart(metrics: Dict, output_path: Path):
    """Generate monthly commit activity chart."""
    monthly_totals = {}
    
    for project_id, project_data in metrics['projects'].items():
        for month, count in project_data.get('monthly', {}).items():
            monthly_totals[month] = monthly_totals.get(month, 0) + count
    
    if not monthly_totals:
        return
    
    months = sorted(monthly_totals.keys())
    counts = [monthly_totals[m] for m in months]
    
    plt.figure(figsize=(10, 6))
    plt.bar(months, counts, color='#0066cc')
    plt.xlabel('Month')
    plt.ylabel('Commits')
    plt.title('Monthly Commit Activity')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def generate_project_chart(metrics: Dict, projects: list, output_path: Path):
    """Generate per-project commit distribution chart."""
    project_names = []
    commit_counts = []
    
    for project in projects:
        project_id = project['id']
        project_data = metrics['projects'].get(project_id, {})
        commits = project_data.get('commits', 0)
        
        if commits > 0:
            project_names.append(project['name'])
            commit_counts.append(commits)
    
    if not project_names:
        return
    
    plt.figure(figsize=(10, 6))
    plt.barh(project_names, commit_counts, color='#0066cc')
    plt.xlabel('Commits')
    plt.title('Commits by Project')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def generate_project_monthly_chart(project_id: str, project_name: str, metrics: Dict, output_path: Path):
    """Generate monthly activity chart for a single project."""
    project_data = metrics['projects'].get(project_id, {})
    monthly = project_data.get('monthly', {})
    
    if not monthly:
        return
    
    months = sorted(monthly.keys())
    counts = [monthly[m] for m in months]
    
    plt.figure(figsize=(8, 5))
    plt.bar(months, counts, color='#0066cc')
    plt.xlabel('Month')
    plt.ylabel('Commits')
    plt.title(f'{project_name} - Monthly Activity')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def generate_org_pie_chart(metrics: Dict, output_path: Path):
    """Generate organization distribution pie chart."""
    orgs = metrics.get('orgs', {})
    
    if not orgs:
        return
    
    labels = list(orgs.keys())
    sizes = list(orgs.values())
    
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title('Commits by Organization')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def generate_project_org_pie_chart(project_id: str, project_name: str, project_orgs: Dict, output_path: Path):
    """Generate organization distribution pie chart for a single project."""
    if not project_orgs:
        return
    
    labels = list(project_orgs.keys())
    sizes = list(project_orgs.values())
    
    plt.figure(figsize=(7, 7))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title(f'{project_name} - Commits by Organization')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
