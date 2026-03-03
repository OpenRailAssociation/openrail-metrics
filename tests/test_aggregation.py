"""Tests for aggregation module."""

from openrail_metrics.aggregation import aggregate_metrics


def test_aggregate_metrics_basic():
    events = [
        {'project_id': 'proj1', 'committer_id': 'abc123', 'date': '2025-12-15T10:00:00Z'},
        {'project_id': 'proj1', 'committer_id': 'def456', 'date': '2025-12-20T10:00:00Z'},
        {'project_id': 'proj2', 'committer_id': 'abc123', 'date': '2026-01-10T10:00:00Z'},
    ]
    
    metrics = aggregate_metrics(events)
    
    assert metrics['total_commits'] == 3
    assert metrics['total_contributors'] == 2
    assert metrics['projects']['proj1']['commits'] == 2
    assert metrics['projects']['proj1']['contributors'] == 2
    assert metrics['projects']['proj2']['commits'] == 1
    assert metrics['projects']['proj2']['contributors'] == 1


def test_aggregate_metrics_monthly():
    events = [
        {'project_id': 'proj1', 'committer_id': 'abc123', 'date': '2025-12-15T10:00:00Z'},
        {'project_id': 'proj1', 'committer_id': 'abc123', 'date': '2025-12-20T10:00:00Z'},
        {'project_id': 'proj1', 'committer_id': 'abc123', 'date': '2026-01-10T10:00:00Z'},
    ]
    
    metrics = aggregate_metrics(events)
    
    assert metrics['projects']['proj1']['monthly']['2025-12'] == 2
    assert metrics['projects']['proj1']['monthly']['2026-01'] == 1


def test_aggregate_metrics_empty():
    metrics = aggregate_metrics([])
    
    assert metrics['total_commits'] == 0
    assert metrics['total_contributors'] == 0
    assert metrics['projects'] == {}
