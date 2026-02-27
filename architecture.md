# Implementation Architecture

## Technology Stack

- **Language**: Python 3.11+
- **PDF Generation**: Pandoc + WeasyPrint
- **Git Operations**: GitPython or subprocess calls to git CLI
- **CLI Framework**: Click or argparse

## Project Structure

```
src/
  openrail_metrics/
    __init__.py
    cli.py              # CLI entry point
    config.py           # Config loading/validation
    git_ops.py          # Repository sync and log extraction
    identity.py         # Email normalization, aliasing, pseudonymization
    attribution.py      # Organization mapping
    aggregation.py      # Metrics calculation
    rendering.py        # Markdown generation
    pdf.py              # PDF generation
tests/
  fixtures/           # Example config and mapping files
  test_*.py
```

## Data Flow

```
projects.yml + report.yml → Config
                              ↓
repos-cache/ ← sync ← Git URLs
                              ↓
git log → Raw commits (date, email, hash, parents)
                              ↓
Normalize emails → Apply aliases → Canonical identity
                              ↓
SHA256 → Pseudonymous committer_id
                              ↓
Apply org mapping → Commit events (project, org, committer_id, date)
                              ↓
Aggregate → Metrics (per-project, per-org, monthly trends)
                              ↓
Render → report.md → Pandoc → report.pdf
```

## Core Design Decisions

### Identity Processing
- All email normalization: lowercase + strip
- Canonical identity: `person:<key>` (if aliased) or `email:<normalized>`
- Pseudonymous ID: first 12 chars of SHA256(canonical_identity)
- No salt (deterministic across runs)

### Privacy
- Emails never written to disk
- Only pseudonymous IDs and aggregates in outputs
- Org/alias mapping files stay external (CLI args)

### Git Operations
- Bare mirrors in `repos-cache/<sanitized-url>.git`
- Clone once, fetch updates
- Extract via `git log --pretty=format:...`
- Filter: exclude bots (via mapping), exclude merges (parent count > 1)

### Aggregation Metrics
- Per project: commits, unique committers, orgs, monthly breakdown
- Per org: commits across all projects
- OpenRail-wide: total commits, committers, orgs, monthly trend

### Output Structure
- `out/raw/commits.ssv` - all commit events
- `out/tables/*.csv` - summary tables
- `out/data/*.yaml` - structured metrics
- `out/meta/run.yml` - reproducibility metadata
- `out/report.md` + `out/report.pdf`

## MVP Scope

**Phase 1 (Minimal Working Version):**
- Load `projects.yml` and `report.yml`
- Sync repos (clone or fetch)
- Extract commits in date range
- Basic email normalization (no aliases yet)
- Default org to "Unknown"
- Generate pseudonymous IDs
- Aggregate: per-project commit counts and unique committers
- Render simple Markdown report
- Generate PDF via Pandoc

**Deferred to Phase 2:**
- Alias mapping
- Organization mapping
- Monthly trends
- Bot filtering
- Advanced report formatting
- `publish` command
- Comprehensive validation

## Error Handling

- Invalid config → fail fast with clear message
- Git operation failures → log and skip repo
- Missing mapping entries → default to "Unknown", log warning
- Duplicate aliases/orgs → error and exit

## Testing Strategy

- Unit tests for identity normalization and pseudonymization
- Fixture-based tests with small example repos
- Integration test: full pipeline with synthetic data
- Validation tests for config schemas
