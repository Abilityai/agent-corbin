#!/usr/bin/env python3
"""
Batch Email Collaborator Enrichment - Efficient Context-Aware Version
====================================================================

Strategy:
1. Process emails in small batches (100 at a time)
2. Track both sent and received emails
3. Require at least 1 sent + 1 received for true collaboration
4. Save progress incrementally to avoid context overload
5. Cover 6 months in manageable time windows

Usage:
    python batch_email_enrichment.py [--batch-size 100] [--months 6]
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime, timedelta
import re

# Add LinkedIn lead generation path for Google client
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src'))

from gmail.google_workspace_client import GoogleWorkspaceClient

class BatchEmailEnricher:
    def __init__(self, linkedin_contacts_dir: str = None, credentials_path: str = None):
        """Initialize the batch enricher"""
        self.linkedin_dir = Path(linkedin_contacts_dir or os.path.join(os.path.dirname(__file__), 'linkedin_contacts'))
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src', 'gmail', 'credentials.json'
        )

        # Initialize Google client
        self.google_client = GoogleWorkspaceClient(
            credentials_file=self.credentials_path,
            token_file=os.path.join(os.path.dirname(self.credentials_path), 'token.pickle')
        )

        # Progress file
        self.progress_file = Path('email_enrichment_progress.json')

        # Load or initialize progress
        self.progress = self.load_progress()

        # Filters for automated emails
        self.automated_keywords = {
            'noreply', 'no-reply', 'donotreply', 'notifications',
            'automated', 'system', 'bounce', 'mailer-daemon',
            'support', 'help', 'info', 'hello', 'hi', 'team',
            'mail.beehiiv.com', 'substack.com', 'calendly.com',
            'linkedin.com', 'facebook.com', 'twitter.com',
            'calendar.google.com', 'e.read.ai', 'notification',
            'updates', 'news', 'digest', 'alert', 'report',
            'summary', 'newsletter'
        }

    def load_progress(self) -> Dict:
        """Load progress from file or create new"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)

        return {
            'started_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'contacts': {},  # email -> {name, sent_count, received_count, subjects}
            'batches_processed': 0,
            'total_emails_scanned': 0,
            'current_date_pointer': None
        }

    def save_progress(self):
        """Save progress to file"""
        self.progress['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
        print(f"✓ Progress saved: {len(self.progress['contacts'])} contacts tracked")

    def is_automated_email(self, email: str) -> bool:
        """Check if email is automated/marketing"""
        email_lower = email.lower()
        return any(keyword in email_lower for keyword in self.automated_keywords)

    def extract_email_and_name(self, from_header: str) -> tuple:
        """Extract email and name from From header"""
        email_match = re.search(r'<(.+?)>', from_header)
        if email_match:
            email = email_match.group(1).strip()
            name = from_header[:from_header.index('<')].strip().strip('"')
        else:
            email = from_header.strip()
            name = ""
        return email, name

    def process_batch(self, query: str, batch_size: int, is_sent: bool = False) -> int:
        """Process a batch of emails"""
        direction = "sent" if is_sent else "received"
        print(f"\n📧 Processing {direction} emails...")

        try:
            # Search emails
            messages = self.google_client.gmail.search_messages(query=query, max_results=batch_size)

            if not messages:
                print(f"  No {direction} messages found")
                return 0

            print(f"  Found {len(messages)} {direction} messages, analyzing...")

            # Process messages
            processed = 0
            for i, msg in enumerate(messages):
                if i % 20 == 0 and i > 0:
                    print(f"    Processed {i}/{len(messages)}...")

                # Get message metadata
                full_msg = self.google_client.gmail.get_message(message_id=msg['id'], format='metadata')
                if not full_msg:
                    continue

                headers = {h['name']: h['value'] for h in full_msg.get('payload', {}).get('headers', [])}

                # Extract relevant contact
                if is_sent:
                    # For sent emails, look at To field
                    to_header = headers.get('To', '')
                    if not to_header:
                        continue
                    email, name = self.extract_email_and_name(to_header)
                else:
                    # For received emails, look at From field
                    from_header = headers.get('From', '')
                    if not from_header:
                        continue
                    email, name = self.extract_email_and_name(from_header)

                # Skip automated emails
                if self.is_automated_email(email):
                    continue

                subject = headers.get('Subject', '')

                # Track contact
                if email not in self.progress['contacts']:
                    self.progress['contacts'][email] = {
                        'name': name,
                        'sent_count': 0,
                        'received_count': 0,
                        'subjects': []
                    }

                # Update counts
                if is_sent:
                    self.progress['contacts'][email]['sent_count'] += 1
                else:
                    self.progress['contacts'][email]['received_count'] += 1

                # Update name if we got a better one
                if name and not self.progress['contacts'][email]['name']:
                    self.progress['contacts'][email]['name'] = name

                # Add subject (keep last 3)
                if len(self.progress['contacts'][email]['subjects']) < 3:
                    self.progress['contacts'][email]['subjects'].append(subject)

                processed += 1

            self.progress['total_emails_scanned'] += processed
            return processed

        except Exception as e:
            print(f"  ✗ Error processing batch: {e}")
            return 0

    def run_batch_enrichment(self, months: int = 6, batch_size: int = 100):
        """Run batch enrichment over time period"""
        print("=" * 70)
        print("Batch Email Collaborator Enrichment")
        print("=" * 70)
        print(f"Time period: Last {months} months")
        print(f"Batch size: {batch_size} emails per batch")
        print(f"Strategy: 1 sent + 1 received = true collaboration")
        print()

        # Calculate time windows (process by month)
        end_date = datetime.now()

        for month_offset in range(months):
            # Calculate date range for this month
            period_end = end_date - timedelta(days=30 * month_offset)
            period_start = period_end - timedelta(days=30)

            start_str = period_start.strftime('%Y/%m/%d')
            end_str = period_end.strftime('%Y/%m/%d')

            print(f"\n{'='*70}")
            print(f"Processing: {start_str} to {end_str}")
            print(f"{'='*70}")

            # Process received emails for this period
            received_query = f"after:{start_str} before:{end_str} -from:me"
            received_count = self.process_batch(received_query, batch_size, is_sent=False)

            # Process sent emails for this period
            sent_query = f"after:{start_str} before:{end_str} from:me"
            sent_count = self.process_batch(sent_query, batch_size, is_sent=True)

            # Update progress
            self.progress['batches_processed'] += 1
            self.progress['current_date_pointer'] = start_str
            self.save_progress()

            # Show stats for this period
            print(f"\n  Period stats:")
            print(f"    Received: {received_count} emails")
            print(f"    Sent: {sent_count} emails")
            print(f"    Total contacts tracked: {len(self.progress['contacts'])}")

        # Final filtering: require 1 sent + 1 received
        print(f"\n{'='*70}")
        print("Filtering for true collaborators (1+ sent AND 1+ received)...")
        print(f"{'='*70}")

        true_collaborators = {
            email: data for email, data in self.progress['contacts'].items()
            if data['sent_count'] >= 1 and data['received_count'] >= 1
        }

        print(f"\n✓ Found {len(true_collaborators)} true collaborators")
        print(f"  (filtered from {len(self.progress['contacts'])} total contacts)")

        # Save final collaborators list
        self.save_collaborators_list(true_collaborators)

        return true_collaborators

    def save_collaborators_list(self, collaborators: Dict):
        """Save final collaborators list"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path(f'collaborators_list_{timestamp}.json')

        # Load existing contacts from database
        existing_emails = self.load_existing_contacts_emails()

        # Separate new vs existing
        new_contacts = []
        existing_contacts = []

        for email, data in collaborators.items():
            contact_info = {
                'email': email,
                'name': data['name'],
                'sent_count': data['sent_count'],
                'received_count': data['received_count'],
                'total_exchanges': data['sent_count'] + data['received_count'],
                'subjects': data['subjects']
            }

            if email.lower() in existing_emails:
                existing_contacts.append(contact_info)
            else:
                new_contacts.append(contact_info)

        # Sort by total exchanges
        new_contacts.sort(key=lambda x: x['total_exchanges'], reverse=True)
        existing_contacts.sort(key=lambda x: x['total_exchanges'], reverse=True)

        report = {
            'generated_at': datetime.now().isoformat(),
            'total_collaborators': len(collaborators),
            'new_contacts': len(new_contacts),
            'existing_in_database': len(existing_contacts),
            'new_contacts_list': new_contacts,
            'existing_contacts_list': existing_contacts
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved collaborators report: {output_file}")
        print(f"\n{'='*70}")
        print("Summary:")
        print(f"{'='*70}")
        print(f"Total true collaborators: {len(collaborators)}")
        print(f"New contacts to add: {len(new_contacts)}")
        print(f"Already in database: {len(existing_contacts)}")

        if new_contacts:
            print(f"\nTop 10 new contacts by exchange volume:")
            for i, contact in enumerate(new_contacts[:10], 1):
                print(f"  {i}. {contact['name']} <{contact['email']}>")
                print(f"     Exchanges: {contact['total_exchanges']} (sent: {contact['sent_count']}, received: {contact['received_count']})")

        return output_file

    def load_existing_contacts_emails(self) -> Set[str]:
        """Load existing contact emails from database"""
        existing_emails = set()

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
                            existing_emails.add(email.lower())

                    # Check Apollo enrichment for emails
                    apollo = data.get('apollo_enrichment', {})
                    person_data = apollo.get('person_data', {})
                    if person_data and isinstance(person_data, dict):
                        email = person_data.get('email')
                        if email:
                            existing_emails.add(email.lower())
            except:
                pass

        return existing_emails


def main():
    parser = argparse.ArgumentParser(description='Batch email collaborator enrichment')
    parser.add_argument('--months', type=int, default=6, help='Number of months to look back (default: 6)')
    parser.add_argument('--batch-size', type=int, default=100, help='Emails per batch (default: 100)')
    parser.add_argument('--resume', action='store_true', help='Resume from saved progress')

    args = parser.parse_args()

    enricher = BatchEmailEnricher()

    if args.resume and enricher.progress_file.exists():
        print("Resuming from saved progress...")
        print(f"Previous progress: {enricher.progress['batches_processed']} batches processed")

    enricher.run_batch_enrichment(months=args.months, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
