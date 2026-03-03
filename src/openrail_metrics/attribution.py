"""Organization attribution."""

from pathlib import Path
from typing import Dict, Optional, Tuple
from collections import defaultdict


def load_org_mapping(path: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Load organization mapping from SSV file.

    Returns tuple: (email_to_canonical, canonical_to_org)
    """
    email_to_canonical = {}
    canonical_to_org = defaultdict(set)

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        parts = line.split(';')
        if len(parts) == 3:
            # Old format without canonical column
            committer, projects_str, org = parts
            canonical = None
        elif len(parts) == 4:
            # Check if it's old format (Committer;Projects;Organization;Canonical)
            # or new format (Committer;Projects;Canonical;Organization)
            committer, projects_str, field3, field4 = parts
            # Heuristic: if field3 looks like an email, it's canonical (new format)
            if '@' in field3 or field3.lower() in ['unknown', 'bot']:
                # New format: Committer;Projects;Canonical;Organization
                canonical = field3.strip().lower() if field3 else None
                org = field4.strip()
            else:
                # Old format: Committer;Projects;Organization;Canonical
                org = field3.strip()
                canonical = field4.strip().lower() if field4 else None
        else:
            continue

        # Extract email from "Name <email>" format
        if '<' in committer and '>' in committer:
            email = committer.split('<')[1].split('>')[0]
        else:
            email = committer

        email = email.lower().strip()
        org = org.strip()
        
        # If no canonical specified, email is its own canonical
        if not canonical:
            canonical = email
        
        email_to_canonical[email] = canonical
        canonical_to_org[canonical].add(org)

    # Validate: each canonical should have exactly one org
    conflicts = {}
    for canonical, orgs in canonical_to_org.items():
        if len(orgs) > 1:
            conflicts[canonical] = orgs
    
    if conflicts:
        error_msg = "Organization conflicts detected:\n"
        for canonical, orgs in sorted(conflicts.items()):
            error_msg += f"  {canonical}: {', '.join(sorted(orgs))}\n"
        raise ValueError(error_msg)
    
    # Convert sets to single values
    canonical_to_org_final = {k: list(v)[0] for k, v in canonical_to_org.items()}
    
    return email_to_canonical, canonical_to_org_final


def get_organization(email: str, project_id: str, org_mapping: Optional[Tuple] = None) -> str:
    """Get organization for an email."""
    if not org_mapping:
        return "Unknown"

    email_to_canonical, canonical_to_org = org_mapping
    email = email.lower().strip()

    # Resolve to canonical
    canonical = email_to_canonical.get(email, email)
    
    # Look up org by canonical
    return canonical_to_org.get(canonical, "Unknown")
