"""Tests for the read-only `org-map show` command."""

from click.testing import CliRunner
from openrail_metrics.cli import cli


HEADER = "Committer;Projects;Canonical;Organization\n"


def _write(tmp_path, body):
    p = tmp_path / "mapping.ssv"
    p.write_text(HEADER + body, encoding="utf-8")
    return p


def _run(org_map, *extra):
    runner = CliRunner()
    return runner.invoke(cli, ["org-map", "show", "--org-map", str(org_map), *extra])


def test_show_sections_and_counts(tmp_path):
    # Two people at SNCF (one with two aliases sharing a canonical), one at SBB.
    org_map = _write(
        tmp_path,
        "Alice A <alice@a.fr>;osrd;alice@a.fr;SNCF\n"
        "alice-alt <alice.alt@a.fr>;osrd,liblrs;alice@a.fr;SNCF\n"
        "Bob B <bob@b.fr>;osrd;bob@b.fr;SNCF\n"
        "Carla C <carla@c.ch>;netzgrafik-editor;carla@c.ch;SBB\n"
    )

    result = _run(org_map)
    assert result.exit_code == 0
    out = result.output

    # Header: 4 entries, 3 people (alice has 2 rows -> 1 person), 2 orgs.
    assert "Committer mapping: 4 entries, 3 people, 2 organizations" in out

    # All three sections present.
    assert "== People (3) ==" in out
    assert "== Organizations (2) ==" in out
    assert "== Unresolved (0) ==" in out

    # Alias grouping: alice's two rows collapse to one person with 2 aliases,
    # and her projects are the union of both rows.
    people_block = out.split("== Organizations")[0]
    alice_line = next(l for l in people_block.splitlines() if "Alice A" in l)
    assert "liblrs" in alice_line and "osrd" in alice_line
    # aliases column shows 2 for Alice
    assert "2" in alice_line.split("osrd")[0]

    # Organizations: SNCF has 2 people / 3 entries, SBB 1 / 1.
    org_block = out.split("== Organizations")[1]
    sncf_line = next(l for l in org_block.splitlines() if l.startswith("SNCF"))
    assert sncf_line.split() == ["SNCF", "2", "3"]


def test_show_lists_unresolved(tmp_path):
    org_map = _write(
        tmp_path,
        "Known <known@x.fr>;osrd;known@x.fr;SNCF\n"
        "mystery@y.fr;osrd;mystery@y.fr;Unknown\n"
    )
    result = _run(org_map)
    assert result.exit_code == 0
    assert "== Unresolved (1) ==" in result.output
    assert "mystery@y.fr" in result.output.split("== Unresolved")[1]


def test_show_project_filter(tmp_path):
    org_map = _write(
        tmp_path,
        "Alice A <alice@a.fr>;osrd;alice@a.fr;SNCF\n"
        "Bob B <bob@b.fr>;netzgrafik-editor;bob@b.fr;SBB\n"
    )
    result = _run(org_map, "--project", "osrd")
    assert result.exit_code == 0
    out = result.output

    assert "(project: osrd)" in out
    assert "Committer mapping: 1 entries, 1 people, 1 organizations" in out
    # Only the osrd person appears.
    assert "Alice A" in out
    assert "Bob B" not in out


def test_show_falls_back_to_canonical_when_no_name(tmp_path):
    # A bare-email row (no "Name <...>") should display the canonical email.
    org_map = _write(tmp_path, "bare@x.fr;osrd;bare@x.fr;SNCF\n")
    result = _run(org_map)
    assert result.exit_code == 0
    assert "bare@x.fr" in result.output.split("== Organizations")[0]


def test_show_does_not_modify_file(tmp_path):
    body = (
        "Alice A <alice@a.fr>;osrd;alice@a.fr;SNCF\n"
        "Bob B <bob@b.fr>;netzgrafik-editor;bob@b.fr;SBB\n"
    )
    org_map = _write(tmp_path, body)
    before = org_map.read_text(encoding="utf-8")

    result = _run(org_map)
    assert result.exit_code == 0
    assert org_map.read_text(encoding="utf-8") == before
