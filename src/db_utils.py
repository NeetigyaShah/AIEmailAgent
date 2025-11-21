import sqlite3
import json
from typing import List, Dict

DB_PATH = "email_agent.db"

DEFAULT_PROMPTS = {
    "categorization": "Categorize this email into one of the following: Work, Personal, Spam, Newsletter. Return only the category name.",
    "extraction": "Extract action items from this email as a list of strings. If no action items, return an empty list.",
    "auto_reply": "Draft a polite and professional reply to this email. Keep it concise. IMPORTANT: Do NOT draft a reply if the sender address contains 'noreply' or 'no-reply'. In that case, return 'N/A'."
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables and default prompts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Emails table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            sender TEXT,
            subject TEXT,
            body TEXT,
            timestamp TEXT,
            category TEXT,
            action_items TEXT,
            generated_draft TEXT,
            summary TEXT,
            image_url TEXT,
            is_processed BOOLEAN DEFAULT 0
        )
    ''')

    # Prompts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            name TEXT PRIMARY KEY,
            prompt_text TEXT
        )
    ''')

    # Insert default prompts if not exist
    for name, text in DEFAULT_PROMPTS.items():
        cursor.execute('INSERT OR IGNORE INTO prompts (name, prompt_text) VALUES (?, ?)', (name, text))

    conn.commit()
    conn.close()

def save_emails(emails: List[Dict]):
    """Save a list of emails to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for email in emails:
        cursor.execute('''
            INSERT OR IGNORE INTO emails (id, sender, subject, body, timestamp, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email['id'], email['sender'], email['subject'], email['body'], email['timestamp'], email.get('image_url')))
        
    conn.commit()
    conn.close()

def get_unprocessed_emails() -> List[Dict]:
    """Fetch emails that haven't been processed yet."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails WHERE is_processed = 0')
    rows = cursor.fetchall()
    conn.close()
    
    emails = []
    for row in rows:
        email = dict(row)
        # Parse JSON fields if they exist (though initially they are None)
        emails.append(email)
    return emails

def update_email_result(email_id: str, category: str, action_items: List[str], draft: str, summary: str = ""):
    """Update email with processing results."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE emails 
        SET category = ?, action_items = ?, generated_draft = ?, summary = ?, is_processed = 1
        WHERE id = ?
    ''', (category, json.dumps(action_items), draft, summary, email_id))
    conn.commit()
    conn.close()

def get_prompts() -> Dict[str, str]:
    """Fetch all prompts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM prompts')
    rows = cursor.fetchall()
    conn.close()
    return {row['name']: row['prompt_text'] for row in rows}

def update_prompt(name: str, new_text: str):
    """Update a specific prompt."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE prompts SET prompt_text = ? WHERE name = ?', (new_text, name))
    conn.commit()
    conn.close()

def get_all_emails() -> List[Dict]:
    """Fetch all emails for display."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails ORDER BY timestamp DESC, id ASC')
    rows = cursor.fetchall()
    conn.close()
    
    emails = []
    for row in rows:
        email = dict(row)
        if email['action_items']:
            try:
                email['action_items'] = json.loads(email['action_items'])
            except Exception:
                email['action_items'] = []
        emails.append(email)
    return emails

def clear_all_emails():
    """Delete all emails from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM emails')
    conn.commit()
    conn.close()

    conn.close()
