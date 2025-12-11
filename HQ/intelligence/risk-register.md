# Risk Register

| ID | Risk | Impact | Likelihood | Owner | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | HQ docs drift from repo structure | High | Medium | Bandit | Sync updates to `config/settings.json`, mirror changes in `notes/project.log` | Monitoring |
| R-002 | Compliance gaps when launching new portals | High | Medium | Compliance Agent | Run checklist before launch, maintain `operations/checklists.md` | Monitoring |
| R-003 | Automation scripts fail silently | Medium | Medium | Core Agent | Add logging + alerts; test `scripts/` changes via CI | Planned fix |
| R-004 | Brand tone inconsistent across agents | Medium | Medium | Design + Content Agents | Centralize tokens + tone cues in `intelligence/brand-brief.md` | Monitoring |
| R-005 | Missed rituals causing backlog buildup | Medium | Low | Bandit | Use ritual reminders + `logs/ritual-journal.md` to document catches | Monitoring |

## Process
1. Review at every Compliance Sync.
2. Update status + mitigation notes as actions occur.
3. When a risk is resolved, move it to a “Closed” section with lesson learned.
