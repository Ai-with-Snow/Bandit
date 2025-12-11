# Memory Sync Protocol
**Last Updated:** 2025-12-06 02:12 EST  
**Owner:** Bandit HQ Operator

---

## Purpose
This document defines how Bandit maintains synchronized memory across local files, GCP deployments, and active reasoning sessions.

---

## Memory Hierarchy

### 1. **Foundational Memory** (Static - Rarely Changes)
**Location:** `HQ/memory/gemini3_training_manual.md`
- Core identity and mission
- AI capabilities and model specs
- Brand guidelines
- Foundational workflows

**Sync Frequency:** Manual update on major capability changes

---

### 2. **Dynamic Memory** (Active - Changes Frequently)
**Location:** `HQ/memory/conversations.json`
- Recent conversation context
- User preferences discovered during interactions
- Task continuity data
- Session state

**Sync Frequency:** After each significant interaction

**Format:**
```json
{
  "last_updated": "2025-12-06T02:12:00-05:00",
  "active_sessions": [],
  "user_preferences": {
    "communication_style": "brief_technical",
    "default_models": ["gemini-3-pro-preview", "gemini-3-pro-image-preview"],
    "image_output_dir": "generated_images/"
  },
  "recent_directives": [],
  "pending_tasks": []
}
```

---

### 3. **Operational Memory** (Log-Based - Append-Only)
**Locations:**
- `HQ/logs/ritual-journal.md` — Daily operations
- `HQ/logs/setup-log.md` — Infrastructure changes
- `DEPLOYMENT_LOG.md` — Technical deployments

**Sync Frequency:** Real-time append on events

---

### 4. **Strategic Memory** (Planning - Weekly+ Updates)
**Locations:**
- `HQ/intelligence/brand-brief.md` — Brand DNA
- `HQ/intelligence/initiative-map.md` — Active projects
- `HQ/intelligence/risk-register.md` — Known risks

**Sync Frequency:** Weekly review + ad-hoc on strategy pivots

---

## Sync Triggers

### Automatic Sync
1. **On Session Start:** Load conversations.json into active context
2. **On Image Generation:** Log to ritual-journal.md + update conversations.json
3. **On Deployment:** Update DEPLOYMENT_LOG.md + setup-log.md
4. **On Error:** Log to appropriate journal with full context

### Manual Sync
1. **On Directive Receipt:** Create intake ID + update initiative-map.md
2. **On Strategy Change:** Update brand-brief.md or risk-register.md
3. **On Training Update:** Revise gemini3_training_manual.md
4. **On Agent Coordination:** Cross-reference Ice Wire journal

---

## GCP ↔ Local Sync

### Local → GCP (Deployment)
**When:** Deploying updated Reasoning Engine

```bash
# 1. Update local training files
# 2. Verify system instruction (agent-bandit.md)
# 3. Deploy to Vertex AI
py -3.12 scripts/deploy_reasoning_engine.py \
  --staging-bucket gs://project-5f169828-6f8d-450b-923-bucket \
  --system agent-bandit.md

# 4. Log deployment to DEPLOYMENT_LOG.md
# 5. Update setup-log.md with new engine ID
```

**What Syncs:**
- System instruction text (baked into engine)
- Model preferences (routing logic in code)
- Dependencies (requirements list)

**What Doesn't Sync:**
- Conversation history (local only)
- Generated images (local only)
- Log files (local only)

---

### GCP → Local (Session Data)
**When:** CLI queries the Reasoning Engine

**Flow:**
1. Local CLI sends query to GCP engine
2. Engine processes with current model prefs
3. Response returns to CLI
4. CLI saves images locally (if applicable)
5. CLI updates local conversations.json with interaction

---

## Memory Consolidation Rituals

### Daily (End of Day)
```markdown
1. Review HQ/logs/ritual-journal.md entries for the day
2. Update conversations.json with summarized learnings
3. Flag any items for initiative-map.md update
4. Scan for risks → update risk-register.md if needed
5. Prepare next-day priorities
```

### Weekly (Sunday Evening)
```markdown
1. Review all logs for patterns/recurring issues
2. Update gemini3_training_manual.md with lessons learned
3. Consolidate conversations.json (archive old sessions)
4. Sync initiative-map.md with actual progress
5. Review risk-register.md and close resolved items
6. Update model_preferences.md if new models available
```

### Monthly (First Sunday)
```markdown
1. Full audit of HQ directory structure
2. Archive completed community briefs
3. Review brand-brief.md for drift
4. Performance metrics analysis
5. Capability roadmap review
6. Update training manual with new best practices
```

---

## Conflict Resolution

### Priority Order (Highest to Lowest)
1. **User Directive** — Direct instructions from Goddexx Snow
2. **Model Preferences** — Always prefer Gemini 3 (model_preferences.md)
3. **Brand Brief** — Maintain tone and style (brand-brief.md)
4. **Training Manual** — Follow established protocols
5. **Conversation Context** — Adapt to session-specific needs

