# Organization Mapping File Format

The organization mapping file is a semicolon-separated values (SSV) file that maps committer email addresses to their organizational affiliations.

## Format

```
Committer;Projects;Organization
Name <email@example.com>;project1,project2;Organization Name
another@example.com;project3;Another Org
```

## Fields

1. **Committer**: Either `Name <email@example.com>` or just `email@example.com`
2. **Projects**: Comma-separated list of project IDs (informational only, not used for attribution)
3. **Organization**: Organization name (e.g., SNCF, DB, SBB, Bot, Unknown)

## Rules

- Header line is required: `Committer;Projects;Organization`
- Email addresses are case-insensitive
- Entries are sorted by name (case-insensitive), then by email
- No spaces after commas in project lists
- Attribution is project-agnostic: email → organization mapping only
- Unknown emails are attributed to "Unknown" organization

## Maintenance

Use the `update-org-map` command to automatically:
- Add new committers found in repositories (with org set to "Unknown")
- Update project lists for existing committers
- Maintain alphabetical sorting

```bash
openrail-metrics update-org-map --org-map path/to/mapping.ssv
```

Manually check the correct mapping to organizations and add missing organizations for entries marked as Unknown.
