"""Tests for config module."""

from pathlib import Path
from openrail_metrics.config import load_config
import tempfile
import yaml


def test_load_config():
    projects_data = {
        'projects': [
            {'id': 'test-proj', 'name': 'Test Project', 'stage': 'qualified', 'repos': ['https://github.com/test/repo.git']}
        ]
    }
    
    report_data = {
        'report': {
            'title': 'Test Report',
            'quarter': '2025Q4',
            'from': '2025-12-01',
            'to': '2026-02-28',
            'issue_date': '2026-03-15'
        }
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        projects_path = Path(tmpdir) / 'projects.yml'
        report_path = Path(tmpdir) / 'report.yml'
        
        projects_path.write_text(yaml.dump(projects_data))
        report_path.write_text(yaml.dump(report_data))
        
        config = load_config(projects_path, report_path)
        
        assert len(config.projects) == 1
        assert config.projects[0]['id'] == 'test-proj'
        assert config.quarter == '2025Q4'
        assert str(config.from_date) == '2025-12-01'
        assert str(config.to_date) == '2026-02-28'
