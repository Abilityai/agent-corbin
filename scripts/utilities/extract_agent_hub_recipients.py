#!/usr/bin/env python3
"""Extract recipient names from Agent Hub delivery emails."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import json
import re
import time
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_PATH = Path.home() / '.config' / 'mcp' / 'google-workspace' / 'token.pickle'

def get_gmail_service():
    """Get authenticated Gmail service."""
    creds = None
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def extract_recipient_from_html(html_content):
    """Extract recipient name from HTML email content."""
    # Look for the greeting line
    match = re.search(r'Hi\s+([^,]+),', html_content)
    if match:
        return match.group(1).strip()
    return None

def extract_workflow_name(html_content):
    """Extract workflow name from email content."""
    match = re.search(r'<strong>([^<]+)</strong>\.\s+It\'s attached', html_content)
    if match:
        return match.group(1).strip()
    return None

def main():
    service = get_gmail_service()
    
    # Search for agent delivery emails
    query = 'from:me subject:"Ability AI Agent Hub" after:2024-01-01'
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=100
    ).execute()
    
    messages = results.get('messages', [])
    print(f"Found {len(messages)} agent delivery emails\n")
    
    recipients = []
    
    for i, msg in enumerate(messages, 1):
        try:
            # Get full message
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            # Extract HTML body
            html_body = None
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/html':
                        import base64
                        html_body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
            
            if html_body:
                recipient = extract_recipient_from_html(html_body)
                workflow = extract_workflow_name(html_body)
                
                if recipient and workflow:
                    recipients.append({
                        'name': recipient,
                        'workflow': workflow
                    })
                    print(f"{i}. {recipient} - {workflow}")
                else:
                    print(f"{i}. [Failed to extract: {msg['id']}]")
            
            # Small delay to avoid rate limits
            time.sleep(0.1)
            
        except Exception as e:
            print(f"{i}. Error processing {msg['id']}: {e}")
            time.sleep(1)  # Longer delay on error
            continue
    
    # Save results
    output_file = 'agent_hub_recipients.json'
    with open(output_file, 'w') as f:
        json.dump(recipients, f, indent=2)
    
    print(f"\n\nExtracted {len(recipients)} recipients")
    print(f"Results saved to {output_file}")
    
    # Print unique names
    unique_names = sorted(set(r['name'] for r in recipients))
    print(f"\n{len(unique_names)} unique recipients:")
    for name in unique_names:
        print(f"  - {name}")

if __name__ == '__main__':
    main()
