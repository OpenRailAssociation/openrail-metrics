# OpenRail Quarterly Metrics Tool

## Design Document

------------------------------------------------------------------------

## 1. Purpose

The tool generates a quarterly OpenRail Association metrics report based
on Git commit activity.

It:

-   Aggregates activity per project and per organization
-   Counts unique human committers
-   Produces OpenRail-wide and per-project statistics
-   Generates a Markdown report and final PDF
-   Avoids publishing any personally identifiable information (PII)

The tool must be:

-   Repeatable
-   Configurable
-   Command-line driven
-   Based on standard text formats (YAML, CSV/SSV, Markdown)
-   Easy to evolve over time

The reporting period must be configurable (e.g. December--February).

------------------------------------------------------------------------

## 2. Non-Goals

-   No public exposure of names or email addresses
-   No advanced privacy framework
-   No web UI

The goal is minimal personal data processing with practical safeguards.

------------------------------------------------------------------------

## 3. High-Level Architecture

The tool is a CLI application with a deterministic pipeline:

1.  Sync repositories
2.  Extract commit data
3.  Normalize identities
4.  Attribute organizations
5.  Aggregate metrics
6.  Render report
7.  Generate PDF

Outputs are written to structured directories and can be regenerated at
any time.

------------------------------------------------------------------------

## 4. Inputs

### 4.1 Project Configuration (`projects.yml`)

Defines OpenRail projects and associated repositories.

``` yaml
projects:
  - id: osrd
    name: OSRD
    stage: incubation
    repos:
      - https://github.com/org/osrd-core.git
      - https://github.com/org/osrd-ui.git

  - id: liblrs
    name: libLRS
    stage: production
    repos:
      - https://github.com/org/liblrs.git
```

Rules:

-   `id` must match identifiers used in org mapping
-   Repo URLs are treated as canonical sources
-   Stages are used for grouping in the report

------------------------------------------------------------------------

### 4.2 Organization Mapping (External SSV)

Provided via CLI:

    --org-map /path/to/openrail_committers.ssv

Format (semicolon-separated):

    Committer;Projects;Organization
    Name <email@example.com>;osrd,liblrs;DB InfraGO

Rules:

-   Primary key is normalized email extracted from `<...>`
-   Projects is a comma-separated list of project IDs
-   Mapping applies only to listed projects
-   Duplicate conflicting entries are an error
-   Unknown emails default to `Unknown`

No committer data from this file is ever written to outputs.

------------------------------------------------------------------------

### 4.3 Alias Mapping (External SSV)

Provided via:

    --aliases /path/to/openrail_aliases.ssv

Purpose: unify multiple emails belonging to the same person.

Format:

    PersonKey;Emails;Notes
    p000001;dev@corp.example,dev@users.noreply.github.com;corp+github
    p000002;first.last@operator.eu,flast@operator.eu;

Rules:

-   `PersonKey` is arbitrary, stable, non-identifying
-   Emails are comma-separated
-   An email may appear only once
-   File is optional

------------------------------------------------------------------------

### 4.4 Report Configuration (`report.yml`)

``` yaml
report:
  title: "OpenRail Metrics Report"
  quarter: "2025Q4"
  from: 2025-12-01
  to: 2026-02-28
  issue_date: 2026-03-15
```

------------------------------------------------------------------------

## 5. Repository Handling

Repositories are cloned as bare mirrors into:

    repos-cache/<repo>.git

Initial clone:

    git clone --mirror <url>

Update:

    git fetch --prune

No working checkouts required.

------------------------------------------------------------------------

## 6. Commit Extraction

For each repository:

    git log --since <from> --until <to> --pretty=format:...

Extract:

-   Commit date (UTC)
-   Committer email
-   Commit hash
-   Parent count (to detect merges)

Default behavior:

-   Exclude bots
-   Exclude merge commits (configurable)

------------------------------------------------------------------------

## 7. Identity Normalization

### 7.1 Email Normalization

-   Lowercase
-   Trim whitespace

### 7.2 Canonical Identity

If alias mapping matches:

    canonical_identity = "person:" + PersonKey

Otherwise:

    canonical_identity = "email:" + normalized_email

------------------------------------------------------------------------

## 8. Pseudonymous Committer ID

No salt is used.

    committer_id = first_12_chars(sha256(canonical_identity))

Properties:

-   Deterministic across runs
-   Not reversible in practice
-   Never exposes email
-   Stable across quarters

Raw email is never written to output files.

------------------------------------------------------------------------

## 9. Organization Attribution

Organization is determined by:

1.  Matching normalized email in org mapping
2.  Ensuring project scope matches
3.  Defaulting to `Unknown`

------------------------------------------------------------------------

## 10. Internal Commit Event Model

    date
    project_id
    repo_id
    org
    committer_id
    is_bot
    is_merge

No email or name stored.

------------------------------------------------------------------------

## 11. Aggregation

### Per Project

-   Total human commits
-   Unique committers
-   Distinct contributing organizations
-   Commits per month
-   Commits per organization

### OpenRail-Wide

-   Total commits
-   Total active committers
-   Total contributing organizations
-   Monthly trend

------------------------------------------------------------------------

## 12. Output Structure

    out/
      raw/
        commits.ssv
      tables/
        project_summary.csv
        org_summary.csv
      data/
        monthly_trends.yaml
        org_distribution.yaml
      report.md
      report.pdf

All files contain only aggregated data and pseudonymous IDs.

------------------------------------------------------------------------

## 13. CLI Structure

Primary command:

    openrail-metrics all   --projects projects.yml   --report report.yml   --org-map /path/org_map.ssv   --aliases /path/aliases.ssv

Subcommands:

    sync
    extract
    aggregate
    render
    all

------------------------------------------------------------------------

## 14. Validation Rules

-   Duplicate alias email → error
-   Conflicting org mappings → error
-   Unknown project ID in org mapping → warning
-   Missing org mapping → all commits assigned to `Unknown`

------------------------------------------------------------------------

## 15. Reproducibility

Each run writes:

    out/meta/run.yml

Containing:

-   Reporting window
-   Tool version
-   Repository HEAD SHAs
-   Config file hashes

Ensures traceability.

------------------------------------------------------------------------

## 16. Privacy Model

The tool:

-   Reads email addresses from git and mapping files
-   Uses them only in memory
-   Writes no emails or names to outputs
-   Publishes only aggregated statistics
-   Uses deterministic pseudonymous IDs
-   Does not use a salt

This minimizes personal data while keeping the implementation simple.
