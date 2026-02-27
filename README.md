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
openrail-metrics all \
  --projects projects.yml \
  --report report.yml \
  --org-map /path/to/openrail_committers.ssv
```

Output will be generated in the `out/` directory:
- `out/report.md` - Markdown report
- `out/report.pdf` - PDF report with embedded graphics
- `out/graphics/` - All generated charts

## Report Structure

The generated report has three sections:

### 1. Quarterly Snapshot
Metrics for the reporting quarter only (3 months):
- Active committers this quarter
- Human commits this quarter
- Contributing organizations this quarter
- Organization distribution pie chart

### 2. Progress Data (12-Month View)
Activity trends over the past 12 months:
- Total committers, commits, organizations
- Activity heatmap showing all projects
- Shows patterns and trends

### 3. Project Details
Per-project statistics and visualizations:
- 12-month activity trends
- Stacked bar charts showing contributions by organization
- Grouped by project stage (Qualified, Onboarded)

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
Committer;Projects;Organization
Name <email@example.com>;osrd,liblrs;Organization Name
```

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

See [architecture.md](architecture.md) for detailed implementation notes.

See [design.md](design.md) for the original design specification.

# License

This repo is licensed under Apache-2.0.
