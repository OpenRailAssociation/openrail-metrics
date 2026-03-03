# Implementation Architecture

## Technology Stack

- **Language**: Python 3.11+
- **PDF Generation**: Pandoc + WeasyPrint
- **Git Operations**: subprocess calls to git CLI
- **CLI Framework**: Click
- **Visualization**: Matplotlib
- **Date Handling**: python-dateutil

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
    aggregation.py      # Metrics calculation (quarter + 12-month)
    rendering.py        # Markdown generation (3-section structure)
    graphics.py         # Chart generation (heatmaps, stacked bars, pie charts)
    pdf.py              # PDF generation
tests/
  test_*.py           # Unit tests for core modules
```

## Data Flow

```
projects.yml + report.yml → Config
                              ↓
repos-cache/ ← sync ← Git URLs
                              ↓
git log (12 months) → Raw commits (date, email, hash, parents)
                              ↓
Normalize emails → Canonical identity (email:<normalized>)
                              ↓
SHA256 → Pseudonymous committer_id (first 12 chars)
                              ↓
Apply org mapping → Commit events (project, org, committer_id, date)
                              ↓
Aggregate → Quarter metrics + 12-month metrics
                              ↓
Generate graphics → Heatmaps, stacked charts, pie charts
                              ↓
Render → report.md (3 sections) → Pandoc → report.pdf
```

## Core Design Decisions

### Identity Processing
- All email normalization: lowercase + strip
- Canonical identity: `email:<normalized>` (aliases not yet implemented)
- Pseudonymous ID: first 12 chars of SHA256(canonical_identity)
- No salt (deterministic across runs)

### Privacy
- Emails never written to disk
- Only pseudonymous IDs and aggregates in outputs
- Org/alias mapping files stay external (CLI args)

### Organization Attribution
**Design Decision**: Organization mapping is project-agnostic.

**Rationale**: 
- A person's organizational affiliation doesn't change based on which project they contribute to
- The "Projects" column in the SSV mapping file is informational only (helps maintainers track contributor activity)
- Attribution logic maps `email → organization` directly, ignoring project context
- This ensures consistent attribution across all projects (e.g., administrative, technical, etc.)

**Implementation**:
- `load_org_mapping()` returns `Dict[email, org]` (not `Dict[email, Dict[project, org]]`)
- `get_organization()` takes `project_id` parameter for API compatibility but doesn't use it for lookup
- All commits from an email get the same organization, regardless of project

**Impact**:
- Simplifies mapping file maintenance (one entry per person, not per person-project combination)
- Ensures administrative/infrastructure contributions are properly attributed
- "Unknown" organization is used when email is not in mapping file

### Git Operations
- Bare mirrors in `repos-cache/<sanitized-url>.git`
- Clone once, fetch updates
- Extract via `git log --pretty=format:...`
- Filter: exclude merges (parent count > 1)
- Extract 12 months of data (9 months before quarter + 3 quarter months)

### Time Windows
- **Quarterly snapshot**: Metrics for the 3-month reporting period only
- **Progress data**: 12-month rolling window for trends and context
- **Per-project charts**: 12-month view with consistent date ranges across all projects

### Aggregation Metrics

**Quarter-only (snapshot):**
- Active committers this quarter
- Human commits this quarter
- Contributing organizations this quarter
- Organization commit distribution (for pie chart)

**12-month (progress):**
- Total committers (12 months)
- Total commits (12 months)
- Total organizations (12 months)
- Per-project: commits, committers, orgs, monthly breakdown
- Per-project: monthly commits by organization (for stacked charts)
- Per-org: total commits across all projects

**Unknown Organization Handling:**
- Commits from unmapped emails are attributed to "Unknown" organization
- "Unknown" is included in all statistics and visualizations
- Extract command reports unmapped emails as warnings to stderr
- Helps identify missing mappings that need manual review

### Visualization Strategy

**Section 1 - Quarterly Snapshot:**
- Organization pie chart (quarter-only data)

**Section 2 - Progress Data:**
- Activity heatmap: 12-month grid (projects × months) with red color intensity
- Shows all projects with consistent month range

**Section 3 - Per-Project Details:**
- Stacked bar chart: 12-month activity by organization
- Each organization shown as colored segment
- Consistent month range across all projects (even if no commits)

### Output Structure
- `out/metrics.json` - Aggregated metrics (intermediate file)
- `out/graphics/` - All generated charts
  - `activity_heatmap.png` - 12-month project activity grid
  - `quarter_org_distribution.png` - Quarter-only org pie chart
  - `{project}_trend.png` - Per-project stacked bar charts
- `out/report.md` - Three-section Markdown report
- `out/report.pdf` - PDF with embedded graphics

### CLI Commands

**Pipeline Commands:**
- `sync` - Clone/update repositories to local cache
- `extract` - Extract commits and aggregate metrics → `out/metrics.json`
- `render` - Generate report and graphics from metrics → `out/report.md` + `out/graphics/`
- `pdf` - Convert markdown to PDF → `out/report.pdf`
- `all` - Run complete pipeline (sync → extract → render → pdf)
  - `--skip-sync` flag to skip repository sync step

**Maintenance Commands:**
- `update-org-map` - Update organization mapping file with new committers
  - Scans all repositories to find email addresses
  - Updates existing entries with current project lists
  - Adds new entries with organization set to "Unknown"
  - Modifies file in place while preserving format
  - No trailing spaces in project lists

## Report Structure

### Section 1: Quarterly Snapshot
- Metrics for the reporting quarter only (3 months)
- Active committers, commits, organizations
- Organization distribution pie chart

### Section 2: Progress Data (12-Month View)
- Metrics over past 12 months for context
- Activity heatmap showing all projects
- Shows trends and patterns

### Section 3: Project Details
- Per-project 12-month statistics
- Stacked bar charts showing monthly activity by organization
- Grouped by project stage (Qualified, Onboarded)

## Implementation Status

**Completed (Phase 1+):**
- ✅ Load `projects.yml` and `report.yml`
- ✅ Sync repos (clone or fetch)
- ✅ Extract commits with extended date range (12 months)
- ✅ Email normalization
- ✅ Organization mapping from external SSV file
- ✅ Generate pseudonymous IDs
- ✅ Aggregate: quarter-specific and 12-month metrics
- ✅ Track monthly commits by organization per project
- ✅ Render three-section Markdown report
- ✅ Generate visualizations (heatmaps, stacked charts, pie charts)
- ✅ Generate PDF via Pandoc + WeasyPrint
- ✅ Unit tests for core modules

**Deferred:**
- ⏸️ Alias mapping (identity consolidation)
- ⏸️ Bot filtering (currently manual via org mapping)
- ⏸️ `publish` command (copy to reports/ directory)
- ⏸️ Reproducibility metadata (out/meta/run.yml)
- ⏸️ Raw data exports (commits.ssv, CSV tables)

## Key Learnings

### 1. Time Window Design
**Challenge**: Balancing snapshot metrics vs. trend analysis.

**Solution**: Dual time windows:
- Extract 12 months of data (9 before + 3 quarter months)
- Aggregate separately for quarter (snapshot) and 12 months (trends)
- Provides context without diluting quarterly focus

### 2. Consistent Date Ranges
**Challenge**: Projects with sparse activity showed different month ranges.

**Solution**: Calculate month range from ALL projects' data, not per-project. Ensures visual consistency and comparability.

### 3. Organization Attribution in Charts
**Challenge**: Showing both activity trends and org distribution without cluttering.

**Solution**: Stacked bar charts integrate both dimensions:
- X-axis: time (months)
- Y-axis: commits
- Color segments: organizations
- Single chart replaces separate trend + pie chart

### 4. Privacy-First Aggregation
**Challenge**: Need org attribution without exposing individual identities.

**Solution**: 
- Pseudonymize at extraction time
- Track org at event level, not identity level
- Aggregate before rendering
- Never write raw emails to disk

### 5. Matplotlib for Reproducible Graphics
**Challenge**: Need consistent, embeddable graphics for PDF.

**Solution**:
- Use Agg backend (non-interactive)
- Save as PNG with fixed DPI (150)
- Consistent color schemes (Reds for heatmap, Set3 for orgs)
- Tight layout to prevent label cutoff

## Error Handling

- Invalid config → fail fast with clear message
- Git operation failures → continue with warning (don't fail entire run)
- Missing mapping entries → default to "Unknown", continue
- Missing org data for project → show simple bar chart instead of stacked

## Testing Strategy

- Unit tests for identity normalization and pseudonymization
- Unit tests for aggregation logic (quarter vs. 12-month)
- Unit tests for config loading
- Unit tests for git operations (URL sanitization)
- Integration testing via manual runs with real data
- Visual inspection of generated charts
