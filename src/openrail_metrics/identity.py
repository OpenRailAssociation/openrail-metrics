"""Identity normalization and pseudonymization."""

import hashlib


def normalize_email(email: str) -> str:
    """Normalize email address."""
    return email.lower().strip()


def get_canonical_identity(email: str) -> str:
    """Get canonical identity for an email (no aliases in MVP)."""
    return f"email:{normalize_email(email)}"


def pseudonymize(canonical_identity: str) -> str:
    """Generate pseudonymous committer ID."""
    hash_obj = hashlib.sha256(canonical_identity.encode('utf-8'))
    return hash_obj.hexdigest()[:12]
