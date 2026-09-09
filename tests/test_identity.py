"""Tests for identity module."""

from openrail_metrics.identity import (
    normalize_email,
    parse_committer_email,
    get_canonical_identity,
    pseudonymize,
)


def test_normalize_email():
    assert normalize_email("User@Example.COM") == "user@example.com"
    assert normalize_email("  test@test.com  ") == "test@test.com"


def test_normalize_email_strips_stray_boundary_chars():
    # Real-world regression: a commit whose git config wrapped the address in
    # U+00A8 must normalize to the clean address so it does not split identity.
    assert normalize_email("\u00a8sim.gaubert.sg@gmail.com\u00a8") == "sim.gaubert.sg@gmail.com"
    assert normalize_email('"quoted@example.com"') == "quoted@example.com"
    assert normalize_email("<addr@example.com>") == "addr@example.com"


def test_normalize_email_preserves_internal_characters():
    # +, ., -, _ inside the address are legitimate and must survive.
    assert normalize_email("tristram+git@tristramg.eu") == "tristram+git@tristramg.eu"
    assert normalize_email("first.last-name_x@sub.example.com") == "first.last-name_x@sub.example.com"
    assert (
        normalize_email("49699333+dependabot[bot]@users.noreply.github.com")
        == "49699333+dependabot[bot]@users.noreply.github.com"
    )


def test_parse_committer_email():
    assert parse_committer_email("Jane Doe <jane@example.com>") == "jane@example.com"
    assert parse_committer_email("bare@example.com") == "bare@example.com"
    # Both name and address wrapped in stray marks; only the address is used.
    assert (
        parse_committer_email("\u00a8Simon\u00a8 <\u00a8sim.gaubert.sg@gmail.com\u00a8>")
        == "sim.gaubert.sg@gmail.com"
    )


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
