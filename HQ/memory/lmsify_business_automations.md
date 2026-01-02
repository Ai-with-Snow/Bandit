# LMSIFY Business Automation Blueprint (Somatic + Mogul Flow)

> A clean, Notion-first operating system for Snow's wellness practice operations.

---

## 🧘 Design Principles

You are building a *high-touch somatic practice* that runs with *low-friction systems*.

- Automations should **protect your presence**, not add complexity.
- Every flow should end in a **clear next action** (for you or the client).
- Your data model should reflect the real lifecycle: **Lead → Client → Session → Follow-up → Revenue**.
- Keep "magic" client-facing, and keep "mechanics" internal.
- Track what matters: **sessions delivered, money collected, taxes set aside, clients retained**.
- Default to *simple triggers* (status changes, form submits) over fragile multi-step chains.
- Build in *care*: aftercare, re-engagement, VIP moments are revenue *and* relationship.

---

## 🗄️ Core Databases (Live)

| Database | Notion ID |
| :--- | :--- |
| **Blueprint** | `b72b8f4cae6d4bf59a5a26dd6e883c8d` |
| **Clients** | `d82da27be3bb42a585d011d8218eb08c` |
| **Sessions** | `5692635812d442baa7ab1d46b2164687` |
| **Leads** | `72d9f077668c48b6aea5ac84c5f816aa` |
| **Events** | `f42e7991dce74e6aa96149056fd6e2ab` |
| **Financials** | `27bf2bb64dbc4f20b83f06d3f74f775a` |

---

## 🗓️ Session & Event Management

### New Session Booked
- **Trigger:** Calendly/Acuity booking confirmed (webhook)
- **Actions:**
  - Create/Update Client in Notion
  - Create Session entry linked to Client
  - Push to Google Calendar
  - Send intake form automatically
- **Tools:** Webhook → Notion API + Google Calendar API + email/intake integration

### Session Completed
- **Trigger:** Session status changed to **Completed**
- **Actions:**
  - Draft and send aftercare email (brand voice, somatic tone)
  - Log payment status and method
  - Prompt follow-up booking (gentle CTA)
  - Set a "check-in" task for 3–7 days later
- **Tools:** Notion + Gmail (or email tool) + simple scheduled reminders

### PAUSE Portal Event Created (Workshop / Group / Offering)
- **Trigger:** New Event page created in Notion
- **Actions:**
  - Push event to Google Calendar
  - Generate platform-safe caption + hashtag set
  - Create RSVP / ticket tracker
  - Optional: auto-create a run-of-show checklist
- **Tools:** Notion + Calendar sync + content generator

---

## 💰 Financials & Taxes

### Invoice Received / Sent
- **Trigger:** Stripe/Square email OR manual entry
- **Actions:**
  - Log to Financials DB
  - Auto-tag: Session, Workshop, Merch
  - Update monthly + quarterly totals
- **Tools:** Gmail parsing + Notion database logic

### Quarterly Tax Reminder
- **Trigger:** Scheduled dates (Jan 15, Apr 15, Jun 15, Sep 15)
- **Actions:**
  - Pull quarterly income + expense totals
  - Generate a simple summary (gross, net, estimated set-aside)
  - Send reminder email to you with numbers included
- **Tools:** Scheduler + Notion query + email send

### Expense Logged
- **Trigger:** New Expense page created
- **Actions:**
  - Auto-categorize (Rent, Supplies, Travel, Education, Equipment)
  - Update quarterly P&L rollup
- **Tools:** Notion-native + optional enrichment logic

---

## 📧 Gmail & Outreach

### Client Inquiry Email
- **Trigger:** Gmail label "LMSIFY Inquiry"
- **Actions:**
  - Create Lead entry
  - Draft response using brand voice (warm, boundaried, clear next steps)
  - Optionally suggest 2–3 booking options and intake link
- **Tools:** Gmail + Notion + draft generator

### Aftercare Email Send
- **Trigger:** Session → Completed
- **Actions:**
  - Send aftercare note
  - Log "Aftercare Sent" date
  - If no reply in 7 days, create a gentle follow-up task
- **Tools:** Gmail + Notion

### Newsletter Draft (Soft Power Marketing)
- **Trigger:** Manual button or monthly schedule
- **Actions:**
  - Pull upcoming events + recent themes from sessions (anonymized)
  - Generate draft copy in your tone
  - Export to Mailchimp (or keep in Notion to paste)
- **Tools:** Notion + content generator

---

## 🔄 Google Calendar Sync (Two-way clarity)

### Push: Notion → GCal
- **Trigger:** New Session/Event created in Notion
- **Actions:** Create Calendar event with title, time, location, and client name (if appropriate)

### Pull: GCal → Notion
- **Trigger:** Calendly/Acuity booking confirmed
- **Actions:** Create Session entry with intake + payment placeholders already queued

---

## 👤 Client Lifecycle (Retention + Relationship)

### New Client Intake
- **Trigger:** Intake form submitted
- **Actions:**
  - Create Client page
  - Link to first session
  - Set Status = Active
  - Queue welcome message + expectations

### Client Dormant Check (Monthly)
- **Trigger:** Scheduled monthly review
- **Actions:**
  - Find clients with no session in 60 days
  - Draft re-engagement note (gentle, non-guilting, inviting)
  - Create a follow-up task if you want to personally review first

### VIP Upgrade
- **Trigger:** Lifetime spend crosses $500+ (or your chosen threshold)
- **Actions:**
  - Set Client status = VIP
  - Send thank-you note + perk (priority booking, bonus resource, etc.)
- **Tools:** Notion + email

---

## 🎯 Implementation Priority (ROI Order)

1. **Google Calendar ↔ Notion Sync** — eliminates scheduling friction and double-entry.
2. **Aftercare Email Automation** — high-touch client care with near-zero effort.
3. **Quarterly Tax Reminder** — reduces stress and prevents last-minute scramble.
4. **Client Dormant Check** — recurring revenue without needing constant promotion.
5. **Inquiry → Lead capture + draft reply** — keeps your intake funnel clean and fast.

---

## ✅ The 5 Moves (Practical Mogul Checklist)

1. Build the **core databases**: Clients, Sessions, Events, Financials, Expenses, Leads.
2. Define the **status triggers** (Booked, Completed, Paid, Aftercare Sent).
3. Implement **Calendar sync** first.
4. Turn on **Aftercare** second (this is your signature).
5. Add **monthly + quarterly rhythms** (dormant check + tax summary).

---

*Last Updated: January 2, 2026*
