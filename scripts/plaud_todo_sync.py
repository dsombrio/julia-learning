#!/usr/bin/env python3
"""TradBot Plaud Todo Sync — reads Plaud transcripts from email, extracts action items, saves to SQLite CRM."""
import urllib.request, urllib.parse, json, ssl, re, html
from datetime import datetime
import sqlite3

GRAPH_CLIENT_ID     = 'af03f985-1424-465a-bdbf-0cee6b59743b'
GRAPH_CLIENT_SECRET = 'yx58Q~ztCwAayJ3XO5650qc9N1cNcXmLbSAfTbRl'
GRAPH_TENANT_ID     = '3ac44adf-88d3-4ffe-aa18-d7ac71dc866f'
DB_PATH             = '/Users/tradbot/Library/Application Support/TradBot/crm.db'
AUTO_ADD_TODOS      = True

def get_token():
    data = urllib.parse.urlencode({
        'client_id': GRAPH_CLIENT_ID, 'client_secret': GRAPH_CLIENT_SECRET,
        'grant_type': 'client_credentials', 'scope': 'https://graph.microsoft.com/.default',
    }).encode()
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        'https://login.microsoftonline.com/' + GRAPH_TENANT_ID + '/oauth2/v2.0/token',
        data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.load(r)['access_token']

