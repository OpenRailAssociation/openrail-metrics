"""Find potential duplicate identities in committer mapping."""

import re
from collections import defaultdict


def parse_email(committer_field):
    """Extract email from 'Name <email>' or just 'email' format."""
    match = re.search(r'<([^>]+)>', committer_field)
    if match:
        return match.group(1).lower().strip()
    return committer_field.lower().strip()


def parse_name(committer_field):
    """Extract name from 'Name <email>' format."""
    match = re.match(r'^(.+?)\s*<', committer_field)
    if match:
        return match.group(1).strip()
    return None


def normalize_name(name):
    """Normalize name for comparison."""
    if not name:
        return None
    normalized = re.sub(r'[^\w\s]', '', name.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def load_mapping(path):
    """Load committer mapping file."""
    entries = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[1:], start=2):
            parts = line.strip().split(';')
            if len(parts) >= 4:
                entries.append({
                    'line': i,
                    'committer': parts[0],
                    'email': parse_email(parts[0]),
                    'name': parse_name(parts[0]),
                    'projects': parts[1],
                    'canonical': parts[2].lower().strip(),
                    'org': parts[3]
                })
    return entries


def is_real_email(email):
    """Check if email is a real email (not GitHub noreply)."""
    return 'users.noreply.github.com' not in email


def email_priority(email):
    """Return priority score for email (higher is better)."""
    # Invalid/placeholder emails
    if email in ['--get', 'unknown'] or not '@' in email:
        return -1
    
    if not is_real_email(email):
        return 0  # GitHub noreply - lowest priority
    
    # Personal free email services
    if any(domain in email for domain in ['gmail.com', 'outlook.', 'yahoo.', 'hotmail.', 'live.', 'proton', 'tuta.com']):
        return 1
    
    # Student emails
    if any(domain in email for domain in ['student', 'epita.fr', 'polytechnique.org', 'telecom-sudparis.eu']):
        return 2
    
    # Professional/organizational emails
    return 3


def choose_canonical(emails):
    """Choose the most professional email from a list."""
    return max(emails, key=email_priority)


def find_duplicates(entries):
    """Find potential duplicate identities."""
    
    canonical_groups = defaultdict(list)
    for entry in entries:
        canonical_groups[entry['canonical']].append(entry)
    
    name_groups = defaultdict(list)
    for entry in entries:
        if entry['name']:
            norm_name = normalize_name(entry['name'])
            if norm_name:
                name_groups[norm_name].append(entry)
    
    username_groups = defaultdict(list)
    for entry in entries:
        email = entry['email']
        username = email.split('@')[0]
        if not re.match(r'^\d+$', username) and '[bot]' not in username:
            username_groups[username].append(entry)
    
    # Find same name with multiple real emails (potential duplicates)
    name_email_groups = {}
    for norm_name, group in name_groups.items():
        real_emails = [e for e in group if is_real_email(e['email'])]
        if len(real_emails) > 1:
            unique_emails = set(e['email'] for e in real_emails)
            if len(unique_emails) > 1:
                name_email_groups[norm_name] = group  # Include all entries for context
    
    return {
        'by_name': {k: v for k, v in name_groups.items() if len(v) > 1},
        'by_username': {k: v for k, v in username_groups.items() if len(v) > 1},
        'by_canonical': {k: v for k, v in canonical_groups.items() if len(v) > 1},
        'by_name_diff_email': name_email_groups
    }


