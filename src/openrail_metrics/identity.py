"""Identity normalization and pseudonymization."""

import hashlib
from typing import Optional, Dict


def normalize_email(email: str) -> str:
    """Normalize email address."""
    return email.lower().strip()


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
