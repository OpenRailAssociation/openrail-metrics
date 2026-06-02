# OpenRail Metrics

This repo contains the tool we use to create the quarterly OpenRail metrics report and the resulting reports.

## Creating a Quarterly Report

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Git
- Pandoc (for PDF generation)
- WeasyPrint (for PDF generation)

### Procedure

1. **Update `config/report.yml`** with the new quarter's parameters:

   ```yaml
   report:
     title: "OpenRail Metrics Report"
     quarter: "2026Q2"
     from: 2026-03-01
     to: 2026-05-31
     issue_date: 2026-06-15
   ```

   Quarters are offset from calendar quarters (Q1 = Dec-Feb, Q2 = Mar-May, Q3 = Jun-Aug, Q4 = Sep-Nov) so the report can be generated in the month after the period ends.

2. **Review the official project list** in the [technical-committee repo](https://github.com/OpenRailAssociation/technical-committee/blob/main/docs/joining/projects.md). Compare against the public repos in the GitHub org (`gh repo list OpenRailAssociation --visibility=public`) and update the TC list if repos were added, archived, or removed. Submit a PR for any changes.

3. **Update `config/projects.yml`** to match the official project list. Add new repos, remove archived ones, update stages for graduated projects.

4. **Update the organization mapping** to include any new committers:

   ```bash
   # Sync repos first (needed to discover new committers)
   uv run openrail-metrics sync

   # Update the mapping file with new emails
   uv run openrail-metrics org-map update \
     --org-map /path/to/openrail_committers.ssv
   ```

   Review the output. For each new "Unknown" entry, fill in the correct organization in the SSV file. Then consolidate duplicate identities and sort:

   ```bash
   # Find and fix duplicate identities (same person, different emails)
   uv run openrail-metrics org-map find-duplicates \
     --org-map /path/to/openrail_committers.ssv --apply

   # Sort the file by canonical email
   uv run openrail-metrics org-map clean \
     --org-map /path/to/openrail_committers.ssv
   ```

5. **Write the executive summary** in `config/intro.md`. This is a short interpretive text that appears before the data sections. Update it each quarter to highlight trends and notable changes.

6. **Run the pipeline**:

   ```bash
   uv run openrail-metrics all \
     --org-map /path/to/openrail_committers.ssv
   ```

   This syncs repositories, extracts commits, generates graphics, renders markdown, and produces the PDF.

7. **Review the output** in `out/` (report.md, report.pdf, graphics/).

8. **Copy the final PDF** to `reports/`:

   ```bash
   cp out/report.pdf reports/openrail-metrics-2026Q2.pdf
   ```

9. **Commit and tag**:

   ```bash
   git add config/ reports/
   git commit -m "Add OpenRail Metrics Report 2026Q2"
   git tag report-2026Q2
   ```

   The tag marks the exact config state used to produce the report. Previous configs can be recovered via their tags (e.g., `git show report-2026Q1:config/report.yml`).

## Report Structure

The overall structure of the generated report is defined in `templates/report.md.template`. The structure of the project section is defined in `templates/project.md.template`.

## Configuration Files

### config/projects.yml

Defines OpenRail projects and their repositories. See the file for the full schema.

### config/report.yml

Defines the reporting period. Updated in place for each new report (previous values recoverable via git tags).

### Organization Mapping (SSV)

External file mapping committers to organizations. Format defined in `docs/org-mapping-format.md`.

## Data Privacy

- Email addresses are never written to output files
- Committer identities are pseudonymized using SHA256 hashing
- Only aggregated statistics are published
- Organization mapping is kept in external files

## Development

```bash
uv run pytest tests/ -v
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for detailed implementation notes.

See [docs/design.md](docs/design.md) for the original design specification.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Code of Conduct

We follow the [code of conduct](CODE_OF_CONDUCT.md) of the OpenRail Association.
