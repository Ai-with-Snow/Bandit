# LMSIFY Headquarters (Bandit Ops)

The HQ is the always-on ops deck for **Let Me Say It For You (LMSIFY)**. It keeps decisions, rituals, and routing maps in one calm control center inspired by the brand’s mantra: **Stillness is the vibe. Breath is the anchor.**

## Architecture
- **Command Deck** — monitors portals, releases, and team status; ties into develop/main for Git hygiene.
- **Observatory** — listens to audience signals, transcripts, and analytics before routing ideas to delivery teams.
- **Labs** — experiments with new flows, automations, and assistants under `src/agents` or `scripts/`.
- **Sanctum** — recovery nook with P.A.U.S.E prompts to make sure we protect creative energy before go-lives.

Each room has its own dossier inside `spaces/` that spells out layout, tools, and owners.

## Ritual Stack
1. **Dawn Systems Check (08:00 ET)** — scan project log, open PRs, and outstanding directives; update `notes/agents/bandit.md`.
2. **Pulse Review (13:00 ET)** — sync with compliance + design + marketing to unblock current initiatives.
3. **Nightly Close (22:00 ET)** — archive transcripts, push summaries to HQ log, and prep next-day TODOs.
4. **P.A.U.S.E reset** — between intense sessions, walk through Patience + Accountability + Unite Self + Experience cards stored in `spaces/sanctum.md`.

## Intake & Routing
- Capture directives in `operations/intake.md`.
- Route to the matching downstream agent (core, uiux, compliance, etc.) and capture the linkage in `operations/comms.md`.
- Surface any blockers or escalations back to the Master Agent via develop → main protocol.

## Activation Checklist
- [ ] Confirm bandit profile and HQ layout (this folder) are synced with `config/settings.json` brand data.
- [ ] Add at least one initiative to `intelligence/initiative-map.md`.
- [ ] Publish ritual adherence notes to `logs/setup-log.md`.
- [ ] Notify Goddexx Snow when new rooms or automations go live.

## Current Priorities
1. Translate upcoming HQ docs from Goddexx Snow into actionable routes.
2. Draft automation hooks for command palette + transcripts pipeline.
3. Prepare compliance-ready intake template for new portals.
