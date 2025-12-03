#!/usr/bin/env python3
"""
Smart Contact Finder - Lightweight Email Analysis
=================================================

Uses Gmail search operators to find contacts intelligently without loading
massive amounts of email content.

Strategy:
1. Search for emails using smart filters
2. Extract unique senders/recipients using metadata only
3. Track counts efficiently
4. Require 1+ sent AND 1+ received for true collaboration

Usage:
    python3 smart_contact_finder.py --months 6
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

def is_automated_email(email):
    """Check if email looks automated"""
    automated_patterns = [
        'noreply', 'no-reply', 'donotreply', 'notifications',
        'automated', 'system', 'bounce', 'mailer-daemon',
        'support@', 'help@', 'info@', 'hello@', 'hi@', 'team@',
        'beehiiv.com', 'substack.com', 'calendly.com',
        'linkedin.com', 'facebook.com', 'twitter.com',
        'calendar.google.com', 'e.read.ai', 'stripe.com',
        'notifications@', 'alerts@', 'updates@', 'news@',
        'digest@', 'newsletter@', 'unsubscribe'
    ]
    email_lower = email.lower()
    return any(pattern in email_lower for pattern in automated_patterns)

def extract_email_from_header(header):
    """Extract email from 'Name <email>' format"""
    match = re.search(r'<(.+?)>', header)
    if match:
        return match.group(1).strip()
    return header.strip()

def load_existing_contacts():
    """Load existing contacts from linkedin_contacts database"""
    linkedin_dir = Path("linkedin_contacts")
    existing_emails = set()

    if not linkedin_dir.exists():
        print("Warning: linkedin_contacts directory not found")
        return existing_emails

    for file_path in linkedin_dir.glob("*.json"):
        if file_path.name == "schema.json":
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check google_contact emails
            gc = data.get('google_contact', {})
            if gc:
                for email in gc.get('emails', []):
                    existing_emails.add(email.lower())

            # Check apollo emails
            apollo = data.get('apollo_enrichment', {})
            pd = apollo.get('person_data', {})
            if pd and isinstance(pd, dict):
                email = pd.get('email')
                if email:
                    existing_emails.add(email.lower())
        except:
            pass

    return existing_emails

def analyze_contacts_from_file(input_file):
    """
    Analyze contacts from a JSON file containing email metadata.

    Expected format from Claude's MCP search:
    {
        "received_emails": [{"from": "Name <email>", ...}, ...],
        "sent_emails": [{"to": "Name <email>", ...}, ...]
    }
    """

    with open(input_file, 'r') as f:
        data = json.load(f)

    contacts = defaultdict(lambda: {"name": "", "sent": 0, "received": 0})

    # Process received emails
    for email_data in data.get('received_emails', []):
        from_header = email_data.get('from', '')
        email = extract_email_from_header(from_header)

        if not email or is_automated_email(email):
            continue

        contacts[email]['received'] += 1

        # Extract name if available
        if '<' in from_header:
            name = from_header.split('<')[0].strip().strip('"')
            if name and not contacts[email]['name']:
                contacts[email]['name'] = name

    # Process sent emails
    for email_data in data.get('sent_emails', []):
        to_header = email_data.get('to', '')
        email = extract_email_from_header(to_header)

        if not email or is_automated_email(email):
            continue

        contacts[email]['sent'] += 1

        # Extract name if available
        if '<' in to_header:
            name = to_header.split('<')[0].strip().strip('"')
            if name and not contacts[email]['name']:
                contacts[email]['name'] = name

    return contacts

def generate_report(contacts, output_file="collaborators_report.json"):
    """Generate final report"""

    # Filter for true collaborators
    collaborators = {
        email: info for email, info in contacts.items()
        if info['sent'] >= 1 and info['received'] >= 1
    }

    # Load existing contacts from database
    existing_emails = load_existing_contacts()

    # Separate new vs existing
    new_contacts = []
    existing_contacts = []

    for email, info in collaborators.items():
        contact_info = {
            'email': email,
            'name': info['name'],
            'sent_count': info['sent'],
            'received_count': info['received'],
            'total_exchanges': info['sent'] + info['received']
        }

        if email.lower() in existing_emails:
            existing_contacts.append(contact_info)
        else:
            new_contacts.append(contact_info)

    # Sort by exchange volume
    new_contacts.sort(key=lambda x: x['total_exchanges'], reverse=True)
    existing_contacts.sort(key=lambda x: x['total_exchanges'], reverse=True)

    # Generate report
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_contacts_tracked': len(contacts),
        'true_collaborators': len(collaborators),
        'new_contacts': len(new_contacts),
        'existing_in_database': len(existing_contacts),
        'new_contacts_list': new_contacts[:50],  # Top 50
        'existing_contacts_list': existing_contacts[:20]  # Top 20
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print("CONTACT ENRICHMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Total contacts tracked: {len(contacts)}")
    print(f"True collaborators (1+ sent & 1+ received): {len(collaborators)}")
    print(f"New contacts to add: {len(new_contacts)}")
    print(f"Already in database: {len(existing_contacts)}")

    if new_contacts:
        print(f"\nTop 10 new contacts by exchange volume:")
        for i, contact in enumerate(new_contacts[:10], 1):
            name = contact['name'] or '(No name)'
            print(f"  {i}. {name} <{contact['email']}>")
            print(f"     Exchanges: {contact['total_exchanges']} " +
                  f"(sent: {contact['sent_count']}, received: {contact['received_count']})")

    print(f"\n✓ Full report saved to: {output_file}")
    print(f"{'='*60}\n")

    return report

def main():
    parser = argparse.ArgumentParser(description='Smart contact finder from email analysis')
    parser.add_argument('--input', type=str, default='email_metadata.json',
                        help='Input JSON file with email metadata from Claude MCP search')
    parser.add_argument('--output', type=str, default=None,
                        help='Output report file')

    args = parser.parse_args()

    # Check if input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found")
        print("\nThis script expects a JSON file with email metadata.")
        print("Run Claude MCP email search first to generate the metadata file.")
        sys.exit(1)

    # Generate output filename with timestamp if not specified
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'collaborators_report_{timestamp}.json'

    print("Smart Contact Finder")
    print("="*60)
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print()

    # Analyze contacts
    print("Analyzing contacts...")
    contacts = analyze_contacts_from_file(args.input)
    print(f"✓ Found {len(contacts)} unique contacts")

    # Generate report
    generate_report(contacts, args.output)

if __name__ == "__main__":
    main()
