# Routing Matrix

Maps each type of HQ request to the agent or team responsible. Use this list when triaging new directives in `operations/intake.md`.

| Request Type | Primary Owner | Backup Owner | Notes |
| --- | --- | --- | --- |
| Repo structure / automation | Core Agent | Master Agent | Reference `agents/master/AGENT.md` + `config/settings.json` |
| UI polish / component refactors | UIUX Agent | Design Agent | Tie into `app/` feature folders; cite shadcn/Tailwind usage |
| Brand / visual storytelling | Design Agent | Visual Agent | Pull from `public/brand/` + `styles/globals.css` tokens |
| CSS tokens + theming | CSS Agent | Core Agent | Guard `#0A2E37` palette alignment |
| Content / copywriting | Content Agent | Marketing Agent | Reference tone from `intelligence/brand-brief.md` |
| Marketing launches | Marketing Agent | Content Agent | Coordinate assets + analytics |
| Compliance / accessibility | Compliance Agent | Core Agent | Log checkpoints + remediation |
| Builds / QA / pipelines | Build Agent | Core Agent | Run `npm run lint`, `npm run build`, future tests |
| Data + analytics | Data Agent | Marketing Agent | Use Observatory dashboards |
| Audio / sonic assets | Music Agent | Design Agent | Reference `notes/transcripts/` for narrative cues |
| Navigation / IA | Navigation Agent | UIUX Agent | Update `config/navigation` and relevant pages |
| HQ automation + orchestration | Bandit | Core Agent | Lives in `scripts/`, `src/agents/`, Documents/HQ |

## Usage
1. When a directive lands, tag it with a request type in `operations/intake.md`.
2. Notify the primary owner via the Communications Protocol.
3. If the owner is unavailable, escalate to the listed backup and log the swap in `logs/ritual-journal.md`.
4. Update this matrix when new agents join or roles shift; reflect the change inside `config/settings.json` if relevant.
