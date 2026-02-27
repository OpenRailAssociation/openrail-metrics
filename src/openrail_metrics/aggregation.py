"""Metrics aggregation."""

from typing import List, Dict
from collections import defaultdict
from datetime import datetime


def aggregate_metrics(commit_events: List[Dict]) -> Dict:
    """Aggregate commit events into metrics."""
    
    # Overall stats
    total_commits = len(commit_events)
    unique_committers = set(e['committer_id'] for e in commit_events)
    
    # Per-project stats
    project_stats = defaultdict(lambda: {
        'commits': 0,
        'committers': set(),
        'monthly': defaultdict(int)
    })
    
    for event in commit_events:
        project_id = event['project_id']
        project_stats[project_id]['commits'] += 1
        project_stats[project_id]['committers'].add(event['committer_id'])
        
        # Monthly breakdown
        month = datetime.fromisoformat(event['date'].replace('Z', '+00:00')).strftime('%Y-%m')
        project_stats[project_id]['monthly'][month] += 1
    
    # Convert sets to counts
    for project_id in project_stats:
        project_stats[project_id]['committers'] = len(project_stats[project_id]['committers'])
        project_stats[project_id]['monthly'] = dict(project_stats[project_id]['monthly'])
    
    return {
        'total_commits': total_commits,
        'total_committers': len(unique_committers),
        'projects': dict(project_stats)
    }
