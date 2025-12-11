# Command Deck

Mission control for LMSIFY HQ. The deck keeps every runway visible at a glance, mixing telemetry from repo automation, conversations, and the brand’s P.A.U.S.E cues.

## Zones
- **Ops Rail** — mirrors `notes/project.log`, feature branches, and deployment readiness. Owners: Bandit + build agent.
- **Signal Wall** — rotates through transcripts, blog stats, and marketing KPIs. Owners: data + marketing agents.
- **Escalation Well** — contains compliance alerts, risk register hooks, and the hotline back to Goddexx Snow.

## Tools
- Next.js dashboards rendered from `app/admin/logs` and `/blog` metrics.
- CLI + scripts from `src/agents/master_agent.py` for automation kicks.
- Manual checklists (see `logs/setup-log.md`) for when automation is still pending.

## Operating Notes
1. Keep deck screens tinted with `#0A2E37` backgrounds, highlight urgent nodes with the accent `#F58720`.
2. If an agent misses a ritual, flag it in the Escalation Well and page compliance for backup.
3. Archive snapshots of the deck weekly to `notes/transcripts/` for auditability.
