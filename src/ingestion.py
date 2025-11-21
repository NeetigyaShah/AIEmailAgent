import json
import os
from imap_tools import MailBox
from .db_utils import save_emails

MOCK_INBOX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'mock_inbox.json')

def fetch_emails_mock() -> int:
    """Loads emails from the mock inbox JSON file into the database."""
    if not os.path.exists(MOCK_INBOX_PATH):
        print(f"Error: Mock inbox not found at {MOCK_INBOX_PATH}")
        return 0

    with open(MOCK_INBOX_PATH, 'r') as f:
        emails = json.load(f)

    # Ensure all keys exist
    for email in emails:
        if 'image_url' not in email:
            email['image_url'] = None
        if 'is_processed' not in email:
            email['is_processed'] = False
        if 'category' not in email:
            email['category'] = ""
        if 'action_items' not in email:
            email['action_items'] = []
        if 'generated_draft' not in email:
            email['generated_draft'] = ""

    save_emails(emails)
    return len(emails)

def fetch_emails_imap(username, password, server="imap.gmail.com", folder="INBOX", limit=10) -> int:
    """Fetches emails from an IMAP server and saves them to the database. Default limit is 10."""
    new_emails = []
    
    def process_msg(msg):
        return {
            "id": str(msg.uid),
            "sender": msg.from_,
            "subject": msg.subject,
            "body": msg.text or msg.html,
            "timestamp": msg.date.isoformat(),
            "category": "",
            "action_items": [],
            "generated_draft": "",
            "image_url": None, # IMAP fetch doesn't extract images yet
            "is_processed": False
        }

    try:
        # If password is actually an access token (OAuth), use xoauth2
        if len(password) > 100: # Simple heuristic for token vs password
            with MailBox(server).xoauth2(username, password, initial_folder=folder) as mailbox:
                for msg in mailbox.fetch(limit=limit, reverse=True):
                    new_emails.append(process_msg(msg))
        else:
            # Standard Login
            with MailBox(server).login(username, password, initial_folder=folder) as mailbox:
                for msg in mailbox.fetch(limit=limit, reverse=True):
                    new_emails.append(process_msg(msg))
        
        if new_emails:
            save_emails(new_emails)
            
        return len(new_emails)
    except Exception as e:
        print(f"IMAP Error: {e}")
        raise e
