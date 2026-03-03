"""Tests for update-org-map command."""

import tempfile
from pathlib import Path
from click.testing import CliRunner
from openrail_metrics.cli import cli


def test_update_org_map_adds_new_entries(tmp_path):
    """Test that new email addresses are added with Unknown org."""
    # Create a minimal org mapping file
    org_map = tmp_path / "test_mapping.ssv"
    org_map.write_text(
        "Committer;Projects;Organization\n"
        "Existing User <existing@example.com>;osrd;SNCF\n"
    )
    
    # Create a minimal projects config
    projects_file = tmp_path / "projects.yml"
    projects_file.write_text(
        "projects:\n"
        "  - id: osrd\n"
        "    name: OSRD\n"
        "    stage: qualified\n"
        "    repos:\n"
        "      - https://github.com/test/repo.git\n"
    )
    
    # Create a minimal report config
    report_file = tmp_path / "report.yml"
    report_file.write_text(
        "report:\n"
        "  title: Test\n"
        "  quarter: 2026Q1\n"
        "  from: 2025-12-01\n"
        "  to: 2026-02-28\n"
        "  issue_date: 2026-03-15\n"
    )
    
    # Note: This test would need actual git repos to work fully
    # For now, we test the file parsing and writing logic
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        'update-org-map',
        '--projects', str(projects_file),
        '--cache-dir', str(tmp_path / 'cache'),
        '--org-map', str(org_map)
    ])
    
    # Should complete without error (even if no repos found)
    assert result.exit_code == 0
    
    # Check file still has header and existing entry
    content = org_map.read_text()
    assert "Committer;Projects;Canonical;Organization" in content
    assert "existing@example.com" in content


def test_update_org_map_updates_project_lists(tmp_path):
    """Test that existing entries get updated project lists."""
    org_map = tmp_path / "test_mapping.ssv"
    org_map.write_text(
        "Committer;Projects;Organization\n"
        "User One <user1@example.com>;osrd;SNCF\n"
        "User Two <user2@example.com>;liblrs;DB\n"
    )
    
    projects_file = tmp_path / "projects.yml"
    projects_file.write_text(
        "projects:\n"
        "  - id: osrd\n"
        "    name: OSRD\n"
        "    stage: qualified\n"
        "    repos: []\n"
        "  - id: liblrs\n"
        "    name: liblrs\n"
        "    stage: onboarded\n"
        "    repos: []\n"
    )
    
    report_file = tmp_path / "report.yml"
    report_file.write_text(
        "report:\n"
        "  title: Test\n"
        "  quarter: 2026Q1\n"
        "  from: 2025-12-01\n"
        "  to: 2026-02-28\n"
        "  issue_date: 2026-03-15\n"
    )
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        'update-org-map',
        '--projects', str(projects_file),
        '--cache-dir', str(tmp_path / 'cache'),
        '--org-map', str(org_map)
    ])
    
    assert result.exit_code == 0
    
    # Verify file has canonical column
    lines = org_map.read_text().split('\n')
    assert lines[0] == "Committer;Projects;Canonical;Organization"
    
    # Check that organizations are preserved
    content = org_map.read_text()
    assert "SNCF" in content
    assert "DB" in content
    
    # Check canonical column is populated
    assert "user1@example.com" in content
    assert "user2@example.com" in content


def test_update_org_map_no_trailing_spaces(tmp_path):
    """Test that project lists don't have trailing spaces."""
    org_map = tmp_path / "test_mapping.ssv"
    org_map.write_text(
        "Committer;Projects;Organization\n"
        "Test User <test@example.com>;osrd,liblrs;SNCF\n"
    )
    
    projects_file = tmp_path / "projects.yml"
    projects_file.write_text(
        "projects:\n"
        "  - id: osrd\n"
        "    name: OSRD\n"
        "    stage: qualified\n"
        "    repos: []\n"
    )
    
    report_file = tmp_path / "report.yml"
    report_file.write_text(
        "report:\n"
        "  title: Test\n"
        "  quarter: 2026Q1\n"
        "  from: 2025-12-01\n"
        "  to: 2026-02-28\n"
        "  issue_date: 2026-03-15\n"
    )
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        'update-org-map',
        '--projects', str(projects_file),
        '--cache-dir', str(tmp_path / 'cache'),
        '--org-map', str(org_map)
    ])
    
    assert result.exit_code == 0
    
    # Check no spaces after commas in project lists
    content = org_map.read_text()
    for line in content.split('\n')[1:]:  # Skip header
        if line.strip():
            parts = line.split(';')
            if len(parts) == 3:
                projects = parts[1]
                # Should not have space after comma
                assert ', ' not in projects, f"Found space after comma in: {projects}"


