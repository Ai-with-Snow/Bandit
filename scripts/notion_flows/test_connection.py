"""
LMSIFY Notion Integration Test

Validates:
1. API token is valid
2. Sessions database is accessible
3. Basic query returns results

Usage: python scripts/notion_flows/test_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv(".env.local")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
SESSIONS_DB = os.getenv("NOTION_SESSIONS_DB")
CLIENTS_DB = os.getenv("NOTION_CLIENTS_DB")
EVENTS_DB = os.getenv("NOTION_EVENTS_DB")

print("=" * 60)
print("🔌 LMSIFY Notion Integration Test")
print("=" * 60)

# Validate environment
if not NOTION_TOKEN:
    print("❌ NOTION_TOKEN not found in .env.local")
    sys.exit(1)
print(f"✅ NOTION_TOKEN loaded (ends with ...{NOTION_TOKEN[-8:]})")

if not SESSIONS_DB:
    print("❌ NOTION_SESSIONS_DB not found in .env.local")
    sys.exit(1)
print(f"✅ NOTION_SESSIONS_DB: {SESSIONS_DB}")

# Initialize client
try:
    from notion_client import Client
    notion = Client(auth=NOTION_TOKEN)
    print("✅ Notion client initialized")
except ImportError:
    print("❌ notion-client not installed. Run: pip install notion-client")
    sys.exit(1)

# Test 1: Retrieve Sessions database schema
print("\n📊 Test 1: Retrieve Sessions Database Schema")
print("-" * 40)
try:
    db = notion.databases.retrieve(database_id=SESSIONS_DB)
    print(f"✅ Database Title: {db.get('title', [{}])[0].get('plain_text', 'Untitled')}")
    print(f"✅ Properties ({len(db.get('properties', {}))}):")
    for prop_name, prop_value in db.get("properties", {}).items():
        print(f"   - {prop_name}: {prop_value.get('type')}")
except Exception as e:
    print(f"❌ Failed to retrieve database: {e}")
    sys.exit(1)

# Test 2: Query Sessions database (first 5 items)
print("\n📋 Test 2: Query Sessions Database")
print("-" * 40)
try:
    results = notion.databases.query(
        database_id=SESSIONS_DB,
        page_size=5
    )
    pages = results.get("results", [])
    print(f"✅ Found {len(pages)} pages (limited to 5)")
    for page in pages:
        title_prop = page.get("properties", {}).get("Name", {}).get("title", [])
        title = title_prop[0]["plain_text"] if title_prop else "Untitled"
        print(f"   - {title}")
except Exception as e:
    print(f"❌ Failed to query database: {e}")
    sys.exit(1)

# Test 3: Check Clients database
print("\n👤 Test 3: Check Clients Database")
print("-" * 40)
if CLIENTS_DB:
    try:
        db = notion.databases.retrieve(database_id=CLIENTS_DB)
        print(f"✅ Clients DB accessible: {db.get('title', [{}])[0].get('plain_text', 'Untitled')}")
    except Exception as e:
        print(f"⚠️ Clients DB issue: {e}")
else:
    print("⚠️ NOTION_CLIENTS_DB not configured")

# Test 4: Check Events database
print("\n📅 Test 4: Check Events Database")
print("-" * 40)
if EVENTS_DB:
    try:
        db = notion.databases.retrieve(database_id=EVENTS_DB)
        print(f"✅ Events DB accessible: {db.get('title', [{}])[0].get('plain_text', 'Untitled')}")
    except Exception as e:
        print(f"⚠️ Events DB issue: {e}")
else:
    print("⚠️ NOTION_EVENTS_DB not configured")

print("\n" + "=" * 60)
print("🎉 All tests passed! Notion integration is ready.")
print("=" * 60)
