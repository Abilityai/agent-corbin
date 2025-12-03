#!/usr/bin/env python3
"""
Batch Email Collaborator Enrichment - MCP Version
=================================================

This version is designed to work WITH Claude Code using MCP tools.
Claude orchestrates the email searches and this script handles processing.

Strategy:
1. Claude searches emails in batches using MCP
2. This script processes results and tracks progress
3. Requires 1 sent + 1 received for true collaboration
4. Saves progress incrementally

Usage:
    Run via Claude Code - this is a helper script for data processing
"""

import json
import os
from pathlib import Path
from typing import Dict, Set
from datetime import datetime
import re

class BatchEmailProcessor:
    def __init__(self, linkedin_contacts_dir: str = None):
        """Initialize the processor"""
        self.linkedin_dir = Path(linkedin_contacts_dir or os.path.join(os.path.dirname(__file__), 'linkedin_contacts'))
        self.progress_file = Path('email_enrichment_progress.json')
        self.progress = self.load_progress()

        self.automated_keywords = {
            'noreply', 'no-reply', 'donotreply', 'notifications',
            'automated', 'system', 'bounce', 'mailer-daemon',
            'support', 'help', 'info', 'hello', 'hi', 'team',
            'mail.beehiiv.com', 'substack.com', 'calendly.com',
            'linkedin.com', 'facebook.com', 'twitter.com',
            'calendar.google.com', 'e.read.ai', 'notification',
            'updates', 'news', 'digest', 'alert', 'report',
            'summary', 'newsletter', 'unsubscribe'
        }

    def load_progress(self) -> Dict:
        """Load progress from file"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)

        return {
            'started_at': datetime.now().isoformat(),
            'contacts': {},
            'batches_processed': 0
        }

    def save_progress(self):
        """Save progress"""
        self.progress['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def is_automated(self, email: str) -> bool:
        """Check if email is automated"""
        return any(k in email.lower() for k in self.automated_keywords)

    def extract_email_name(self, header: str) -> tuple:
        """Extract email and name"""
        match = re.search(r'<(.+?)>', header)
        if match:
            email = match.group(1).strip()
            name = header[:header.index('<')].strip().strip('"')
        else:
            email = header.strip()
            name = ""
        return email, name

    def process_messages(self, messages_data: str, is_sent: bool = False):
        """Process batch of messages from MCP output"""
        lines = messages_data.strip().split('\n')

        processed = 0
        for line in lines:
            if 'From:' in line or 'To:' in line:
                # Extract header
                if is_sent and 'To:' in line:
                    header = line.split('To:', 1)[1].strip()
                elif not is_sent and 'From:' in line:
                    header = line.split('From:', 1)[1].strip()
                else:
                    continue

                email, name = self.extract_email_name(header)

                if self.is_automated(email):
                    continue

                # Track
                if email not in self.progress['contacts']:
                    self.progress['contacts'][email] = {
                        'name': name,
                        'sent': 0,
                        'received': 0
                    }

                if is_sent:
                    self.progress['contacts'][email]['sent'] += 1
                else:
                    self.progress['contacts'][email]['received'] += 1

                if name and not self.progress['contacts'][email]['name']:
                    self.progress['contacts'][email]['name'] = name

                processed += 1

        self.progress['batches_processed'] += 1
        self.save_progress()
        return processed

    def get_true_collaborators(self) -> Dict:
        """Filter for 1+ sent AND 1+ received"""
        return {
            email: data for email, data in self.progress['contacts'].items()
            if data['sent'] >= 1 and data['received'] >= 1
        }

    def load_existing_emails(self) -> Set[str]:
        """Load existing contact emails"""
        existing = set()
        for file_path in self.linkedin_dir.glob("*.json"):
            if file_path.name == "schema.json":
                continue
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    gc = data.get('google_contact', {})
                    if gc:
                        for e in gc.get('emails', []):
                            existing.add(e.lower())
                    apollo = data.get('apollo_enrichment', {})
                    pd = apollo.get('person_data', {})
                    if pd and isinstance(pd, dict):
                        e = pd.get('email')
                        if e:
                            existing.add(e.lower())
            except:
                pass
        return existing

    def generate_report(self):
        """Generate final report"""
        collaborators = self.get_true_collaborators()
        existing_emails = self.load_existing_emails()

        new = []
        existing = []

        for email, data in collaborators.items():
            info = {
                'email': email,
                'name': data['name'],
                'sent': data['sent'],
                'received': data['received'],
                'total': data['sent'] + data['received']
            }

            if email.lower() in existing_emails:
                existing.append(info)
            else:
                new.append(info)

        new.sort(key=lambda x: x['total'], reverse=True)
        existing.sort(key=lambda x: x['total'], reverse=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = Path(f'collaborators_report_{timestamp}.json')

        report = {
            'generated_at': datetime.now().isoformat(),
            'total_contacts_tracked': len(self.progress['contacts']),
            'true_collaborators': len(collaborators),
            'new_contacts': len(new),
            'existing_in_database': len(existing),
            'new_contacts_list': new,
            'existing_contacts_list': existing
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        return report_file, report


if __name__ == "__main__":
    print("This is a helper script for Claude Code MCP-based enrichment")
    print("Run via Claude Code, not standalone")