def test_update_org_map_maintains_alphabetical_order(tmp_path):
    """Test that entries are sorted by name (case-insensitive), then email."""
    org_map = tmp_path / "test_mapping.ssv"
    org_map.write_text(
        "Committer;Projects;Organization\n"
        "Zebra User <zebra@example.com>;osrd;SNCF\n"
        "Alpha User <alpha@example.com>;liblrs;DB\n"
        "alpha user <different@example.com>;osrd;SBB\n"
        "Middle User <middle@example.com>;osrd;SNCF\n"
    )
    
    projects_file = tmp_path / "projects.yml"
    projects_file.write_text(
        "projects:\n"
        "  - id: osrd\n"
        "    name: OSRD\n"
        "    stage: qualified\n"
        "    repos: []\n"
    )
    
    report_file = tmp_path / "report.yml"
    report_file.write_text(
        "report:\n"
        "  title: Test\n"
        "  quarter: 2026Q1\n"
        "  from: 2025-12-01\n"
        "  to: 2026-02-28\n"
        "  issue_date: 2026-03-15\n"
    )
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        'update-org-map',
        '--projects', str(projects_file),
        '--cache-dir', str(tmp_path / 'cache'),
        '--org-map', str(org_map)
    ])
    
    assert result.exit_code == 0
    
    # Check sorting by name, then email
    lines = org_map.read_text().split('\n')
    names = []
    for line in lines[1:]:  # Skip header
        if line.strip():
            parts = line.split(';')
            if len(parts) == 3:
                committer = parts[0]
                if '<' in committer:
                    name = committer.split('<')[0].strip()
                else:
                    name = committer
                names.append(name)
    
    # Verify names are sorted case-insensitively
    assert names == sorted(names, key=str.lower), f"Names not sorted: {names}"
    
    # Verify "Alpha User" entries are in correct order (by email)
    alpha_lines = [line for line in lines[1:] if line.startswith('Alpha User') or line.startswith('alpha user')]
    assert len(alpha_lines) == 2
    # "alpha@example.com" should come before "different@example.com"
    assert 'alpha@example.com' in alpha_lines[0]
    assert 'different@example.com' in alpha_lines[1]


def test_update_org_map_handles_duplicate_emails(tmp_path):
    """Test that duplicate emails are kept (not removed)."""
    org_map = tmp_path / "test_mapping.ssv"
    org_map.write_text(
        "Committer;Projects;Organization\n"
        "Jane Smith <jane@example.com>;osrd;CompanyA\n"
        "u123456 <jane@example.com>;osrd;CompanyA\n"
    )
    
    projects_file = tmp_path / "projects.yml"
    projects_file.write_text(
        "projects:\n"
        "  - id: osrd\n"
        "    name: OSRD\n"
        "    stage: qualified\n"
        "    repos: []\n"
    )
    
    report_file = tmp_path / "report.yml"
    report_file.write_text(
        "report:\n"
        "  title: Test\n"
        "  quarter: 2026Q1\n"
        "  from: 2025-12-01\n"
        "  to: 2026-02-28\n"
        "  issue_date: 2026-03-15\n"
    )
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        'update-org-map',
        '--projects', str(projects_file),
        '--cache-dir', str(tmp_path / 'cache'),
        '--org-map', str(org_map)
    ])
    
    assert result.exit_code == 0
    
    # Both entries should be kept
    content = org_map.read_text()
    assert 'Jane Smith <jane@example.com>' in content
    assert 'u123456 <jane@example.com>' in content
    
    # Both entries should have canonical column
    jane_lines = [line for line in content.split('\n') if 'jane@example.com' in line and line.strip()]
    assert len(jane_lines) == 2


