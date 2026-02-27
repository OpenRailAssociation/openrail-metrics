"""Metrics aggregation."""

from typing import List, Dict
from collections import defaultdict
from datetime import datetime


def aggregate_metrics(commit_events: List[Dict], quarter_from_date=None, quarter_to_date=None) -> Dict:
    """Aggregate commit events into metrics.
    
    Args:
        commit_events: All commit events (may span longer than quarter)
        quarter_from_date: Start of the reporting quarter (for snapshot metrics)
        quarter_to_date: End of the reporting quarter (for snapshot metrics)
    """
    
    # Overall stats (all data)
    total_commits = len(commit_events)
    unique_committers = set(e['committer_id'] for e in commit_events)
    unique_orgs = set(e.get('org', 'Unknown') for e in commit_events if e.get('org') != 'Unknown')
    
    # Quarter-only stats (snapshot)
    quarter_commits = []
    if quarter_from_date and quarter_to_date:
        quarter_commits = [
            e for e in commit_events 
            if quarter_from_date <= datetime.fromisoformat(e['date'].replace('Z', '+00:00')).date() <= quarter_to_date
        ]
    
    quarter_committers = set(e['committer_id'] for e in quarter_commits)
    quarter_orgs = set(e.get('org', 'Unknown') for e in quarter_commits if e.get('org') != 'Unknown')
    
    # Quarter-only org stats
    quarter_org_stats = defaultdict(int)
    for event in quarter_commits:
        org = event.get('org', 'Unknown')
        if org != 'Unknown':
            quarter_org_stats[org] += 1
    
    # Per-project stats (all data)
    project_stats = defaultdict(lambda: {
        'commits': 0,
        'committers': set(),
        'orgs': set(),
        'org_commits': defaultdict(int),
        'monthly': defaultdict(int),
        'monthly_by_org': defaultdict(lambda: defaultdict(int))
    })
    
    # Per-org stats (all data)
    org_stats = defaultdict(int)
    
    for event in commit_events:
        project_id = event['project_id']
        org = event.get('org', 'Unknown')
        
        project_stats[project_id]['commits'] += 1
        project_stats[project_id]['committers'].add(event['committer_id'])
        
        if org != 'Unknown':
            project_stats[project_id]['orgs'].add(org)
            project_stats[project_id]['org_commits'][org] += 1
            org_stats[org] += 1
        
        # Monthly breakdown
        month = datetime.fromisoformat(event['date'].replace('Z', '+00:00')).strftime('%Y-%m')
        project_stats[project_id]['monthly'][month] += 1
        
        # Monthly by org
        if org != 'Unknown':
            project_stats[project_id]['monthly_by_org'][month][org] += 1
    
    # Convert sets to counts and nested dicts to regular dicts
    for project_id in project_stats:
        project_stats[project_id]['committers'] = len(project_stats[project_id]['committers'])
        project_stats[project_id]['orgs'] = len(project_stats[project_id]['orgs'])
        project_stats[project_id]['org_commits'] = dict(project_stats[project_id]['org_commits'])
        project_stats[project_id]['monthly'] = dict(project_stats[project_id]['monthly'])
        
        # Convert monthly_by_org nested defaultdict to regular dict
        monthly_by_org = {}
        for month, orgs in project_stats[project_id]['monthly_by_org'].items():
            monthly_by_org[month] = dict(orgs)
        project_stats[project_id]['monthly_by_org'] = monthly_by_org
    
    return {
        'total_commits': total_commits,
        'total_committers': len(unique_committers),
        'total_orgs': len(unique_orgs),
        'quarter_commits': len(quarter_commits),
        'quarter_committers': len(quarter_committers),
        'quarter_orgs': len(quarter_orgs),
        'quarter_org_stats': dict(quarter_org_stats),
        'projects': dict(project_stats),
        'orgs': dict(org_stats)
    }
