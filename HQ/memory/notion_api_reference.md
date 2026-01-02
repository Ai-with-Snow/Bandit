# Notion API Reference — Research Summary

> Comprehensive analysis of https://developers.notion.com/ for LMSIFY business automations.

---

## 🧠 Key Concepts

### Integration Types
| Type | Scope | Auth | Use Case |
| :--- | :--- | :--- | :--- |
| **Internal** | Single workspace | API Token | Custom automations, LMSIFY flows |
| **Public** | Any workspace | OAuth 2.0 | Shareable apps, requires security review |

### Core Objects
- **Pages**: Items in databases or standalone documents
- **Databases** (now "Data Sources" in v2025-09-03): Schemas with typed properties
- **Blocks**: Content units (text, images, embeds)
- **Users**: Workspace members and bot users

---

## 🔗 Key Endpoints

### Pages
| Endpoint | Method | Use Case |
| :--- | :--- | :--- |
| `/v1/pages` | POST | Create page (session, client, event) |
| `/v1/pages/{id}` | PATCH | Update properties (status, dates) |
| `/v1/pages/{id}` | GET | Retrieve page details |

### Databases/Data Sources
| Endpoint | Method | Use Case |
| :--- | :--- | :--- |
| `/v1/databases/{id}/query` | POST | Filter/sort pages (find dormant clients) |
| `/v1/databases/{id}` | GET | Get schema (property types) |

### Blocks
| Endpoint | Method | Use Case |
| :--- | :--- | :--- |
| `/v1/blocks/{id}/children` | PATCH | Append content to page |
| `/v1/blocks/{id}/children` | GET | Read page content |

---

## 🤖 Notion MCP (Model Context Protocol)

**What:** A hosted server that gives AI tools (ChatGPT, Claude, Cursor) direct access to Notion workspaces.

**Why It Matters for Bandit:**
- **Token-efficient**: Markdown-based API optimized for context windows
- **Full CRUD**: AI can read/write pages, databases, comments
- **Use Cases**: Generate PRDs, search workspace, manage tasks, create reports

**Setup:** https://developers.notion.com/docs/mcp

---

## 📊 Filtering & Pagination

### Filter Example (Find Dormant Clients)
```json
{
  "filter": {
    "and": [
      {"property": "Status", "select": {"equals": "Active"}},
      {"property": "Last Session", "date": {"before": "2025-11-01"}}
    ]
  }
}
```

### Pagination
- **Default page size**: 100 items
- **Use `start_cursor`** for subsequent pages
- **Supported endpoints**: Query database, list blocks, list users

---

## 🔧 Property Types for LMSIFY Databases

| Property | Type | Notes |
| :--- | :--- | :--- |
| Session Name | `title` | Required, one per database |
| Date | `date` | Start/end times |
| Status | `select` | Booked, Completed, Cancelled |
| Client | `relation` | Link to Clients DB |
| Payment Status | `select` | Pending, Paid |
| GCal Synced | `checkbox` | Track sync state |
| Aftercare Sent | `checkbox` | Track email state |

---

## 📚 Official Example Repos (Relevant to LMSIFY)

| Example | Use Case | Link |
| :--- | :--- | :--- |
| **Send email from Notion trigger** | Aftercare emails | [GitHub](https://github.com/makenotion/notion-cookbook/tree/main/examples/javascript/database-email-update) |
| **Add pages to database** | Create sessions/clients | [GitHub](https://github.com/makenotion/notion-cookbook/blob/main/examples/javascript/intro-to-notion-api/intermediate/2-add-page-to-database.ts) |
| **Filter and sort pages** | Dormant client check | [GitHub](https://github.com/makenotion/notion-cookbook/blob/main/examples/javascript/intro-to-notion-api/intermediate/4-sort-database.ts) |
| **Sync with external service** | Calendar/Acuity sync | [Spotify example](https://developers.notion.com/page/spotify) |

---

## ⚙️ API Version Note

**Current:** `2025-09-03`
- "Databases" renamed to "Data Sources"
- `data_source_id` replaces `database_id` in parent objects
- Use `notion-client` SDK v2.4+ for compatibility

---

## 🔗 Quick Links

- [API Reference](https://developers.notion.com/reference/intro)
- [Examples](https://developers.notion.com/page/examples)
- [Notion MCP](https://developers.notion.com/docs/mcp)
- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py)

---

*Last Updated: January 2, 2026*
