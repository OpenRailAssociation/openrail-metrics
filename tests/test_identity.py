"""Tests for identity module."""

from openrail_metrics.identity import normalize_email, get_canonical_identity, pseudonymize


def test_normalize_email():
    assert normalize_email("User@Example.COM") == "user@example.com"
    assert normalize_email("  test@test.com  ") == "test@test.com"


def test_get_canonical_identity():
    assert get_canonical_identity("user@example.com") == "email:user@example.com"
    assert get_canonical_identity("Test@Example.COM") == "email:test@example.com"


def test_pseudonymize():
    canonical = "email:test@example.com"
    result = pseudonymize(canonical)
    
    assert len(result) == 12
    
    # Deterministic
    assert pseudonymize(canonical) == result


def test_pseudonymize_different_emails():
    id1 = pseudonymize("email:user1@example.com")
    id2 = pseudonymize("email:user2@example.com")
    
    assert id1 != id2
