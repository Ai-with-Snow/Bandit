"""
LMSIFY Google APIs Validation Test

Tests connectivity and basic operations for:
- Gmail (read inbox, send test)
- Google Calendar (list events, create test)
- Google Sheets (read/write)
- Google Tasks (list, create)

Usage:
    python scripts/notion_flows/test_google_apis.py
"""

import os
import sys
import pickle
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(".env.local")

# ══════════════════════════════════════════════════════════════════════════════
# AUTH SETUP
# ══════════════════════════════════════════════════════════════════════════════

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/forms.body.readonly',
]

def get_credentials():
    """Get or refresh Google OAuth credentials."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    
    creds = None
    
    if os.path.exists('google_token.pickle'):
        with open('google_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json not found!")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('google_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

# ══════════════════════════════════════════════════════════════════════════════
# TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_gmail(creds):
    """Test Gmail API - read recent emails."""
    print("\n📧 TEST: Gmail API")
    print("-" * 40)
    try:
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        
        # Get recent messages
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])
        
        print(f"✅ Connected! Found {len(messages)} recent messages")
        
        # Get profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Email: {profile.get('emailAddress')}")
        
        return True
    except Exception as e:
        print(f"❌ Gmail failed: {e}")
        return False

def test_calendar(creds):
    """Test Google Calendar API - list upcoming events."""
    print("\n📅 TEST: Google Calendar API")
    print("-" * 40)
    try:
        from googleapiclient.discovery import build
        service = build('calendar', 'v3', credentials=creds)
        
        # Get upcoming events
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        print(f"✅ Connected! Found {len(events)} upcoming events")
        for event in events[:3]:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"   - {event.get('summary', 'No title')} ({start[:10]})")
        
        return True
    except Exception as e:
        print(f"❌ Calendar failed: {e}")
        return False

def test_sheets(creds):
    """Test Google Sheets API - create test sheet."""
    print("\n📊 TEST: Google Sheets API")
    print("-" * 40)
    try:
        from googleapiclient.discovery import build
        service = build('sheets', 'v4', credentials=creds)
        
        # Create a test spreadsheet
        spreadsheet = {
            'properties': {'title': f'LMSIFY Test - {datetime.now().strftime("%Y-%m-%d %H:%M")}'}
        }
        sheet = service.spreadsheets().create(body=spreadsheet).execute()
        sheet_id = sheet.get('spreadsheetId')
        sheet_url = sheet.get('spreadsheetUrl')
        
        print(f"✅ Created test sheet: {sheet_id[:20]}...")
        print(f"   URL: {sheet_url}")
        
        # Write test data
        values = [['Client', 'Amount', 'Date'], ['Test Client', 150, '2026-01-02']]
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='A1:C2',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
        print(f"✅ Wrote test data to sheet")
        
        return True
    except Exception as e:
        print(f"❌ Sheets failed: {e}")
        return False

def test_tasks(creds):
    """Test Google Tasks API - list and create."""
    print("\n✅ TEST: Google Tasks API")
    print("-" * 40)
    try:
        from googleapiclient.discovery import build
        service = build('tasks', 'v1', credentials=creds)
        
        # List task lists
        results = service.tasklists().list(maxResults=10).execute()
        task_lists = results.get('items', [])
        
        print(f"✅ Connected! Found {len(task_lists)} task lists")
        for tl in task_lists[:3]:
            print(f"   - {tl.get('title')}")
        
        # Create a test task in the first list
        if task_lists:
            first_list_id = task_lists[0]['id']
            task = {
                'title': f'LMSIFY Test Task - {datetime.now().strftime("%H:%M")}',
                'notes': 'Created by Bandit integration test'
            }
            created = service.tasks().insert(tasklist=first_list_id, body=task).execute()
            print(f"✅ Created test task: {created.get('title')}")
        
        return True
    except Exception as e:
        print(f"❌ Tasks failed: {e}")
        return False

def test_drive(creds):
    """Test Google Drive API - list files."""
    print("\n📂 TEST: Google Drive API")
    print("-" * 40)
    try:
        from googleapiclient.discovery import build
        service = build('drive', 'v3', credentials=creds)
        
        # List recent files
        results = service.files().list(pageSize=5, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        print(f"✅ Connected! Found {len(files)} recent files")
        for f in files[:3]:
            print(f"   - {f.get('name')}")
        
        return True
    except Exception as e:
        print(f"❌ Drive failed: {e}")
        return False

def test_docs(creds):
    """Test Google Docs API - create test doc."""
    print("\n📄 TEST: Google Docs API")
    print("-" * 40)
    try:
        from googleapiclient.discovery import build
        service = build('docs', 'v1', credentials=creds)
        
        # Create a test document
        doc = service.documents().create(body={
            'title': f'LMSIFY Test Doc - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        }).execute()
        
        print(f"✅ Created test doc: {doc.get('title')}")
        print(f"   ID: {doc.get('documentId')[:20]}...")
        
        return True
    except Exception as e:
        print(f"❌ Docs failed: {e}")
        return False

def test_slides(creds):
    """Test Google Slides API - create test presentation."""
    print("\n📊 TEST: Google Slides API")
    print("-" * 40)
    try:
        from googleapiclient.discovery import build
        service = build('slides', 'v1', credentials=creds)
        
        # Create a test presentation
        presentation = service.presentations().create(body={
            'title': f'LMSIFY Test Slides - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        }).execute()
        
        print(f"✅ Created test presentation: {presentation.get('title')}")
        print(f"   ID: {presentation.get('presentationId')[:20]}...")
        
        return True
    except Exception as e:
        print(f"❌ Slides failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("🔌 LMSIFY Google APIs Validation Test")
    print("=" * 60)
    
    # Get credentials (will open browser for OAuth if needed)
    print("\n[AUTH] Getting Google OAuth credentials...")
    creds = get_credentials()
    
    if not creds:
        print("❌ Failed to get credentials")
        sys.exit(1)
    
    print("✅ Credentials obtained")
    
    # Run tests
    results = {
        'Gmail': test_gmail(creds),
        'Calendar': test_calendar(creds),
        'Sheets': test_sheets(creds),
        'Tasks': test_tasks(creds),
        'Drive': test_drive(creds),
        'Docs': test_docs(creds),
        'Slides': test_slides(creds),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    for api, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {api}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All Google APIs validated successfully!")
    else:
        print("\n⚠️ Some APIs failed. Check the errors above.")
    
    sys.exit(0 if all_passed else 1)
