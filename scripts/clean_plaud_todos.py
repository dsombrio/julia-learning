#!/usr/bin/env python3
"""Clean plaud todos - keep only truly actionable items for David."""
import sqlite3, re

DB_PATH = '/Users/tradbot/Library/Application Support/TradBot/crm.db'

REMOVE_PREFIXES = [
    'AI Suggestions', 'Here are some possible solutions', 'Here are possible solutions',
    'Context:', 'Impact:', 'Current Situation:', 'Examples:', 'Pain Points:',
    'Background:', 'Overview:', 'Quantitative Metrics:', 'Specific Goals:',
    'Resources Required:', 'Success Metrics:', 'Stakeholders:', 'Timeframe:',
    'Notes:', 'Other Information', 'The customer wants', 'The customer described',
    'The consultant', 'The representative', 'The vendor', 'The meeting',
]

REMOVE_PATTERNS = [
    r'^\[', r'^\@', r'\[TBD\]', r'\[No primary', r'^\s*\d+\.\s',  # bracketed, mentions, numbered list items
]

REMOVE_KEYWORDS = [
    'The AI has identified', 'Pain Points', 'Here are possible solutions',
    'Current Situation', 'Examples:', 'Context:', 'Stakeholders:', 'Resources Required:',
    'Success Metrics:', 'Timeframe:', 'Quantitative Metrics',
]

def is_actionable(title):
    t = title.strip()
    
    # Check prefix exclusions
    for pfx in REMOVE_PREFIXES:
        if t.startswith(pfx):
            return False
    
    # Check pattern exclusions
    for pat in REMOVE_PATTERNS:
        if re.match(pat, t, re.IGNORECASE):
            return False
    
    # Check keyword exclusions
    t_lower = t.lower()
    for kw in REMOVE_KEYWORDS:
        if kw.lower() in t_lower:
            return False
    
    # Too short
    if len(t) < 30:
        return False
    
    # Must start with a verb (or similar actionable pattern)
    action_verbs = [
        r'^(email|send|call|contact|text|reach out|get back|circle back|check on|schedule|confirm|review|prepare|quote|mail|follow up|drop off|set up|coordinate|provide|get pricing|get quote|offer|propose|pilot|implement|negotiate|prepare|develop|arrange|secure|submit|share|explore|research|prepare|leave|attend|visit|coordinate|attach|include|confirm|schedule)',
        r'^(vendor to|sales rep to|rep to|supplier to|consultant to)',
        r'^(meet|prepare and bring|visit|attend|schedule|leave|follow up|follow-up)',
    ]
    
    has_action_verb = any(re.match(p, t, re.IGNORECASE) for p in action_verbs)
    
    # OR: clear action item format (starts with verb, contains "to" action pattern)
    has_to_pattern = re.match(r'^(email|send|call|contact|text|schedule|confirm|review|prepare|quote|leave|follow up|provide|get|share|offer|propose|arrange|secure|submit|explore|research|attach|drop off)\s+', t, re.IGNORECASE)
    
    return has_action_verb or has_to_pattern

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Get all plaud todos
c.execute("SELECT id, title FROM tasks WHERE source='plaud' ORDER BY id")
all_todos = c.fetchall()

keep = []
remove = []
for tid, title in all_todos:
    if is_actionable(title):
        keep.append(tid)
    else:
        remove.append(tid)

# Delete non-actionable ones
placeholders = ','.join('?' * len(remove))
c.execute(f"DELETE FROM tasks WHERE id IN ({placeholders})", remove)
conn.commit()

print(f'Kept: {len(keep)} | Removed: {len(remove)}')
print('\nRemoved items:')
for tid, title in all_todos:
    if tid in remove:
        print(f'  [{tid}] {title[:100]}')

print(f'\nRemaining: {len(keep)} todos')