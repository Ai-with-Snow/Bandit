# Bandit HQ Memory Index

**Agent:** Bandit  
**Sub-Agent:** Icewire (Operations Signalist)  
**Owner:** Marquitah Snowball "Snow" (Goddexx Snow)  
**Last Updated:** 2025-12-06  
**Next Review:** 2026-03-06

---

## Core Brain Files

| File | Purpose | Format |
|------|---------|--------|
| [`bandit_snow_profile_year1.yaml`](./bandit_snow_profile_year1.yaml) | 100 things Bandit knows/believes/infers about Snow | YAML |
| [`bandit_self_model_v1.md`](./bandit_self_model_v1.md) | 20 Q&A defining Bandit's operational self-model | Markdown |
| [`bandit_system_prompt.md`](./bandit_system_prompt.md) | Complete system prompt with all directives | Markdown |
| [`bandit_tools.py`](./bandit_tools.py) | Python tool/function implementations | Python |
| [`bandit_functions.json`](./bandit_functions.json) | Gemini Function Calling schema | JSON |
| [`bandit_rag_config.yaml`](./bandit_rag_config.yaml) | RAG search & retrieval configuration | YAML |

---

## Snow Profile Categories

The 100-item profile is organized into:

1. **Identity** (11 items) — Name preferences, self-concept, authority
2. **Nervous System & Trauma** (11 items) — Regulation, triggers, patterns
3. **Kink & Intimacy** (11 items) — Consent, dynamics, boundaries
4. **Business & Money** (12 items) — LMSIFY, pricing, sustainability
5. **Creativity & Art** (11 items) — Process, cycles, aesthetics
6. **Community & Leadership** (12 items) — Tone, safety, collaboration
7. **Daily Life & Capacity** (11 items) — Energy, routines, limits
8. **Spiritual & Celestial** (10 items) — Metaphor, ritual, intuition
9. **AI & Tech** (11 items) — Tool expectations, collaboration model

---

## Bandit Self-Model Sections

The 20-question self-model covers:

1. **Primary Function & Approach** (Q1-5) — Job, detection, calibration
2. **Nervous System & Context** (Q6-10) — Dashboard, tagging, spaces
3. **Memory & Correction** (Q11-15) — Updates, fade/stick, teaching
4. **Tone, Ethics & Boundaries** (Q16-20) — Voice, escalation, kink limits

---

## Available Functions

| Function | Purpose |
|----------|---------|
| `nervous_system_check` | Assess Snow's state, recommend mode |
| `search_snow_profile` | RAG search over profile |
| `update_profile_item` | Modify profile entries |
| `tag_information` | Classify as core/optional/nope |
| `create_bounded_task` | Scope work clearly |
| `park_task` | Safely pause work |
| `check_escalation` | Determine if human referral needed |
| `calibrate_tone` | Adjust communication style |
| `weekly_review` | Generate reflection prompts |
| `quarterly_profile_review` | Surface stale profile items |

---

## RAG Auto-Triggers

Bandit automatically retrieves from memory when:

- **Always:** `nervous_system_check`, `check_escalation`, `calibrate_tone`
- **Keywords:** money/pricing → business_and_money
- **Keywords:** overwhelmed/anxious → nervous_system_and_trauma
- **Keywords:** kink/consent → kink_and_intimacy
- **Keywords:** identity/name → identity

---

## Review Schedule

| Review Type | Frequency | Next Due |
|-------------|-----------|----------|
| Profile items marked "guessing" | Quarterly | 2026-03-06 |
| Full profile audit | Annually | 2026-12-06 |
| Self-model alignment check | Quarterly | 2026-03-06 |
| Tool effectiveness review | Monthly | 2025-01-06 |

---

*This index is alive. Update when adding/removing files.*
