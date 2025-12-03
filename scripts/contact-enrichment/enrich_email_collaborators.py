#!/usr/bin/env python3
"""
Email Collaborators Contact Enrichment Workflow
===============================================

This script identifies collaboration partners from Gmail, checks if they exist
in the contact database, and enriches them with LinkedIn and Apollo data.

Workflow:
1. Search Gmail for recent emails (last 90 days)
2. Extract sender email addresses and names
3. Filter out automated/marketing emails
4. Check if contact exists in linkedin_contacts/ database
5. If not, add to Google Contacts
6. Run sync to match with LinkedIn
7. Enrich with Apollo data
8. Generate report

Usage:
    python enrich_email_collaborators.py [--days 90] [--min-messages 2]
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime, timedelta
from collections import Counter
import re

# Add LinkedIn lead generation path for Google client
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src'))

from gmail.google_workspace_client import GoogleWorkspaceClient

class EmailCollaboratorEnricher:
    def __init__(self, linkedin_contacts_dir: str = None, credentials_path: str = None):
        """Initialize the enricher"""
        self.linkedin_dir = Path(linkedin_contacts_dir or os.path.join(os.path.dirname(__file__), 'linkedin_contacts'))
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src', 'gmail', 'credentials.json'
        )

        # Initialize Google client
        self.google_client = GoogleWorkspaceClient(
            credentials_file=self.credentials_path,
            token_file=os.path.join(os.path.dirname(self.credentials_path), 'token.pickle')
        )

        # Storage
        self.collaborators = {}  # email -> {name, count, recent_subjects}
        self.existing_contacts_emails = set()
        self.new_contacts = []

        # Filters for automated emails
        self.automated_domains = {
            'noreply', 'no-reply', 'donotreply', 'notifications',
            'automated', 'system', 'bounce', 'mailer-daemon',
            'support', 'help', 'info', 'hello', 'hi', 'team',
            'mail.beehiiv.com', 'substack.com', 'calendly.com',
            'linkedin.com', 'facebook.com', 'twitter.com',
            'calendar.google.com', 'e.read.ai'
        }

    def is_automated_email(self, email: str, sender_name: str = "") -> bool:
        """Check if email is automated/marketing"""
        email_lower = email.lower()

        # Check if contains automated keywords
        for keyword in self.automated_domains:
            if keyword in email_lower:
                return True

        # Check for common patterns
        if any(pattern in email_lower for pattern in [
            'notification', 'updates', 'news', 'digest',
            'alert', 'report', 'summary', 'newsletter'
        ]):
            return True

        return False

    def fetch_email_collaborators(self, days: int = 90, min_messages: int = 2):
        """Fetch email collaborators from Gmail"""
        print(f"Fetching emails from last {days} days...")

        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')

        # Search for emails (not from user)
        query = f"after:{since_date} -from:me"

        try:
            # Get message list
            messages = self.google_client.gmail.search_messages(query=query, max_results=500)

            print(f"Found {len(messages)} messages, analyzing senders...")

            # Process messages one by one
            for i, msg in enumerate(messages):
                if i % 50 == 0 and i > 0:
                    print(f"  Processed {i}/{len(messages)} messages...")

                # Get message metadata
                full_msg = self.google_client.gmail.get_message(message_id=msg['id'], format='metadata')

                if not full_msg:
                    continue

                headers = {h['name']: h['value'] for h in full_msg.get('payload', {}).get('headers', [])}

                from_header = headers.get('From', '')
                subject = headers.get('Subject', '')

                # Extract email and name from "Name <email>" format
                email_match = re.search(r'<(.+?)>', from_header)
                if email_match:
                    email = email_match.group(1).strip()
                    name = from_header[:from_header.index('<')].strip().strip('"')
                else:
                    email = from_header.strip()
                    name = ""

                # Skip if automated
                if self.is_automated_email(email, name):
                    continue

                # Track collaborator
                if email not in self.collaborators:
                    self.collaborators[email] = {
                        'name': name,
                        'count': 0,
                        'recent_subjects': []
                    }

                self.collaborators[email]['count'] += 1
                if len(self.collaborators[email]['recent_subjects']) < 3:
                    self.collaborators[email]['recent_subjects'].append(subject)

            # Filter by minimum message count
            self.collaborators = {
                email: data for email, data in self.collaborators.items()
                if data['count'] >= min_messages
            }

            print(f"Identified {len(self.collaborators)} collaboration partners")

        except Exception as e:
            print(f"Error fetching emails: {e}")
            return {}

        return self.collaborators

    def load_existing_contacts(self):
        """Load existing contacts from linkedin_contacts database"""
        print("Loading existing contact database...")

        for file_path in self.linkedin_dir.glob("*.json"):
            if file_path.name == "schema.json":
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Check google_contact field for emails
                    google_contact = data.get('google_contact', {})
                    if google_contact:
                        for email in google_contact.get('emails', []):
                            self.existing_contacts_emails.add(email.lower())

                    # Check Apollo enrichment for emails
                    apollo = data.get('apollo_enrichment', {})
                    person_data = apollo.get('person_data', {})
                    if person_data and isinstance(person_data, dict):
                        email = person_data.get('email')
                        if email:
                            self.existing_contacts_emails.add(email.lower())

            except Exception as e:
                pass  # Skip problematic files

        print(f"Loaded {len(self.existing_contacts_emails)} existing contact emails")

    def identify_new_contacts(self) -> List[Dict]:
        """Identify contacts that need to be added"""
        print("Identifying new contacts...")

        for email, data in self.collaborators.items():
            if email.lower() not in self.existing_contacts_emails:
                self.new_contacts.append({
                    'email': email,
                    'name': data['name'],
                    'message_count': data['count'],
                    'recent_subjects': data['recent_subjects']
                })

        print(f"Found {len(self.new_contacts)} new contacts to enrich")
        return self.new_contacts

    def add_to_google_contacts(self):
        """Add new contacts to Google Contacts"""
        if not self.new_contacts:
            print("No new contacts to add")
            return

        print(f"\nAdding {len(self.new_contacts)} contacts to Google Contacts...")

        added = 0
        for contact in self.new_contacts:
            try:
                # Parse name
                name_parts = contact['name'].split(' ', 1)
                given_name = name_parts[0] if name_parts else contact['email'].split('@')[0]
                family_name = name_parts[1] if len(name_parts) > 1 else ""

                # Create contact
                result = self.google_client.contacts.create_contact(
                    given_name=given_name,
                    family_name=family_name,
                    email=contact['email'],
                    notes=f"Added via email enrichment workflow. {contact['message_count']} messages exchanged."
                )

                if result:
                    added += 1
                    print(f"  ✓ Added: {contact['name']} <{contact['email']}>")

            except Exception as e:
                print(f"  ✗ Failed to add {contact['email']}: {e}")

        print(f"\nSuccessfully added {added}/{len(self.new_contacts)} contacts")

    def generate_report(self, output_dir: str = None):
        """Generate enrichment report"""
        output_dir = Path(output_dir or self.linkedin_dir.parent)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        report_path = output_dir / f'email_collaborator_enrichment_{timestamp}.json'

        report = {
            'generated_at': datetime.now().isoformat(),
            'total_collaborators': len(self.collaborators),
            'existing_in_database': len(self.collaborators) - len(self.new_contacts),
            'new_contacts_added': len(self.new_contacts),
            'collaborators': self.collaborators,
            'new_contacts': self.new_contacts
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nGenerated enrichment report: {report_path}")
        return report_path

    def run(self, days: int = 90, min_messages: int = 2):
        """Run the complete enrichment workflow"""
        print("=" * 60)
        print("Email Collaborators Contact Enrichment Workflow")
        print("=" * 60)

        # Step 1: Fetch email collaborators
        self.fetch_email_collaborators(days=days, min_messages=min_messages)

        # Step 2: Load existing contacts
        self.load_existing_contacts()

        # Step 3: Identify new contacts
        self.identify_new_contacts()

        # Step 4: Add to Google Contacts
        self.add_to_google_contacts()

        # Step 5: Generate report
        self.generate_report()

        print("\n" + "=" * 60)
        print("Enrichment completed!")
        print("=" * 60)
        print(f"Total collaborators found: {len(self.collaborators)}")
        print(f"Already in database: {len(self.collaborators) - len(self.new_contacts)}")
        print(f"New contacts added: {len(self.new_contacts)}")
        print("\nNext steps:")
        print("1. Run sync_google_contacts_to_linkedin.py to match with LinkedIn")
        print("2. Use /linkedin-lead-research for unmatched contacts")
        print("3. Use /apollo-campaign-manager to enrich with Apollo data")


def main():
    parser = argparse.ArgumentParser(description='Enrich email collaborators workflow')
    parser.add_argument('--days', type=int, default=90, help='Number of days to look back (default: 90)')
    parser.add_argument('--min-messages', type=int, default=2, help='Minimum messages to be considered collaborator (default: 2)')

    args = parser.parse_args()

    enricher = EmailCollaboratorEnricher()
    enricher.run(days=args.days, min_messages=args.min_messages)


if __name__ == "__main__":
    main()
