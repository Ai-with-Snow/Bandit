# BANDIT HARNESS PLAYBOOK

## 🤖 The Automated Solo Developer Protocol

This Playbook defines the strict "Rules of Engagement" for the Bandit Persistent Agent Harness. It is inspired by the "Anthropic Secret Playbook" for long-running autonomous agents.

### 🏛️ Roles

1.  **Initializer Agent**
    *   **Trigger**: Run once at the start of a completely new project epoch.
    *   **Responsibility**:
        *   Create `feature_list.json` (The "PRD" / backlog).
        *   Create `bandit_progress.json` (The "Session Log").
        *   Initialize `git` repo (if not exists).
        *   Does NOT write feature code.

2.  **Coding Agent** (Recurring Loop)
    *   **Trigger**: Run repeatedly until `feature_list.json` is clear.
    *   **The Loop**:
        1.  **PRIME**: Read `bandit_progress.json`, `feature_list.json`, and `git log`. Get context.
        2.  **SCOPE**: Select *ONE* feature/task from `feature_list.json` that is `passed: false`.
        3.  **IMPLEMENT**: Write code, tests, and configuration for *only* that feature.
        4.  **VERIFY**: Run `pytest` targeting the specific test file.
        5.  **DECIDE**:
            *   If Tests PASS: Mark feature `passed: true` in `feature_list.json`.
            *   If Tests FAIL: Mark `status: failed`, log error, do NOT mark passed.
        6.  **COMMIT**: Write entry to `bandit_progress.json` and (optional) git commit.

### 📜 Core Artifacts

*   `HQ/harness/feature_list.json`: The Source of Truth for what needs to be built.
*   `HQ/harness/bandit_progress.json`: The Memory of what has been done.
*   `tests/`: The Adjudicator of Truth. No manual "it looks good".

### ⚠️ Golden Rules

1.  **Trust Tests Only**: Never mark a feature as passed unless a verify command exits with code 0.
2.  **One Token At A Time**: Do not try to implement Year 1 and Year 4 in one session.
3.  **Log Everything**: The next agent has *zero* memory of this session except what is written to `bandit_progress.json`.
4.  **Async Persistence**: Data sync to BigQuery happens in background; do not block the main loop.

---
*Created by: Antigravity*
*Maintained by: Bandit*
