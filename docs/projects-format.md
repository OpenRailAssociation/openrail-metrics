# Projects Configuration Specification

## File Format

YAML file defining OpenRail projects and their associated repositories.

## Schema

```yaml
projects:
  - id: <project-id>
    name: <display-name>
    stage: <lifecycle-stage>
    repos:
      - <git-url>
      - <git-url>
```

## Fields

### `projects` (required)
Array of project definitions.

### `id` (required)
- Unique project identifier
- Lowercase, alphanumeric with hyphens
- Used in org mapping file to scope attributions
- Example: `osrd`, `liblrs`, `rolling-stock-db`

### `name` (required)
- Human-readable project name
- Used in report output
- Example: `OSRD`, `libLRS`, `Rolling Stock Database`

### `stage` (required)
- Project lifecycle stage
- Used for grouping in reports
- Valid values: `incubation`, `production`, `archived`

### `repos` (required)
- Array of Git repository URLs
- Must be publicly accessible or credentials configured
- HTTPS or SSH URLs supported
- Example: `https://github.com/OpenRailAssociation/osrd.git`

## Example

```yaml
projects:
  - id: osrd
    name: OSRD
    stage: production
    repos:
      - https://github.com/OpenRailAssociation/osrd.git

  - id: liblrs
    name: libLRS
    stage: incubation
    repos:
      - https://github.com/OpenRailAssociation/liblrs.git
      - https://github.com/OpenRailAssociation/liblrs-python.git

  - id: rolling-stock-db
    name: Rolling Stock Database
    stage: incubation
    repos:
      - https://github.com/OpenRailAssociation/rolling-stock-database.git
```

## Validation Rules

- All `id` values must be unique
- At least one repository per project
- No duplicate repository URLs across projects
- Repository URLs must be valid Git URLs
