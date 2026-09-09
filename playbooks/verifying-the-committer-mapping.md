# Verifying the committer mapping

Before generating a quarterly report, confirm the committer mapping is complete and consistent. This is the check behind step 4 of the "Creating a Quarterly Report" procedure in the README. Run it after syncing the repositories.

## The three checks

1. **Are any contributors missing?** Copy the mapping file and run `org-map update` against the copy, so nothing real changes:

   ```bash
   cp /path/to/openrail_committers.ssv /tmp/probe.ssv
   uv run openrail-metrics org-map update --org-map /tmp/probe.ssv
   ```

   "New entries: 0" means everyone who committed on the counted branches is already mapped. Any listed names are missing and must be added to the real file.

2. **Is the mapping internally consistent?** Run `extract`:

   ```bash
   uv run openrail-metrics extract --org-map /path/to/openrail_committers.ssv
   ```

   Extract enforces that all identities sharing one canonical email have the same organization. If two entries for the same person disagree, it stops with a conflict listing. Completing without error means there are no contradictions.

3. **Does every contributor have a real organization?** Confirm no entry is still `Unknown`:

   ```bash
   uv run openrail-metrics org-map show --org-map /path/to/openrail_committers.ssv
   ```

   The Unresolved section lists any `Unknown` rows. `Unknown` means a contributor was added automatically but nobody has yet assigned their organization.

All three passing (no new people, no conflicts, no Unknowns) means the mapping is ready.

## Branch-scope caveat

Only check the branches the report actually counts. The report counts commits from each repository's configured branch only (see `config/projects.yml`; for example OSRD's `dev`, most others `main`), not every branch. `org-map update` and `extract` already restrict themselves to those branches.

If you instead sweep every branch by hand (`git log --all`), you will find many committers who are not in the mapping and conclude it is broken. They are on feature or pull-request branches the report never counts, so they correctly do not appear. Checking against all branches chases contributors the report will never include. Match the report's branch scope, or the completeness check produces false alarms.

The reasoning behind counting only these branches is recorded in `docs/architecture.md` (metrics calculation) and rendered for readers in the report's methodology appendix.