def print_duplicates(duplicates):
    """Print duplicate analysis."""
    print("=" * 80)
    print("SAME NAME WITH DIFFERENT EMAIL ADDRESSES")
    print("=" * 80)
    
    for norm_name, group in sorted(duplicates['by_name_diff_email'].items()):
        real_emails = [e for e in group if is_real_email(e['email'])]
        github_emails = [e for e in group if not is_real_email(e['email'])]
        
        real_email_set = set(e['email'] for e in real_emails)
        canonicals = set(e['canonical'] for e in group)
        
        print(f"\n{norm_name.upper()} ({len(real_emails)} real emails, {len(github_emails)} GitHub, {len(canonicals)} canonical):")
        
        if real_emails:
            print("  Real emails:")
            for entry in real_emails:
                print(f"    Line {entry['line']}: {entry['email']}")
                print(f"      → canonical: {entry['canonical']}, org: {entry['org']}")
        
        if github_emails:
            print("  GitHub noreply (for reference):")
            for entry in github_emails:
                print(f"    Line {entry['line']}: {entry['email']}")
                print(f"      → canonical: {entry['canonical']}, org: {entry['org']}")
    
    print("\n" + "=" * 80)
    print("POTENTIAL DUPLICATES BY NAME")
    print("=" * 80)
    
    for norm_name, group in sorted(duplicates['by_name'].items()):
        canonicals = set(e['canonical'] for e in group)
        if len(canonicals) > 1:
            print(f"\n{norm_name.upper()} ({len(group)} entries, {len(canonicals)} canonical emails):")
            for entry in group:
                print(f"  Line {entry['line']}: {entry['committer']}")
                print(f"    → canonical: {entry['canonical']}, org: {entry['org']}")
    
    print("\n" + "=" * 80)
    print("POTENTIAL DUPLICATES BY EMAIL USERNAME")
    print("=" * 80)
    
    for username, group in sorted(duplicates['by_username'].items()):
        canonicals = set(e['canonical'] for e in group)
        if len(canonicals) > 1:
            print(f"\n{username} ({len(group)} entries, {len(canonicals)} canonical emails):")
            for entry in group:
                print(f"  Line {entry['line']}: {entry['email']}")
                print(f"    → canonical: {entry['canonical']}, org: {entry['org']}")
    
    print("\n" + "=" * 80)
    print("ALREADY GROUPED IDENTITIES (same canonical)")
    print("=" * 80)
    
    for canonical, group in sorted(duplicates['by_canonical'].items()):
        print(f"\n{canonical} ({len(group)} entries):")
        for entry in group:
            print(f"  Line {entry['line']}: {entry['committer']}")


def apply_canonical_fixes(org_map_path, duplicates):
    """Update mapping file to use best canonical email for each duplicate group."""
    from collections import defaultdict
    
    # Build mapping: email -> best canonical
    email_to_canonical = {}
    
    for norm_name, group in duplicates['by_name_diff_email'].items():
        # Get all emails for this person
        all_emails = [e['email'] for e in group]
        # Choose the best one
        best_canonical = choose_canonical(all_emails)
        # Map all emails to this canonical
        for email in all_emails:
            email_to_canonical[email] = best_canonical
    
    # Read original file
    with open(org_map_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update canonical column
    updated_lines = [lines[0]]  # Keep header
    changes = 0
    
    for line in lines[1:]:
        parts = line.strip().split(';')
        if len(parts) >= 4:
            email = parse_email(parts[0])
            old_canonical = parts[2].lower().strip()
            
            if email in email_to_canonical:
                new_canonical = email_to_canonical[email]
                if old_canonical != new_canonical:
                    parts[2] = new_canonical
                    changes += 1
            
            updated_lines.append(';'.join(parts) + '\n')
        else:
            updated_lines.append(line)
    
    # Write back
    with open(org_map_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    return changes


def sort_org_mapping(org_map_path):
    """Sort organization mapping file by canonical email, then by committer name."""
    with open(org_map_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    header = lines[0]
    entries = []
    
    for line in lines[1:]:
        parts = line.strip().split(';')
        if len(parts) >= 4:
            entries.append({
                'committer': parts[0],
                'projects': parts[1],
                'canonical': parts[2].lower().strip(),
                'org': parts[3],
                'line': line.strip()
            })
    
    # Sort by canonical (case-insensitive), then by committer
    entries.sort(key=lambda e: (e['canonical'], e['committer'].lower()))
    
    # Write back
    with open(org_map_path, 'w', encoding='utf-8') as f:
        f.write(header)
        for entry in entries:
            f.write(f"{entry['committer']};{entry['projects']};{entry['canonical']};{entry['org']}\n")
    
    return len(entries)
