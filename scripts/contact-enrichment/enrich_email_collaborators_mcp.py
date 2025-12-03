#!/usr/bin/env python3
"""
Email Collaborators Contact Enrichment Workflow - MCP Version
==============================================================

This version uses Claude Code's Google Workspace MCP tools for better performance.
Run via Claude Code, not directly.

Workflow:
1. Search Gmail for recent emails (last 90 days)
2. Extract sender email addresses and names
3. Filter out automated/marketing emails
4. Check if contact exists in linkedin_contacts/ database
5. If not, report for manual addition to Google Contacts
6. Generate report

Usage (via Claude Code):
    Ask Claude: "Run the email collaborator enrichment with MCP"
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime, timedelta
from collections import Counter

class EmailCollaboratorEnricherMCP:
    def __init__(self, linkedin_contacts_dir: str = None):
        """Initialize the enricher"""
        self.linkedin_dir = Path(linkedin_contacts_dir or os.path.join(os.path.dirname(__file__), 'linkedin_contacts'))

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

    def parse_email_messages(self, messages_text: str):
        """Parse messages from MCP batch retrieval output"""
        # This would parse the output from mcp__google_workspace__get_gmail_messages_content_batch
        # For now, return parsed structure

        # Messages are in format:
        # === Message 1/N ===
        # Message ID: xyz
        # Thread ID: abc
        # From: Name <email>
        # Subject: ...
        # Date: ...

        messages = []
        current_msg = {}

        for line in messages_text.split('\n'):
            if line.startswith('=== Message'):
                if current_msg:
                    messages.append(current_msg)
                current_msg = {}
            elif line.startswith('From:'):
                current_msg['from'] = line.replace('From:', '').strip()
            elif line.startswith('Subject:'):
                current_msg['subject'] = line.replace('Subject:', '').strip()

        if current_msg:
            messages.append(current_msg)

        return messages

    def analyze_collaborators(self, messages: List[Dict], min_messages: int = 2):
        """Analyze messages to identify collaborators"""
        print(f"Analyzing {len(messages)} messages...")

        for msg in messages:
            from_header = msg.get('from', '')
            subject = msg.get('subject', '')

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

        print(f"Found {len(self.new_contacts)} new contacts to add")
        return self.new_contacts

    def generate_report(self, output_dir: str = None):
        """Generate enrichment report"""
        output_dir = Path(output_dir or self.linkedin_dir.parent)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        report_path = output_dir / f'email_collaborator_enrichment_{timestamp}.json'

        report = {
            'generated_at': datetime.now().isoformat(),
            'total_collaborators': len(self.collaborators),
            'existing_in_database': len(self.collaborators) - len(self.new_contacts),
            'new_contacts_to_add': len(self.new_contacts),
            'collaborators': self.collaborators,
            'new_contacts': self.new_contacts
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nGenerated enrichment report: {report_path}")
        return report_path


if __name__ == "__main__":
    print("This script is designed to be run via Claude Code with MCP tools.")
    print("Please ask Claude Code to run the email collaborator enrichment.")
