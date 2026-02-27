# Report Format Specification

## Structure

### Cover Page
- OpenRail logo
- Title: "Quarterly Metrics Report"
- Quarter: "Q4 2025"
- Scope: date range
- Issue date
- Prepared by
- Bitergia logo

### Table of Contents
1. Spotlight Metric of the Quarter
2. OpenRail-Wide Project Statistics
3. Project Overview Pages (grouped by stage)
4. Appendices

## Section Details

### 1. Spotlight Metric of the Quarter
- Narrative highlight with supporting visualization
- Example: Cross-company collaboration pie chart

### 2. OpenRail-Wide Project Statistics

**Summary Statistics:**
- Total active contributors (includes commits, issues, PRs, comments)
- Total active committers (commit authors only)
- Number of human commits across all projects
- Number of code-contributing organizations

**Activity Trend:**
- Stacked horizontal bar chart showing commits per project per month
- Color-coded by commit volume ranges (0-100, 100-200, etc.)

**Code-committing Organizations:**
- List of organizations with commit activity
- Note about freelancers/individuals not listed as organizations

### 3. Project Overview Pages

Grouped by lifecycle stage (Stage 2 - Qualified, Stage 1 - Onboarded)

**Per Project:**
- Project name and full title
- Website URL
- Description
- Contributors: X (Y committers) between [dates]
- Key organizations (if applicable)
- Activity trend chart: monthly human commits, stacked by organization
- Repositories: bulleted list of GitHub URLs

**Charts:**
- Bar chart: monthly commits, color-coded by organization
- Pie chart: organization distribution (for projects with multiple orgs)

## Data Requirements

### MVP Scope (Phase 1)
- Total commits (human, non-merge)
- Unique committers
- Per-project breakdown
- Monthly trends
- Simple organization attribution (default to "Unknown")

### Future (Phase 2)
- Contributors vs committers distinction
- Issue/PR activity
- Advanced visualizations
- Spotlight metrics

## Output Format

- Markdown with embedded data for charts
- PDF generation via Pandoc with custom styling
- Beige/cream background with orange accent dots
- Bitergia owl logo watermark
