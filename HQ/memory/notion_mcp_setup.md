# Notion MCP Setup for Bandit

> Enable direct AI access to your Notion workspace for agentic workflows.

---

## What is Notion MCP?

**Model Context Protocol (MCP)** is a standard for connecting AI tools to external services. Notion provides a hosted MCP server that gives AI assistants (like Bandit/Claude/ChatGPT) secure access to your workspace.

**Benefits:**
- 🔌 **One-click setup** — OAuth-based, no API keys to manage
- 📖 **Full CRUD** — AI can read/write pages, databases, comments
- ⚡ **Token-efficient** — Markdown-based API optimized for context windows

---

## Setup Options

### Option A: Notion MCP (Hosted by Notion)

1. Go to: https://developers.notion.com/docs/get-started-with-mcp
2. Click "Connect Notion"
3. Authorize your workspace
4. Copy the MCP server URL

**Use with:**
- Claude Desktop (built-in MCP support)
- Cursor (via MCP config)
- ChatGPT (via custom actions)

### Option B: Self-Hosted MCP Server

Notion provides an open-source MCP server you can run locally:

```bash
# Clone the Notion MCP server
git clone https://github.com/makenotion/notion-mcp-server.git
cd notion-mcp-server

# Install dependencies
npm install

# Set your Notion token
export NOTION_TOKEN=ntn_your_token_here

# Run the server
npm start
```

---

## Bandit MCP Integration (Future)

To integrate Notion MCP with Bandit's proxy server, add this endpoint:

```python
# In proxy_server.py

@app.post("/mcp/notion")
async def notion_mcp_passthrough(request: Request):
    """Passthrough to Notion MCP for AI-native workspace access."""
    # Forward to Notion MCP server
    pass
```

---

## Quick Reference

| Action | MCP Tool | Description |
| :--- | :--- | :--- |
| Search | `notion_search` | Find pages/databases by query |
| Read page | `notion_get_page` | Get page content as Markdown |
| Create page | `notion_create_page` | Create new page in database |
| Update page | `notion_update_page` | Update page properties |
| Query DB | `notion_query_database` | Filter/sort database pages |

---

## Related Files

- [Notion API Reference](file:///c:/Users/Goddexx%20Snow/Documents/bandit/HQ/memory/notion_api_reference.md)
- [Business Automations](file:///c:/Users/Goddexx%20Snow/Documents/bandit/HQ/memory/lmsify_business_automations.md)

---

*Last Updated: January 2, 2026*
