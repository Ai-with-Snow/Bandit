# Communications Protocol

HQ communication balances calm leadership with decisive routing.

## Channels
| Channel | Purpose | Owner | Notes |
| --- | --- | --- | --- |
| Command Deck Updates | Broadcast daily status + blockers | Bandit | Mirror highlights in `notes/project.log` |
| Observatory Digest | Share intel and KPIs | Data Agent | Pulled twice daily |
| Labs Dispatch | Request experiments + prototypes | Labs Lead | Reference `spaces/labs.md` |
| Executive Ping | Direct line to Goddexx Snow | Bandit | Only for escalations or approvals |

## Escalation Ladder
1. Attempt resolution within owning agent.
2. Loop in Bandit for cross-team support.
3. Ping Master Agent via develop branch PR.
4. Escalate to Goddexx Snow only when timeline, compliance, or reputation is at risk.

## Comms Tone Checklist
- Lead with context; cite path (`app/`, `notes/`, `docs/`) for every mention.
- Keep UI copy aligned with `#0A2E37` calm energy; highlight urgent cues with `#F58720`.
- Close loops by recording outcomes in `logs/setup-log.md`.

## Intake Linkage
All inbound directives are logged in `operations/intake.md` and then mirrored to Command Deck. Include:
- Directive summary.
- Origin (voice note, doc, meeting).
- Owner + due date.
- Status + next checkpoint.
