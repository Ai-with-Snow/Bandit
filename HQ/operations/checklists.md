# HQ Checklists

Operational checklists for each recurring ritual. Keep this file open during live sessions.

## Dawn Systems Check
- [ ] Review `notes/project.log` for overnight commits or structural changes.
- [ ] Run `git status -sb` to confirm clean working tree or capture diffs.
- [ ] Inspect open directives in `operations/intake.md`; flag overdue items.
- [ ] Verify `config/settings.json` brand + navigation data; sync if HQ updates occurred.
- [ ] Post a short summary to Command Deck (Notes + Slack/voice as needed).

## Pulse Review
- [ ] Summarize key Observatory metrics (blog, transcripts, analytics).
- [ ] Collect updates from each active agent owner listed in `operations/routing-matrix.md`.
- [ ] Record blockers + decisions in `logs/ritual-journal.md`.
- [ ] Adjust `intelligence/initiative-map.md` statuses.

## Nightly Close
- [ ] Ensure `notes/agents/bandit.md` captures the day’s highlights + next steps.
- [ ] Move completed directives from `operations/intake.md` to the Completed section.
- [ ] Archive any new transcripts or transcripts proxies to `notes/transcripts/`.
- [ ] Update `logs/setup-log.md` with infrastructure or HQ changes.

## Compliance Sync
- [ ] Review `intelligence/risk-register.md` entries.
- [ ] Check for new integrations (see `docs/integrations.md`) or secrets (.env*).
- [ ] Capture action items with owners + due dates.

## Portal Launch Prep
- [ ] Confirm assets ready in `public/brand/`.
- [ ] Validate UI flows in `app/(feature)` or equivalents.
- [ ] Run `npm run lint` and `npm run build`.
- [ ] Draft release blurb referencing brand brief.
- [ ] Schedule Observatory follow-up to measure impact.
