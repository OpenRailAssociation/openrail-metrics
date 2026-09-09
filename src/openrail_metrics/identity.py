"""Identity normalization and pseudonymization."""

import hashlib
import re
from typing import Optional, Dict

# A valid email must start and end with an alphanumeric character. Some commits
# carry git identities whose author.email is wrapped in stray punctuation (seen
# in the wild: a name and address both wrapped in U+00A8, "¨addr¨"). Left in the
# string, such junk produces a distinct canonical from the person's clean rows
# and splits their commits across two identities. Strip anything outside the
# leading/trailing alphanumeric boundary; internal +.-_% and @ are preserved.
_EMAIL_BOUNDARY = re.compile(r'^[^0-9a-z]+|[^0-9a-z]+$')


def normalize_email(email: str) -> str:
    """Normalize an email address: lowercase, trim whitespace, strip stray
    non-alphanumeric characters from the start and end."""
    return _EMAIL_BOUNDARY.sub('', email.strip().lower())


def parse_committer_email(committer_field: str) -> str:
    """Extract and normalize the email from a 'Name <email>' committer field,
    or from a bare-address field. Central parser so every call site normalizes
    identically."""
    match = re.search(r'<([^>]*)>', committer_field)
    raw = match.group(1) if match else committer_field
    return normalize_email(raw)


def get_canonical_identity(email: str, email_to_canonical: Optional[Dict[str, str]] = None) -> str:
    """Get canonical identity for an email, resolving aliases if mapping provided."""
    normalized = normalize_email(email)
    
    if email_to_canonical:
        canonical = email_to_canonical.get(normalized, normalized)
    else:
        canonical = normalized
    
    return f"email:{canonical}"


def pseudonymize(canonical_identity: str) -> str:
    """Generate pseudonymous committer ID."""
    hash_obj = hashlib.sha256(canonical_identity.encode('utf-8'))
    return hash_obj.hexdigest()[:12]
