# Bandit AI Capabilities — Integration Manifest

> **For AI Strategic Planning**: This document describes all available integrations and automations Bandit can execute. Use this as context for generating automation strategies, workflow designs, and task orchestration.

---

## 🤖 What is Bandit?

Bandit is an autonomous AI agent powered by **Gemini 3.0** (Flash & Pro) that serves as the operational backbone for **LMSIFY** — a somatic wellness practice run by Goddexx Snow.

**Core Mission**: Automate business operations while protecting Snow's presence for high-touch client work.

---

## ✅ Validated API Integrations

All APIs below have been tested and are **fully operational** as of January 2, 2026.

### Google Workspace Suite

| API | Capability | Use Cases |
| :--- | :--- | :--- |
| **Gmail** | Read inbox, send emails | Aftercare emails, inquiry responses, newsletters |
| **Calendar** | Read/write events | Session scheduling, event sync with Notion |
| **Sheets** | Create/read/write spreadsheets | Financial reports, P&L tracking, client lists |
| **Tasks** | Create/manage tasks | Follow-up reminders, check-in tasks |
| **Drive** | List/manage files | Session recordings, resource storage |
| **Docs** | Create/edit documents | Session notes, contracts, intake docs |
| **Slides** | Create presentations | PAUSE Portal decks, workshop materials |
| **Forms** | Read form responses | Intake forms, feedback surveys |
| **Meet** | Schedule meetings | Virtual session links |
| **Apps Script** | Custom triggers | Advanced automation hooks |

### Notion API

| Capability | Databases Available |
| :--- | :--- |
| Create/update pages | Sessions, Clients, Leads, Events, Financials |
| Query with filters | Find dormant clients, unpaid sessions, etc. |
| Update properties | Mark sessions complete, toggle checkboxes |
| Sync with external services | Calendar, email triggers |

**Database IDs (for automation scripts):**
- Sessions: `5692635812d442baa7ab1d46b2164687`
- Clients: `d82da27be3bb42a585d011d8218eb08c`
- Events: `f42e7991dce74e6aa96149056fd6e2ab`
- Leads: `72d9f077668c48b6aea5ac84c5f816aa`
- Financials: `27bf2bb64dbc4f20b83f06d3f74f775a`

---

## 🔄 Available Automation Flows

### Session & Client Management
- **New Session Booked** → Create Notion entry + Google Calendar event + Send intake form
- **Session Completed** → Draft aftercare email + Log payment + Create follow-up task
- **Client Dormant 60+ days** → Generate re-engagement email draft
- **VIP Threshold Met** → Update client status + Send thank-you

### Financial Operations
- **Invoice Received** → Log to Financials DB + Auto-categorize
- **Quarterly Tax Reminder** → Pull totals + Email summary (Jan 15, Apr 15, Jun 15, Sep 15)
- **Monthly P&L Export** → Generate Google Sheet with income/expense breakdown

### Content & Outreach
- **Client Inquiry Email** → Create Lead in Notion + Draft response
- **Newsletter Draft** → Pull upcoming events + Generate copy in brand voice
- **PAUSE Portal Event** → Create Slides deck + Calendar event + Ticket tracker

---

## 🧠 Bandit's Reasoning Capabilities

| Mode | Model | Use Case |
| :--- | :--- | :--- |
| **Instant** | Gemini 3 Flash | Quick queries, simple tasks |
| **Auto** | Hybrid routing | Balanced complexity |
| **Thinking** | Gemini 3 Pro | Deep reasoning, strategy, multi-step planning |

**Special Abilities:**
- **RAG Knowledge Base**: 55+ HQ documents indexed in Vertex AI Search
- **Code Execution**: Python sandbox for calculations
- **Web Search**: Real-time grounding with Google Search
- **Deep Research**: Async research mode for complex queries

---

## 📁 Key Files for Automation

| File | Purpose |
| :--- | :--- |
| `scripts/notion_flows/calendar_sync.py` | Push/pull Notion ↔ Google Calendar |
| `scripts/notion_flows/aftercare_email.py` | Send aftercare emails on session complete |
| `scripts/notion_flows/test_google_apis.py` | Validate all Google API connections |
| `HQ/memory/lmsify_business_automations.md` | Full automation blueprint |
| `HQ/memory/lmsify_platform_language.md` | Platform-safe language for social content |

---

## 🎯 Strategic Planning Prompt

Use this as context for generating automation strategies:

> "Given Bandit's capabilities above, propose a workflow that [DESCRIBE GOAL]. Consider which APIs to use, what triggers make sense, and how to minimize manual intervention while maintaining the high-touch, consent-centered brand voice of LMSIFY."

### Example Goals to Strategize:
1. Automate the entire client intake-to-first-session flow
2. Generate monthly financial reports and tax set-aside reminders
3. Create a re-engagement campaign for dormant clients
4. Build a content calendar with platform-safe captions
5. Sync Calendly bookings to Notion with automatic intake emails

---

## 🔐 Authentication Status

| Service | Status | Token Location |
| :--- | :--- | :--- |
| Notion API | ✅ Active | `.env.local` |
| Google APIs | ✅ Active | `google_token.pickle` |
| GCP Project | ✅ Active | `project-5f169828-6f8d-450b-923` |

---

*Last Updated: January 2, 2026 @ 3:00 AM EST*
*Owner: Goddexx Snow | Maintained by Bandit (Antigravity)*
