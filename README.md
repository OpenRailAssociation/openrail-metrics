# OpenRail Metrics

This repo contains the tool we use to create the quarterly OpenRail metrics report and the resulting reports.

## Quick Start

### Prerequisites

- Python 3.11+
- Git
- Pandoc (for PDF generation)
- WeasyPrint (for PDF generation)

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install the package
pip install -e .
```

### Usage

Generate a quarterly report:

```bash
openrail-metrics all
  --org-map /path/to/openrail_committers.ssv
```

Output will be generated in the `out/` directory:
- `out/report.md` - Markdown report
- `out/report.pdf` - PDF report with embedded graphics
- `out/graphics/` - All generated charts

## Report Structure

The overall structure of the generated report is defined in the `templates/report.md.template` template file. The structure of the project section is defined in `templates/project.md.template`.

## Configuration Files

### projects.yml

Defines OpenRail projects and their repositories:

```yaml
projects:
  - id: osrd
    name: OSRD
    stage: qualified
    repos:
      - https://github.com/OpenRailAssociation/osrd.git
```

### report.yml

Defines the reporting period:

```yaml
report:
  title: "OpenRail Metrics Report"
  quarter: "2026Q1"
  from: 2025-12-01
  to: 2026-02-28
  issue_date: 2026-03-15
```

### Organization Mapping (SSV)

External file mapping committers to organizations:

```
Committer;Projects;Canonical;Organization
Name <email@example.com>;osrd,liblrs;email@example.com,Organization Name
```

Its format is defined in `docs/org-mapping-format.md`.

## Data Privacy

The tool is designed with privacy in mind:
- Email addresses are never written to output files
- Committer identities are pseudonymized using SHA256 hashing
- Only aggregated statistics are published
- Organization mapping is kept in external files

## Development

Run tests:

```bash
pytest tests/ -v
```

## Architecture

See [docs/architecture.md](architecture.md) for detailed implementation notes.

See [docs/design.md](design.md) for the original design specification.

# License

This repo is licensed under Apache-2.0.
