# Directive Intake

Template for capturing every instruction headed to HQ.

## Fields
- **ID** — timestamp + short slug (ex: `2025-11-20-hq-room-grid`).
- **Source** — Goddexx Snow, agent brief, transcript, etc.
- **Summary** — single-sentence description.
- **Owner** — agent responsible.
- **Due** — target date/time.
- **Status** — queued / in-progress / blocked / done.
- **Artifacts** — paths (e.g., `agents/master/AGENT.md`, `/mnt/c/Users/...`).

## Active Queue
| ID | Summary | Owner | Due | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| 2025-11-20-hq-setup | Build HQ structure in Documents | Bandit | 2025-11-20 | In Progress | Includes spaces + operations docs |
| 2025-11-20-igloo-build | Apply Irie Igloo category/role map across Discord | Ice Wire | 2025-11-22 | Queued | See `HQ/community/bandit-irie-igloo-server-map.md` |
| 2025-11-20-igloo-copy | Pin welcome, Igloo Code, Melt Spot & Circle copy | Ice Wire | 2025-11-21 | Queued | Use `HQ/community/bandit-irie-igloo-copy.md` |
| 2025-11-20-igloo-broadcast | Configure Celestial Radio channels + FredBoat DJ stack | Ice Wire | 2025-11-22 | Queued | `HQ/community/bandit-irie-igloo-broadcast.md` |
| 2025-11-20-mr-krabz-assets | Produce visual itinerary, ticket PDFs + Shopify event wiring | Ice Wire | 2025-11-23 | Queued | `HQ/community/bandit-feelin-it-mr-krabz.md` |
| 2025-11-20-pause-vetting | Export shareable + fillable vetting PDF and store canonically | Ice Wire | 2025-11-22 | Queued | `HQ/community/bandit-pause-portal-vetting.md` |
| 2025-11-20-pause-emails | Load activation + vetting templates into ESP automation | Ice Wire | 2025-11-24 | Queued | `HQ/community/bandit-pause-portal-emails.md` |
| 2025-11-20-pleasher-kit | Convert PleasHer outline into facilitator deck + workbook | Ice Wire | 2025-11-25 | Queued | `HQ/community/bandit-pleasher-workshop.md` |
| 2025-11-20-velvet-assets | Build Velvet Evenings one-pager + Shopify tier setup + flyer exports | Ice Wire | 2025-11-27 | Queued | `HQ/community/bandit-velvet-evenings.md` |
| 2025-11-20-million-intake | Provide revenue metrics for sensory, portal, OF lanes (avg sessions, Pause Portal attendance, OF revenue) | Goddexx Snow → Bandit | 2025-11-22 | Blocked (needs data) | `HQ/community/million-dollar-upscale-intake.md` |
| 2025-11-20-streamer-metrics | Deliver streaming KPI baselines (session counts, attendance, revenue) | Goddexx Snow → Bandit | 2025-11-22 | Blocked (needs data) | Feeds `community/streamer-focus.md` |
| 2025-11-20-branch-graphic | Plan branch graphic + repo branch `feature/hq-branch-graphic` | Ice Wire | 2025-11-21 | Queued | Output to `community/streamer-focus.md` + design briefs |
| 2025-11-20-stream-assets | Kick off banners/overlays/logo production | Bandit + Design + Ice Wire | 2025-11-25 | Queued | Asset list in `community/streamer-focus.md` |
| 2025-11-20-revenue-model | Model revenue once metrics land | Ice Wire | 2025-11-26 | Pending | Depends on `streamer-metrics` completion |
| 2025-11-20-disclaimer-page | Publish poetic + formal disclaimers on LMSIFY site + footer | Bandit + Compliance | 2025-11-23 | Queued | `HQ/community/website-disclaimer.md` |
| 2025-11-20-disclaimer-review | Legal + accessibility review for disclaimer copy | Compliance Agent | 2025-11-22 | Queued | Same doc |
| 2025-11-20-flyer-brief | Provide flyer template brief answers (division, purpose, vibe, output) | Goddexx Snow | ASAP | Blocked (needs owner input) | `HQ/community/website-disclaimer.md` |
| 2025-11-20-flyer-templates | Produce flyer template batch once brief ready | Ice Wire + Design Agent | Pending brief | Pending | Depends on `flyer-brief` |

## Workflow
1. Capture directive inside this file immediately.
2. Create supporting doc/branch; reference it here and in Command Deck updates.
3. Update status at every ritual checkpoint.
4. When done, move the row to the Completed section and log summary in `logs/setup-log.md` + `notes/agents/bandit.md`.

## Completed
| ID | Summary | Owner | Completed | Artifacts |
| --- | --- | --- | --- | --- |
| 2025-11-20-streamer-doc | Convert Notion “Streamer focus” into HQ dossier | Bandit | 2025-11-20 | `HQ/community/streamer-focus.md` |