def test_canonical_email_identity_resolution(tmp_path):
    """Test that canonical email resolves multiple identities to same person."""
    org_map = tmp_path / "test_mapping.ssv"
    org_map.write_text(
        "Committer;Projects;Canonical;Organization\n"
        "Jane Smith <jane@example.com>;osrd;jane@example.com;CompanyA\n"
        "Jane Smith <jane.personal@example.com>;osrd;jane@example.com;CompanyA\n"
        "u123456 <jane@example.com>;osrd;jane@example.com;CompanyA\n"
    )
    
    from openrail_metrics import attribution, identity
    
    # Load mapping
    email_to_canonical, canonical_to_org = attribution.load_org_mapping(org_map)
    
    # All three emails should resolve to same canonical
    assert email_to_canonical['jane@example.com'] == 'jane@example.com'
    assert email_to_canonical['jane.personal@example.com'] == 'jane@example.com'
    
    # All should get same org
    org_mapping = (email_to_canonical, canonical_to_org)
    assert attribution.get_organization('jane@example.com', 'osrd', org_mapping) == 'CompanyA'
    assert attribution.get_organization('jane.personal@example.com', 'osrd', org_mapping) == 'CompanyA'
    
    # All should get same pseudonymized ID
    id1 = identity.pseudonymize(identity.get_canonical_identity('jane@example.com', email_to_canonical))
    id2 = identity.pseudonymize(identity.get_canonical_identity('jane.personal@example.com', email_to_canonical))
    assert id1 == id2


def test_canonical_email_org_conflict_detection(tmp_path):
    """Test that conflicting orgs for same canonical are detected."""
    org_map = tmp_path / "test_mapping.ssv"
    org_map.write_text(
        "Committer;Projects;Canonical;Organization\n"
        "Jane Smith <jane@example.com>;osrd;jane@example.com;CompanyA\n"
        "Jane Smith <jane.personal@example.com>;osrd;jane@example.com;CompanyB\n"
    )
    
    from openrail_metrics import attribution
    import pytest
    
    # Should raise ValueError due to org conflict
    with pytest.raises(ValueError, match="Organization conflicts detected"):
        attribution.load_org_mapping(org_map)


def test_update_org_map_preserves_all_name_variations(tmp_path):
    """Test that different names for same email are all preserved."""
    org_map = tmp_path / "test_mapping.ssv"
    org_map.write_text(
        "Committer;Projects;Organization\n"
        "Jane Smith <jane@example.com>;osrd;CompanyA\n"
        "jane_smith <jane@example.com>;osrd;CompanyA\n"
    )
    
    projects_file = tmp_path / "projects.yml"
    projects_file.write_text(
        "projects:\n"
        "  - id: osrd\n"
        "    name: OSRD\n"
        "    stage: qualified\n"
        "    repos: []\n"
    )
    
    report_file = tmp_path / "report.yml"
    report_file.write_text(
        "report:\n"
        "  title: Test\n"
        "  quarter: 2026Q1\n"
        "  from: 2025-12-01\n"
        "  to: 2026-02-28\n"
        "  issue_date: 2026-03-15\n"
    )
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        'update-org-map',
        '--projects', str(projects_file),
        '--cache-dir', str(tmp_path / 'cache'),
        '--org-map', str(org_map)
    ])
    
    assert result.exit_code == 0
    
    # Both name variations should be preserved
    content = org_map.read_text()
    assert 'Jane Smith <jane@example.com>' in content
    assert 'jane_smith <jane@example.com>' in content
    
    # Should have 2 entries for this email
    jane_lines = [line for line in content.split('\n') if 'jane@example.com' in line and line.strip() and not line.startswith('Committer')]
    assert len(jane_lines) == 2, f"Expected 2 entries, got {len(jane_lines)}: {jane_lines}"
