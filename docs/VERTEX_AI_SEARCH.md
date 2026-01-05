# Vertex AI Search Integration - Quick Reference

**Date**: December 6, 2025  
**Status**: ✅ Operational

---

## Configuration

### Data Store
- **ID**: `bandit-hq-knowledge_1765072850414`
- **Location**: global
- **Source**: `gs://bandit-hq-knowledge-bucket/HQ/`
- **Documents**: 55 markdown files

### Environment
```powershell
.\setup_cloud.ps1  # Loads all required variables
```

---

## Usage

### RAG Queries
```bash
.\test_rag.bat
> /rag what are Bandit's core capabilities?
```

### Sync HQ Documents
```bash
.\sync_hq.bat                                    # Manual sync
.\sync_hq.bat --dry-run                          # Preview changes
py -3.12 scripts/watch_hq_changes.py             # Auto-watcher
```

### Direct gcloud
```bash
gcloud storage ls -r gs://bandit-hq-knowledge-bucket/HQ/
gcloud storage cp HQ/memory/new.md gs://bandit-hq-knowledge-bucket/HQ/memory/
```

---

## Files

| File | Purpose |
|------|---------|
| `scripts/bandit_cli.py` | RAG integration |
| `scripts/sync_hq_to_gcs.py` | Sync script |
| `scripts/watch_hq_changes.py` | Auto-watcher |
| `sync_hq.bat` | Quick sync |
| `test_rag.bat` | RAG tester |
| `setup_cloud.ps1` | Environment |

---

## Documentation

- **Full Guide**: [`walkthrough.md`](file:///C:/Users/Goddexx%20Snow/.gemini/antigravity/brain/80ac731a-470e-4579-a6ac-8a81deea501c/walkthrough.md)
- **Sync Guide**: [`hq_sync_guide.md`](file:///C:/Users/Goddexx%20Snow/.gemini/antigravity/brain/80ac731a-470e-4579-a6ac-8a81deea501c/hq_sync_guide.md)
- **Session Log**: [`session_20251206_vertex_ai_search.md`](file:///c:/Users/Goddexx%20Snow/Documents/Bandit/HQ/logs/session_20251206_vertex_ai_search.md)

---

**Quick Start**: `.\test_rag.bat` → `/rag your question here`
