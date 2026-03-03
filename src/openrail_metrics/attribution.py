"""Organization attribution."""

from pathlib import Path
from typing import Dict, Optional


def load_org_mapping(path: Path) -> Dict[str, Dict[str, str]]:
    """Load organization mapping from SSV file.

    Returns dict: {normalized_email: {project_id: org_name}}
    """
    mapping = {}

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        parts = line.split(';')
        if len(parts) != 3:
            continue

        committer, projects_str, org = parts

        # Extract email from "Name <email>" format
        if '<' in committer and '>' in committer:
            email = committer.split('<')[1].split('>')[0]
        else:
            email = committer

        email = email.lower().strip()

        # Parse project list
        project_ids = [p.strip() for p in projects_str.split(',')]

        # Store mapping per project
        if email not in mapping:
            mapping[email] = {}

        for project_id in project_ids:
            mapping[email][project_id] = org.strip()

    return mapping


def get_organization(email: str, project_id: str, org_mapping: Optional[Dict] = None) -> str:
    """Get organization for an email and project."""
    if not org_mapping:
        return "Unknown"

    email = email.lower().strip()

    if email in org_mapping and project_id in org_mapping[email]:
        return org_mapping[email][project_id]

    return "Unknown"
