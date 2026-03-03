"""Graphics generation for reports."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict
import numpy as np


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


def generate_activity_heatmap(metrics: Dict, projects: list, output_path: Path, months: int = 12):
    """Generate heatmap showing commits per project per month.
    
    Args:
        metrics: Aggregated metrics
        projects: List of projects
        output_path: Path to save the heatmap
        months: Number of months to display (default: 12)
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    # Collect all months across all projects
    all_months = set()
    for project_data in metrics['projects'].values():
        all_months.update(project_data.get('monthly', {}).keys())
    
    if not all_months:
        return
    
    # Get the date range - use only the last N months of data
    months_in_data = sorted(all_months)
    last_month = datetime.strptime(months_in_data[-1], '%Y-%m')
    
    # Start N-1 months before the last month
    start_month = last_month - relativedelta(months=months-1)
    
    # Generate exactly N months
    month_list = []
    current = start_month
    for _ in range(months):
        month_list.append(current.strftime('%Y-%m'))
        current += relativedelta(months=1)
    
    # Build data matrix: projects x months
    project_names = []
    data_matrix = []
    
    for project in projects:
        project_id = project['id']
        project_data = metrics['projects'].get(project_id, {})
        
        if project_data.get('commits', 0) > 0:
            project_names.append(project['name'])
            row = [project_data.get('monthly', {}).get(month, 0) for month in month_list]
            data_matrix.append(row)
    
    if not project_names:
        return
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(max(10, len(month_list) * 1.2), max(6, len(project_names) * 0.8)))
    
    # Convert to numpy array for plotting
    data = np.array(data_matrix)
    
    # Create heatmap with red color scheme
    im = ax.imshow(data, cmap='Reds', aspect='auto')
    
    # Set ticks
    ax.set_xticks(np.arange(len(month_list)))
    ax.set_yticks(np.arange(len(project_names)))
    ax.set_xticklabels(month_list)
    ax.set_yticklabels(project_names)
    
    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Commits', rotation=270, labelpad=15)
    
    # Add text annotations
    for i in range(len(project_names)):
        for j in range(len(month_list)):
            value = data[i, j]
            if value > 0:
                text = ax.text(j, i, int(value), ha="center", va="center", 
                             color="white" if value > data.max() * 0.5 else "black", 
                             fontsize=8)
    
    ax.set_title(f'Activity Trend: Commits per Project per Month ({months}-month view)')
    ax.set_xlabel('Month')
    ax.set_ylabel('Project')
    
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


def generate_project_monthly_chart(project_id: str, project_name: str, metrics: Dict, output_path: Path, months: int = 12):
    """Generate monthly activity chart for a single project with 12-month view."""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    project_data = metrics['projects'].get(project_id, {})
    monthly = project_data.get('monthly', {})
    
    if not monthly:
        return
    
    # Get last N months
    months_in_data = sorted(monthly.keys())
    last_month = datetime.strptime(months_in_data[-1], '%Y-%m')
    start_month = last_month - relativedelta(months=months-1)
    
    # Generate month list
    month_list = []
    current = start_month
    for _ in range(months):
        month_list.append(current.strftime('%Y-%m'))
        current += relativedelta(months=1)
    
    counts = [monthly.get(m, 0) for m in month_list]
    
    plt.figure(figsize=(10, 5))
    plt.bar(month_list, counts, color='#0066cc')
    plt.xlabel('Month')
    plt.ylabel('Commits')
    plt.title(f'{project_name} - Monthly Activity ({months}-month view)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def generate_project_org_stacked_chart(project_id: str, project_name: str, metrics: Dict, output_path: Path, months: int = 12):
    """Generate stacked bar chart showing monthly activity by organization for a project."""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    project_data = metrics['projects'].get(project_id, {})
    monthly = project_data.get('monthly', {})
    monthly_by_org = project_data.get('monthly_by_org', {})
    
    # Get the last month from ALL projects to ensure consistent range
    all_months = set()
    for proj_data in metrics['projects'].values():
        all_months.update(proj_data.get('monthly', {}).keys())
    
    if not all_months:
        return
    
    # Use the latest month across all projects
    months_in_data = sorted(all_months)
    last_month = datetime.strptime(months_in_data[-1], '%Y-%m')
    start_month = last_month - relativedelta(months=months-1)
    
    # Generate month list (same for all projects)
    month_list = []
    current = start_month
    for _ in range(months):
        month_list.append(current.strftime('%Y-%m'))
        current += relativedelta(months=1)
    
    # Get all organizations for this project
    all_orgs = set()
    for month_orgs in monthly_by_org.values():
        all_orgs.update(month_orgs.keys())
    
    if not all_orgs:
        # No org data, just show total
        counts = [monthly.get(m, 0) for m in month_list]
        plt.figure(figsize=(10, 5))
        plt.bar(month_list, counts, color='#0066cc')
        plt.xlabel('Month')
        plt.ylabel('Commits')
        plt.title(f'{project_name} - Activity Trend')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        return
    
    # Build stacked data
    org_list = sorted(all_orgs)
    data_by_org = {}
    for org in org_list:
        data_by_org[org] = [monthly_by_org.get(m, {}).get(org, 0) for m in month_list]
    
    # Create stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Use different colors for each organization
    colors = plt.cm.Set3(np.linspace(0, 1, len(org_list)))
    
    bottom = np.zeros(len(month_list))
    for i, org in enumerate(org_list):
        ax.bar(month_list, data_by_org[org], bottom=bottom, label=org, color=colors[i])
        bottom += np.array(data_by_org[org])
    
    ax.set_xlabel('Month')
    ax.set_ylabel('Commits')
    ax.set_title(f'{project_name} - Activity Trend by Organization')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def generate_org_pie_chart(metrics: Dict, output_path: Path, quarter_only: bool = False):
    """Generate organization distribution pie chart.
    
    Args:
        metrics: Aggregated metrics
        output_path: Path to save the chart
        quarter_only: If True, use quarter_org_stats instead of orgs
    """
    if quarter_only:
        orgs = metrics.get('quarter_org_stats', {})
        title = 'Commits by Organization (This Quarter)'
    else:
        orgs = metrics.get('orgs', {})
        title = 'Commits by Organization'
    
    if not orgs:
        return
    
    labels = list(orgs.keys())
    sizes = list(orgs.values())
    
    plt.figure(figsize=(4, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
    plt.title(title, fontsize=11, pad=20)
    plt.axis('equal')
    plt.tight_layout(pad=1.5)
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
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
