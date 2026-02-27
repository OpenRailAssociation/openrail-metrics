"""Git repository operations."""

import subprocess
from pathlib import Path
from typing import List, Dict
from datetime import date
import re


def sanitize_repo_name(url: str) -> str:
    """Convert repo URL to safe directory name."""
    return re.sub(r'[^\w\-]', '_', url.replace('https://', '').replace('.git', ''))


def sync_repo(url: str, cache_dir: Path) -> Path:
    """Clone or update a repository as bare mirror."""
    repo_name = sanitize_repo_name(url)
    repo_path = cache_dir / f"{repo_name}.git"
    
    if repo_path.exists():
        # Update existing mirror
        subprocess.run(['git', '-C', str(repo_path), 'fetch', '--prune'], 
                      check=True, capture_output=True)
    else:
        # Clone as bare mirror
        cache_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', '--mirror', url, str(repo_path)],
                      check=True, capture_output=True)
    
    return repo_path


def extract_commits(repo_path: Path, from_date: date, to_date: date) -> List[Dict]:
    """Extract commit data from repository."""
    # Format: hash|author_email|commit_date|parent_count
    format_str = '%H|%ae|%cI|%P'
    
    result = subprocess.run([
        'git', '-C', str(repo_path), 'log',
        f'--since={from_date.isoformat()}',
        f'--until={to_date.isoformat()}',
        f'--pretty=format:{format_str}',
        '--all'
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
            'email': email.lower().strip(),
            'date': commit_date,
            'is_merge': parent_count > 1
        })
    
    return commits