def fetch_all_inbox(token):
    """Fetch ALL inbox messages (handles pagination)."""
    ctx = ssl.create_default_context()
    headers = {'Authorization': f'Bearer {token}'}
    all_msgs = []
    
    # Build initial URL with explicit encoding
    base = 'https://graph.microsoft.com/v1.0/users/tradbot@traditionsales.com/mailFolders/inbox/messages'
    params = urllib.parse.urlencode({
        '$top': 50,
        '$orderby': 'receivedDateTime desc',
        '$select': 'id,subject,body,receivedDateTime,from,isRead'
    })
    page_url = f'{base}?{params}'
    
    while page_url and len(all_msgs) < 200:
        encoded = page_url.replace(' ', '%20')
        req = urllib.request.Request(encoded, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as r:
            data = json.load(r)
        msgs = data.get('value', [])
        all_msgs.extend(msgs)
        next_link = data.get('@odata.nextLink')
        page_url = next_link.replace(' ', '%20') if next_link else None
    
    return all_msgs

def strip_html(text):
    """Remove HTML tags and decode entities."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_todos(text, subject):
    """Parse action items from Plaud transcript plain-text.
    Strategy: ONLY trust the To-Do List / Action Items section. 
    If not present, return empty list (don't hallucinate from narrative).
    """
    todos = []
    
    # Find "To-Do List" or "Action Items" section
    todo_section_match = re.search(
        r'(?:To-Do List|Action Items|Tasks|Follow Up|Next Steps)\s+(.+?)(?=\n\n[A-Z][a-z]+:|\Z)',
        text, re.IGNORECASE | re.DOTALL
    )
    
    if not todo_section_match:
        return []
    
    section_text = todo_section_match.group(1)
    
    # Split on sentence boundaries (periods and semicolons)
    # Filter out meta lines (Deadline:, Stakeholder:, etc.) and short fragments
    sentences = re.split(r'(?<=[.;])\s+', section_text)
    
    skip_words = ['deadline:', 'stakeholder:', 'stakeholders:', 'timeframe:', 
                   'resources required:', 'success metrics:']
    
    for s in sentences:
        s = s.strip()
        if len(s) < 20:
            continue
        # Skip meta lines
        lower_s = s.lower()
        if any(sw in lower_s for sw in skip_words):
            continue
        # Skip lines that are just parenthesized comments
        if s.startswith('(') and s.endswith(')'):
            continue
        # Skip lines ending with colons only (section headers)
        if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*:$', s.strip()):
            continue
        todos.append({'title': s[:200], 'priority': 'medium'})
    
    # Deduplicate
    seen = set()
    deduped = []
    for t in todos:
        key = t['title'].lower()[:60]
        if key not in seen:
            seen.add(key)
            deduped.append(t)
    
    return deduped

def mark_read(token, msg_id):
    # Mark email as read AND record that we've processed it so we don't re-add
    ctx = ssl.create_default_context()
    
    # Record processed email in local tracking file
    processed_file = '/Users/tradbot/.openclaw/workspace/scripts/processed_plaud_emails.json'
    try:
        with open(processed_file) as f:
            processed = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        processed = []
    
    if msg_id not in processed:
        processed.append(msg_id)
        with open(processed_file, 'w') as f:
            json.dump(processed, f, indent=2)
    
    # Mark as read in email
    url = f'https://graph.microsoft.com/v1.0/users/tradbot@traditionsales.com/messages/{msg_id}'
    req = urllib.request.Request(url,
        data=json.dumps({'isRead': True}).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='PATCH'
    )
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            pass
    except Exception as e:
        print(f'    [WARN] Could not mark as read: {e}')

def already_processed(msg_id):
    """Check if we've already processed this email (prevents re-adding from old emails)."""
    processed_file = '/Users/tradbot/.openclaw/workspace/scripts/processed_plaud_emails.json'
    try:
        with open(processed_file) as f:
            return msg_id in json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False

def add_todo(title, desc, source='plaud', priority='medium'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Check duplicate
    c.execute("SELECT id FROM tasks WHERE title=? AND source=? AND DATE(created_at)=?",
              (title, source, today))
    if c.fetchone():
        print(f'    [SKIP] Already added today: {title[:70]}')
    else:
        c.execute("""INSERT INTO tasks (user_id, title, description, source, status, priority, created_at)
                     VALUES (1, ?, ?, ?, 'pending', ?, CURRENT_TIMESTAMP)""",
                  (title, desc, source, priority))
        print(f'    [ADDED] {title[:80]}')
    
    conn.commit()
    conn.close()

def get_body(token, msg_id):
    ctx = ssl.create_default_context()
    url = f'https://graph.microsoft.com/v1.0/users/tradbot@traditionsales.com/messages/{msg_id}?$select=body'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, context=ctx) as r:
        data = json.load(r)
    return data.get('body', {}).get('content', '')

def main():
    print(f'=== Plaud Todo Sync | {datetime.now().strftime("%Y-%m-%d %H:%M")} ===')
    
    token = get_token()
    print('Fetching inbox...')
    all_msgs = fetch_all_inbox(token)
    print(f'  Total inbox messages: {len(all_msgs)}')
    
    # Filter to Plaud emails (read OR unread — process all that match)
    plaud_emails = [
        m for m in all_msgs
        if (
            'plaud' in (m.get('subject') or '').lower() or
            'no-reply@plaud.ai' in (m.get('from') or {}).get('emailAddress', {}).get('address', '').lower()
        )
        and not already_processed(m.get('id', ''))
    ]
    
    if not plaud_emails:
        print('No unread Plaud transcripts found.')
        return
    
    print(f'Found {len(plaud_emails)} unread Plaud transcript(s)')
    
    total_added = 0
    for email in plaud_emails:
        sub = email.get('subject', '')
        msg_id = email.get('id')
        dt = email.get('receivedDateTime', '')[:10]
        
        print(f'\n  Processing: {sub}')
        print(f'  Date: {dt}')
        
        body_html = get_body(token, msg_id)
        body_text = strip_html(body_html)
        
        todos = extract_todos(body_text, sub)
        
        if not todos:
            print(f'    No action items found — skipping.')
            mark_read(token, msg_id)
            continue
        
        print(f'    Found {len(todos)} action item(s):')
        for todo in todos:
            desc = f'Source: {sub}'
            if AUTO_ADD_TODOS:
                add_todo(todo['title'], desc, source='plaud', priority=todo.get('priority', 'medium'))
            else:
                print(f'    [WOULD ADD] {todo["title"][:80]}')
            total_added += 1
        
        mark_read(token, msg_id)
    
    print(f'\nDone. Added {total_added} todo(s).')

if __name__ == '__main__':
    main()