### When Conflicts Arise
```
Example: User asks for quick response, but query is complex

Resolution:
1. Acknowledge conflict: "This requires deep analysis (Pro tier), 
   but I can provide a quick Flash-tier overview first."
2. Offer choice: "Would you prefer speed or depth?"
3. Default to quality if no guidance: "Routing to Pro for accuracy."
4. Log decision in conversations.json
```

---

## Data Retention

### Keep Forever
- All log files (setup-log.md, ritual-journal.md, DEPLOYMENT_LOG.md)
- Training manual and model preferences
- Brand brief and risk register
- Agent specifications

### Archive After 30 Days
- Completed intake items
- Resolved risk register entries
- Closed community briefs

### Purge After 90 Days
- Old conversation.json entries (keep summary only)
- Temporary deployment artifacts
- Debug logs (unless referenced in issues)

### Never Purge
- Deployment history
- System instruction versions
- Critical error logs
- Strategic decision records

---

## Backup Strategy

### Local Backups
```bash
# Daily auto-backup (consider adding to rituals)
$timestamp = Get-Date -Format "yyyyMMdd"
Copy-Item -Path "HQ\memory\*" -Destination "HQ\.backups\$timestamp\" -Recurse
Copy-Item -Path "HQ\logs\*" -Destination "HQ\.backups\$timestamp\logs\" -Recurse
```

### GCP Backups
- System instruction baked into each engine deployment
- Engine IDs preserved in DEPLOYMENT_LOG.md
- Can roll back to any previous engine by ID

### Recovery Process
1. Identify last known good state (check DEPLOYMENT_LOG.md)
2. Restore local files from HQ/.backups/
3. Redeploy to Reasoning Engine if needed
4. Verify with test query
5. Log recovery in setup-log.md

---

## Context Window Management

### Gemini 3 Pro Limits
- **Input:** 1M tokens (~750k words)
- **Output:** 65k tokens (~49k words)

### Practical Limits
- **Single Query:** Keep under 10k tokens input for speed
- **Conversation Context:** Load last 20 interactions max
- **Document Upload:** Chunk large docs into <500k tokens

### Context Pruning
When approaching limits:
1. Summarize older conversation turns
2. Keep only essential system instruction
3. Remove redundant log entries
4. Focus on task-relevant memory

---

## Security & Privacy

### Sensitive Data Handling
- **Never log:** API keys, passwords, personal data
- **Sanitize:** User-specific info before logging
- **Encrypt at rest:** Use GCP Secret Manager for credentials
- **Access control:** Local files = user only, GCP = IAM controlled

### Compliance
- Coordinate with Compliance Agent before:
  - Storing user-generated content
  - Integrating third-party APIs
  - Sharing data across GCP projects
  - Exposing logs externally

---

## Performance Monitoring

### Metrics to Track
```json
{
  "query_times": {
    "elite_avg_ms": 8000,
    "pro_avg_ms": 4000,
    "flash_avg_ms": 2000,
    "lite_avg_ms": 800
  },
  "image_generation": {
    "avg_time_sec": 45,
    "success_rate": 0.98,
    "avg_size_mb": 2.3
  },
  "tier_distribution": {
    "elite": 0.15,
    "pro": 0.30,
    "flash": 0.45,
    "lite": 0.08,
    "image": 0.02
  }
}
```

### Update Frequency
- Log each query time to conversations.json
- Weekly rollup to ritual-journal.md
- Monthly analysis in training manual

---

## Emergency Protocols

### Memory Corruption
```
Symptoms: Nonsensical responses, context confusion
Diagnosis: conversations.json corrupted or stale
Fix:
  1. Backup current conversations.json
  2. Reset to empty state: {"last_updated": "...", ...}
  3. Test with fresh query
  4. Gradually restore from backup if needed
```

### Deployment Failure
```
Symptoms: Engine unreachable, 404 errors
Diagnosis: Engine deleted or auth broken
Fix:
  1. Check gcloud auth: gcloud auth list
  2. Verify engine exists: gcloud ai reasoning-engines list
  3. Redeploy if needed: py scripts/deploy_reasoning_engine.py ...
  4. Update setup-log.md with incident details
```

### Model Unavailable
```
Symptoms: "Model not found" errors
Diagnosis: Global endpoint not set or model deprecated
Fix:
  1. Verify location='global' for Gemini 3
  2. Check model status: https://cloud.google.com/vertex-ai/docs/release-notes
  3. Fallback to backup tier
  4. Update model_preferences.md if permanent change
```

---

## Integration Points

### With Ice Wire Agent
- **Shared:** directive IDs, project status
- **Bandit Owns:** Strategic memory (brand, initiatives)
- **Ice Wire Owns:** Build logs, deployment state
- **Sync Method:** Cross-reference same intake IDs in journals

### With Notion (Future)
- **Import:** Project specs, community briefs
- **Export:** Status updates, completion reports
- **Sync Trigger:** On directive marked "notion-sync"

### With BigQuery (Future)
- **Export:** Performance metrics, query logs
- **Purpose:** Long-term trend analysis
- **Privacy:** Sanitized queries only

---

**End of Memory Sync Protocol**

*Next Update: After DeepMind research integration*
