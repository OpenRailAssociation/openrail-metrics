"""Configuration loading and validation."""

import yaml
from pathlib import Path
from datetime import date
from typing import List, Dict, Any


class Config:
    """Configuration container."""
    
    def __init__(self, projects: List[Dict], report: Dict):
        self.projects = projects
        self.report = report
    
    @property
    def from_date(self) -> date:
        return self.report['from']
    
    @property
    def to_date(self) -> date:
        return self.report['to']
    
    @property
    def quarter(self) -> str:
        return self.report['quarter']


def load_projects(path: Path) -> List[Dict[str, Any]]:
    """Load projects configuration."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data['projects']


def load_report(path: Path) -> Dict[str, Any]:
    """Load report configuration."""
    with open(path) as f:
        return yaml.safe_load(f)['report']


def load_config(projects_path: Path, report_path: Path) -> Config:
    """Load complete configuration."""
    projects = load_projects(projects_path)
    report = load_report(report_path)
    return Config(projects, report)
