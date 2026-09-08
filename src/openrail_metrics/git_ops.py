"""Git repository operations."""

import subprocess
from pathlib import Path
from typing import List, Dict
from datetime import date
import re

from .identity import normalize_email


def sanitize_repo_name(url: str) -> str:
    """Convert repo URL to safe directory name."""
    return re.sub(r'[^\w\-]', '_', url.replace('https://', '').replace('.git', ''))


def sync_repo(url: str, cache_dir: Path) -> Path:
    """Clone or update a repository as bare mirror."""
    repo_name = sanitize_repo_name(url)
    repo_path = cache_dir / f"{repo_name}.git"

    if repo_path.exists():
        # Update existing mirror
        try:
            subprocess.run(['git', '-C', str(repo_path), 'fetch', '--prune'],
                          check=True, capture_output=True, timeout=30)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            # Network issue or timeout - use cached version
            print(f"    Warning: Could not update repo (using cached version): {e}")
    else:
        # Clone as bare mirror
        cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(['git', 'clone', '--mirror', url, str(repo_path)],
                          check=True, capture_output=True, timeout=60)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"    Error: Could not clone repo: {e}")
            raise

    return repo_path

    return repo_path


def extract_commits(repo_path: Path, from_date: date, to_date: date, branches: List[str] = None) -> List[Dict]:
    """Extract commit data from repository.
    
    Args:
        repo_path: Path to git repository
        from_date: Start date for commits
        to_date: End date for commits
        branches: List of branch names to include (default: all branches)
    """
    # Format: hash|author_email|commit_date|parent_count
    format_str = '%H|%ae|%cI|%P'

    # Build branch arguments
    if branches:
        branch_args = branches
    else:
        branch_args = ['--branches']

    result = subprocess.run([
        'git', '-C', str(repo_path), 'log',
        f'--since={from_date.isoformat()}',
        f'--until={to_date.isoformat()}',
        f'--pretty=format:{format_str}',
        *branch_args
    ], capture_output=True, text=True, check=True)

    commits = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue

        parts = line.split('|')
        if len(parts) != 4:
            continue

        commit_hash, email, commit_date, parents = parts
        parent_count = len(parents.split()) if parents else 0

        commits.append({
            'hash': commit_hash,
            'email': normalize_email(email),
            'date': commit_date,
            'is_merge': parent_count > 1
        })

    return commits
