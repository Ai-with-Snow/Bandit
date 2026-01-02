"""
LMSIFY Notion ↔ Google Calendar Sync

Push: New Sessions/Events in Notion → Google Calendar
Pull: Calendly/Acuity bookings → Notion Sessions DB

Usage:
    python scripts/notion_flows/calendar_sync.py --push
    python scripts/notion_flows/calendar_sync.py --pull
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment
load_dotenv(".env.local")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
SESSIONS_DB = os.getenv("NOTION_SESSIONS_DB")
EVENTS_DB = os.getenv("NOTION_EVENTS_DB")

# Validate
if not NOTION_TOKEN:
    print("[ERROR] NOTION_TOKEN not found in .env.local")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# NOTION CLIENT
# ══════════════════════════════════════════════════════════════════════════════

try:
    from notion_client import Client
    notion = Client(auth=NOTION_TOKEN)
    print(f"[INIT] Notion client initialized")
except ImportError:
    print("[ERROR] notion-client not installed. Run: pip install notion-client")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE CALENDAR CLIENT (requires google-api-python-client)
# ══════════════════════════════════════════════════════════════════════════════

def get_calendar_service():
    """Get authenticated Google Calendar service."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import pickle
        
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    print("[ERROR] credentials.json not found. Download from Google Cloud Console.")
                    print("        https://console.cloud.google.com/apis/credentials")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"[ERROR] Failed to get calendar service: {e}")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# PUSH: Notion → Google Calendar
# ══════════════════════════════════════════════════════════════════════════════

def push_to_calendar():
    """Push unsynced Notion sessions/events to Google Calendar."""
    print("\n[PUSH] Querying Notion for unsynced sessions...")
    
    # Query Sessions where "GCal Synced" is not checked
    results = notion.databases.query(
        database_id=SESSIONS_DB,
        filter={
            "property": "GCal Synced",
            "checkbox": {"equals": False}
        }
    )
    
    sessions = results.get("results", [])
    print(f"[PUSH] Found {len(sessions)} unsynced sessions")
    
    if not sessions:
        print("[PUSH] Nothing to sync.")
        return
    
    service = get_calendar_service()
    if not service:
        print("[PUSH] Skipping calendar push - no Google auth.")
        return
    
    for session in sessions:
        props = session.get("properties", {})
        
        # Extract session details
        title_prop = props.get("Name", {}).get("title", [])
        title = title_prop[0]["plain_text"] if title_prop else "LMSIFY Session"
        
        date_prop = props.get("Date", {}).get("date", {})
        if not date_prop or not date_prop.get("start"):
            print(f"  [SKIP] No date set for: {title}")
            continue
        
        start_time = date_prop.get("start")
        end_time = date_prop.get("end") or start_time
        
        # Create Google Calendar event
        event = {
            'summary': f"🧘 {title}",
            'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
            'end': {'dateTime': end_time, 'timeZone': 'America/New_York'},
            'description': f"LMSIFY Session - Notion ID: {session['id']}"
        }
        
        try:
            created = service.events().insert(calendarId='primary', body=event).execute()
            print(f"  [OK] Created: {title} → {created.get('htmlLink')}")
            
            # Mark as synced in Notion
            notion.pages.update(
                page_id=session["id"],
                properties={"GCal Synced": {"checkbox": True}}
            )
        except Exception as e:
            print(f"  [ERROR] Failed to create event: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# PULL: Calendly/Webhook → Notion (placeholder for webhook receiver)
# ══════════════════════════════════════════════════════════════════════════════

def create_session_from_booking(booking_data: dict):
    """Create a Notion Session entry from a Calendly/Acuity webhook payload."""
    print(f"[PULL] Creating session from booking: {booking_data.get('name')}")
    
    # Extract booking details
    client_name = booking_data.get("name", "Unknown Client")
    start_time = booking_data.get("start_time")
    end_time = booking_data.get("end_time")
    email = booking_data.get("email")
    
    # Create Session in Notion
    new_session = notion.pages.create(
        parent={"database_id": SESSIONS_DB},
        properties={
            "Name": {"title": [{"text": {"content": f"Session: {client_name}"}}]},
            "Date": {"date": {"start": start_time, "end": end_time}},
            "Status": {"select": {"name": "Booked"}},
            "GCal Synced": {"checkbox": False},  # Will be synced on next push
            "Intake Sent": {"checkbox": False},
        }
    )
    
    print(f"[PULL] Created Notion session: {new_session['id']}")
    return new_session

# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LMSIFY Notion ↔ Calendar Sync")
    parser.add_argument("--push", action="store_true", help="Push Notion sessions to GCal")
    parser.add_argument("--pull", action="store_true", help="Pull bookings to Notion (manual test)")
    args = parser.parse_args()
    
    if args.push:
        push_to_calendar()
    elif args.pull:
        # Test pull with dummy data
        test_booking = {
            "name": "Test Client",
            "email": "test@example.com",
            "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
        }
        create_session_from_booking(test_booking)
    else:
        print("Usage: python calendar_sync.py --push OR --pull")
        print("  --push: Sync Notion sessions to Google Calendar")
        print("  --pull: Test creating a session from booking data")
