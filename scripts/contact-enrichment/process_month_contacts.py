#!/usr/bin/env python3
"""
Process contacts from email metadata month by month
"""
import json
import re
from pathlib import Path
from collections import defaultdict

def is_automated(email):
    """Check if email looks automated"""
    patterns = ['noreply', 'no-reply', 'donotreply', 'notifications', 'automated',
                'system', 'bounce', 'mailer-daemon', 'support@', 'help@', 'info@',
                'hello@', 'hi@', 'team@', 'beehiiv.com', 'substack.com', 'calendly.com',
                'linkedin.com', 'facebook.com', 'twitter.com', 'calendar.google',
                'stripe.com', 'mercury.com', 'blotato.com', '@mail.', 'updates@',
                'news@', 'digest@', 'newsletter@', 'invoice@']
    return any(p in email.lower() for p in patterns)

def extract_email(header):
    """Extract email from 'Name <email>' format"""
    match = re.search(r'<(.+?)>', header)
    if match:
        return match.group(1).strip()
    return header.strip()

def extract_name(header):
    """Extract name from 'Name <email>' format"""
    if '<' in header:
        return header[:header.index('<')].strip().strip('"')
    return ""

# Load or initialize progress
progress_file = Path('contact_progress.json')
if progress_file.exists():
    with open(progress_file) as f:
        data = json.load(f)
else:
    data = {'contacts': {}, 'months_processed': []}

contacts = data['contacts']

# Read input from stdin (will be piped from bash)
import sys
for line in sys.stdin:
    line = line.strip()
    if not line or not (':' in line):
        continue

    # Parse "From: Name <email>" or "To: Name <email>"
    if line.startswith('From:'):
        header = line[5:].strip()
        direction = 'received'
    elif line.startswith('To:'):
        header = line[3:].strip()
        direction = 'sent'
    else:
        continue

    email = extract_email(header)
    name = extract_name(header)

    if not email or is_automated(email):
        continue

    # Track contact
    if email not in contacts:
        contacts[email] = {'name': name, 'sent': 0, 'received': 0}

    contacts[email][direction] += 1

    # Update name if better
    if name and not contacts[email]['name']:
        contacts[email]['name'] = name

# Save progress
data['contacts'] = contacts
with open(progress_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Processed. Total contacts tracked: {len(contacts)}")
