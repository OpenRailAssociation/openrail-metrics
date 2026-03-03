# Organization Mapping File Format

The organization mapping file is a semicolon-separated values (SSV) file that maps committer email addresses to their organizational affiliations and resolves identity aliases.

## Format

```
Committer;Projects;Canonical;Organization
Name <email@example.com>;project1,project2;email@example.com;Organization Name
another@example.com;project3;another@example.com;Another Org
Name <alias@example.com>;project1;email@example.com;Organization Name
```

## Fields

1. **Committer**: Either `Name <email@example.com>` or just `email@example.com`
2. **Projects**: Comma-separated list of project IDs (informational, helps with manual org assignment)
3. **Canonical**: Canonical email address for this person (used for identity resolution)
4. **Organization**: Organization name (e.g., SNCF, DB, SBB, Bot, Unknown)

## Identity Resolution

The **Canonical** column groups multiple email addresses that belong to the same person:

```
Committer;Projects;Canonical;Organization
Jane Smith <jane@example.com>;netzgrafik-editor;jane@example.com;CompanyA
Jane Smith <jane.personal@example.com>;netzgrafik-editor;jane@example.com;CompanyA
u123456 <jane@example.com>;netzgrafik-editor;jane@example.com;CompanyA
```

All three entries have the same canonical email, so they are treated as the same person:
- Same pseudonymized contributor ID in metrics
- Commits from all three identities count toward the same person
- Organization is looked up via the canonical email

### Rationale

**Why not separate files?**
- Need to see project context when assigning organizations
- Single file keeps all information together for manual review
- Sorting by canonical groups related entries visibly

**Why canonical column instead of separate identity map?**
- Avoids duplicating organization information
- Makes grouping explicit and visible in the same file
- Prevents conflicting org assignments (validated at runtime)

**Why not just use email matching?**
- Same person may use different emails (work vs personal, GitHub noreply, etc.)
- Same email may appear with different names (proper name vs username)
- Explicit canonical column makes identity resolution transparent

## Rules

1. **Canonical defaults to email**: When `update-org-map` adds new entries, canonical is set to the email from that row
2. **Sorting**: Entries are sorted by canonical email (case-insensitive), then by name - this groups the same person together
3. **No spaces in project lists**: Projects are comma-separated without spaces (e.g., `osrd,liblrs`)
4. **Org consistency**: All entries with the same canonical email MUST have the same organization (validated by extract command)
5. **Email normalization**: Emails are case-insensitive for matching

## Validation

The `extract` command validates:
- All entries with the same canonical email have the same organization
- If conflicts exist, the command fails with an error listing the conflicts
- Human must resolve conflicts before metrics can be generated

## Maintenance

Use the `update-org-map` command to automatically:
- Add new committers found in repositories (with org set to "Unknown", canonical set to email)
- Update project lists for existing committers
- Maintain alphabetical sorting by canonical email

```bash
openrail-metrics update-org-map --org-map path/to/mapping.ssv
```

After running `update-org-map`, manually review:
1. New entries (org = "Unknown") - assign correct organization
2. Potential aliases - set canonical email to group identities
3. Ensure all entries with same canonical have same org

Manually check the correct mapping to organizations and add missing organizations for entries marked as Unknown.
