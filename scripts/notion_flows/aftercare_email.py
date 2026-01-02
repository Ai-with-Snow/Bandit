"""
LMSIFY Aftercare Email Automation

Sends aftercare emails when a Session status changes to "Completed".

Flow:
1. Query Sessions where Status = Completed AND Aftercare Sent = false
2. For each session, generate ethereal aftercare email
3. Send via Gmail API
4. Update Notion: Aftercare Sent = true

Usage:
    python scripts/notion_flows/aftercare_email.py
    python scripts/notion_flows/aftercare_email.py --dry-run
"""

import os
import sys
import base64
from datetime import datetime
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment
load_dotenv(".env.local")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
SESSIONS_DB = os.getenv("NOTION_SESSIONS_DB")
CLIENTS_DB = os.getenv("NOTION_CLIENTS_DB")

# ══════════════════════════════════════════════════════════════════════════════
# NOTION CLIENT
# ══════════════════════════════════════════════════════════════════════════════

try:
    from notion_client import Client
    notion = Client(auth=NOTION_TOKEN)
except ImportError:
    print("[ERROR] notion-client not installed. Run: pip install notion-client")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# GMAIL CLIENT (requires google-api-python-client + oauth2client)
# ══════════════════════════════════════════════════════════════════════════════

def get_gmail_service():
    """Get authenticated Gmail service."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import pickle
        
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None
        
        if os.path.exists('gmail_token.pickle'):
            with open('gmail_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    print("[WARN] credentials.json not found. Gmail send disabled.")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('gmail_token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"[WARN] Gmail auth failed: {e}")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# AFTERCARE EMAIL TEMPLATES (LMSIFY Brand Voice)
# ══════════════════════════════════════════════════════════════════════════════

def generate_aftercare_email(client_name: str, session_date: str) -> dict:
    """Generate ethereal aftercare email in LMSIFY brand voice."""
    subject = f"✨ Aftercare — Your Session with Snow"
    
    body = f"""Hello {client_name},

I hope this message finds you in a soft, grounded place.

Thank you for showing up for yourself in our session on {session_date}. What you brought into that space—your breath, your presence, your willingness to feel—was profound, and I want you to know I see you.

**Aftercare Reminders:**
- 💧 Hydrate intentionally. Let water be a gentle reset.
- 🛁 If you can, take a warm bath or shower. Let it wash over you.
- 📓 Journal anything that surfaced. No editing, just flow.
- 🌙 Rest without guilt. Your nervous system is still integrating.

There's no rush to "process" everything. Your body knows what to do.

If anything comes up that you want to share or explore, I'm here.

With warmth and care,
**Snow**
*Let Me Say It For You*

---
*This is an automated aftercare message from LMSIFY.*
"""
    
    return {"subject": subject, "body": body}

def send_email(gmail_service, to_email: str, subject: str, body: str) -> bool:
    """Send email via Gmail API."""
    if not gmail_service:
        print(f"  [SKIP] Gmail not configured. Would send to: {to_email}")
        return False
    
    try:
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to send email: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# MAIN FLOW
# ══════════════════════════════════════════════════════════════════════════════

def process_aftercare(dry_run: bool = False):
    """Process sessions needing aftercare emails."""
    print("\n" + "=" * 60)
    print("🧘 LMSIFY Aftercare Email Automation")
    print("=" * 60)
    
    if dry_run:
        print("[MODE] Dry run — no emails will be sent, no Notion updates")
    
    # Query sessions needing aftercare
    print("\n[QUERY] Finding sessions with Status=Completed, Aftercare Sent=false...")
    
    try:
        # Note: This filter assumes these properties exist in your Sessions DB:
        # - Status (select)
        # - Aftercare Sent (checkbox)
        # - Client (relation to Clients DB)
        # - Date (date)
        results = notion.databases.query(
            database_id=SESSIONS_DB,
            filter={
                "and": [
                    {"property": "Status", "select": {"equals": "Completed"}},
                    {"property": "Aftercare Sent", "checkbox": {"equals": False}}
                ]
            }
        )
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        print("[HINT] Make sure your Sessions DB has 'Status' (select) and 'Aftercare Sent' (checkbox) properties")
        return
    
    sessions = results.get("results", [])
    print(f"[FOUND] {len(sessions)} sessions need aftercare")
    
    if not sessions:
        print("[DONE] No pending aftercare emails.")
        return
    
    gmail = None if dry_run else get_gmail_service()
    
    for session in sessions:
        props = session.get("properties", {})
        
        # Get session title
        title_prop = props.get("Name", {}).get("title", [])
        title = title_prop[0]["plain_text"] if title_prop else "Session"
        
        # Get date
        date_prop = props.get("Date", {}).get("date", {})
        session_date = date_prop.get("start", "your recent session") if date_prop else "your recent session"
        
        # Get client email (requires looking up the related client)
        client_relation = props.get("Client", {}).get("relation", [])
        client_email = None
        client_name = "Beautiful Soul"
        
        if client_relation:
            client_id = client_relation[0].get("id")
            try:
                client_page = notion.pages.retrieve(page_id=client_id)
                client_props = client_page.get("properties", {})
                
                # Get client name
                name_prop = client_props.get("Name", {}).get("title", [])
                if name_prop:
                    client_name = name_prop[0]["plain_text"]
                
                # Get client email
                email_prop = client_props.get("Email", {}).get("email")
                if email_prop:
                    client_email = email_prop
            except:
                pass
        
        print(f"\n[PROCESS] {title}")
        print(f"  Client: {client_name}")
        print(f"  Email: {client_email or 'Not found'}")
        print(f"  Date: {session_date}")
        
        # Generate email
        email_content = generate_aftercare_email(client_name, session_date)
        
        if dry_run:
            print(f"  [DRY RUN] Would send: {email_content['subject']}")
            continue
        
        # Send email
        if client_email:
            sent = send_email(gmail, client_email, email_content['subject'], email_content['body'])
            if sent:
                print(f"  [SENT] ✅ Email sent to {client_email}")
        else:
            print(f"  [SKIP] No email address for client")
            continue
        
        # Update Notion
        try:
            notion.pages.update(
                page_id=session["id"],
                properties={
                    "Aftercare Sent": {"checkbox": True}
                }
            )
            print(f"  [UPDATED] ✅ Notion marked as sent")
        except Exception as e:
            print(f"  [ERROR] Failed to update Notion: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Aftercare processing complete!")
    print("=" * 60)

# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LMSIFY Aftercare Email Automation")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending emails or updating Notion")
    args = parser.parse_args()
    
    process_aftercare(dry_run=args.dry_run)
