#!/usr/bin/env python3
"""
Extract Email Contacts and Sync with Google Contacts
This script:
1. Finds all contacts with bidirectional email exchanges (sent + received) in the last 6 months
2. Compares with existing Google Contacts
3. Adds missing contacts to Google Contacts
4. Re-runs the LinkedIn sync
"""

import os
import sys
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re
from collections import defaultdict

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src'))

from gmail import GoogleWorkspaceClient


class EmailContactExtractor:
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src', 'gmail', 'credentials.json'
        )
        
        self.google_client = GoogleWorkspaceClient(
            credentials_file=self.credentials_path,
            token_file=os.path.join(os.path.dirname(self.credentials_path), 'token.pickle')
        )
        
        self.gmail = self.google_client.gmail
        self.contacts_manager = self.google_client.contacts
        
        self.my_emails = set()
        self.email_conversations = defaultdict(lambda: {
            'email': None,
            'name': None,
            'sent_count': 0,
            'received_count': 0,
            'last_interaction': None,
            'first_interaction': None,
            'thread_ids': set()
        })
        
        self.existing_contacts = {}
        self.new_contacts_to_add = []
        
    def extract_email_address(self, email_string: str) -> str:
        """Extract clean email address from string like 'Name <email@domain.com>'"""
        if not email_string:
            return None
        match = re.search(r'<(.+?)>', email_string)
        if match:
            return match.group(1).lower().strip()
        return email_string.strip().lower()
    
    def extract_name_from_email(self, email_string: str) -> str:
        """Extract name from email string like 'Name <email@domain.com>'"""
        if not email_string:
            return None
        if '<' in email_string:
            name = email_string.split('<')[0].strip()
            name = name.strip('"').strip("'")
            return name if name else None
        return None
    
    def get_my_email_addresses(self) -> Set[str]:
        """Get all email addresses associated with the account"""
        profile = self.gmail.get_profile()
        if profile and 'emailAddress' in profile:
            my_email = profile['emailAddress'].lower()
            self.my_emails.add(my_email)
            
            # Add common aliases
            if '@' in my_email:
                username, domain = my_email.split('@')
                if domain == 'gmail.com':
                    self.my_emails.add(f"{username}@googlemail.com")
        
        print(f"My email addresses: {self.my_emails}")
        return self.my_emails
    
    def get_header_value(self, headers: List[Dict], name: str) -> str:
        """Get header value by name"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return None
    
    def analyze_emails_last_6_months(self, max_results: int = 5000):
        """Analyze emails from the last 6 months"""
        print("\n" + "="*80)
        print("ANALYZING EMAIL EXCHANGES (Last 6 Months)")
        print("="*80)
        
        # Get my email addresses
        self.get_my_email_addresses()
        
        # Calculate date 6 months ago
        six_months_ago = datetime.now() - timedelta(days=180)
        date_str = six_months_ago.strftime('%Y/%m/%d')
        
        # Query for emails after the date
        query = f'after:{date_str}'
        
        print(f"\nFetching emails after {date_str}...")
        messages = self.gmail.list_messages(query=query, max_results=max_results)
        
        print(f"Found {len(messages)} messages to analyze\n")
        
        processed = 0
        for i, msg_ref in enumerate(messages):
            if i % 100 == 0 and i > 0:
                pct = (i / len(messages)) * 100
                print(f"  Processed {i}/{len(messages)} messages ({pct:.1f}%) - Found {len(self.email_conversations)} contacts so far...")
            
            try:
                msg = self.gmail.get_message(msg_ref['id'], format='metadata')
                if not msg:
                    continue
                
                headers = msg.get('payload', {}).get('headers', [])
                
                # Get relevant headers
                from_header = self.get_header_value(headers, 'From')
                to_header = self.get_header_value(headers, 'To')
                cc_header = self.get_header_value(headers, 'Cc')
                date_header = self.get_header_value(headers, 'Date')
                
                # Parse date
                msg_date = None
                if date_header:
                    try:
                        msg_date = datetime.strptime(date_header.split('(')[0].strip(), 
                                                     '%a, %d %b %Y %H:%M:%S %z')
                    except:
                        try:
                            msg_date = datetime.strptime(date_header.split('+')[0].strip(),
                                                         '%a, %d %b %Y %H:%M:%S')
                        except:
                            pass
                
                # Extract from email
                from_email = self.extract_email_address(from_header)
                from_name = self.extract_name_from_email(from_header)
                
                # Check if this is a sent or received email
                is_sent = from_email in self.my_emails
                
                # Process recipients for sent emails
                if is_sent:
                    recipients = []
                    if to_header:
                        recipients.extend([r.strip() for r in to_header.split(',')])
                    if cc_header:
                        recipients.extend([r.strip() for r in cc_header.split(',')])
                    
                    for recipient in recipients:
                        email = self.extract_email_address(recipient)
                        if email and email not in self.my_emails:
                            name = self.extract_name_from_email(recipient)
                            
                            self.email_conversations[email]['email'] = email
                            if name and not self.email_conversations[email]['name']:
                                self.email_conversations[email]['name'] = name
                            self.email_conversations[email]['sent_count'] += 1
                            self.email_conversations[email]['thread_ids'].add(msg.get('threadId'))
                            
                            if msg_date:
                                if (not self.email_conversations[email]['last_interaction'] or 
                                    msg_date > self.email_conversations[email]['last_interaction']):
                                    self.email_conversations[email]['last_interaction'] = msg_date
                                
                                if (not self.email_conversations[email]['first_interaction'] or
                                    msg_date < self.email_conversations[email]['first_interaction']):
                                    self.email_conversations[email]['first_interaction'] = msg_date
                
                # Process sender for received emails
                else:
                    if from_email and from_email not in self.my_emails:
                        self.email_conversations[from_email]['email'] = from_email
                        if from_name and not self.email_conversations[from_email]['name']:
                            self.email_conversations[from_email]['name'] = from_name
                        self.email_conversations[from_email]['received_count'] += 1
                        self.email_conversations[from_email]['thread_ids'].add(msg.get('threadId'))
                        
                        if msg_date:
                            if (not self.email_conversations[from_email]['last_interaction'] or
                                msg_date > self.email_conversations[from_email]['last_interaction']):
                                self.email_conversations[from_email]['last_interaction'] = msg_date
                            
                            if (not self.email_conversations[from_email]['first_interaction'] or
                                msg_date < self.email_conversations[from_email]['first_interaction']):
                                self.email_conversations[from_email]['first_interaction'] = msg_date
                
                processed += 1
                
            except Exception as e:
                print(f"  Error processing message {msg_ref['id']}: {e}")
                continue
        
        print(f"\n✓ Processed {processed} messages")
        print(f"✓ Found {len(self.email_conversations)} unique email contacts")
    
    def filter_bidirectional_contacts(self) -> List[Dict]:
        """Filter contacts with bidirectional exchanges (sent AND received)"""
        bidirectional = []
        
        for email, data in self.email_conversations.items():
            if data['sent_count'] > 0 and data['received_count'] > 0:
                bidirectional.append({
                    'email': email,
                    'name': data['name'],
                    'sent_count': data['sent_count'],
                    'received_count': data['received_count'],
                    'total_exchanges': data['sent_count'] + data['received_count'],
                    'thread_count': len(data['thread_ids']),
                    'last_interaction': data['last_interaction'],
                    'first_interaction': data['first_interaction']
                })
        
        # Sort by total exchanges
        bidirectional.sort(key=lambda x: x['total_exchanges'], reverse=True)
        
        print(f"\n✓ Found {len(bidirectional)} contacts with bidirectional exchanges")
        return bidirectional
    
    def load_existing_google_contacts(self):
        """Load existing Google Contacts"""
        print("\n" + "="*80)
        print("LOADING EXISTING GOOGLE CONTACTS")
        print("="*80)
        
        contacts = self.contacts_manager.list_contacts(
            read_mask='names,emailAddresses,phoneNumbers,organizations,addresses,biographies,urls,metadata'
        )
        
        exported = self.contacts_manager.export_contacts_to_dict(contacts)
        
        # Create lookup by email
        for contact in exported:
            for email in contact.get('emails', []):
                self.existing_contacts[email.lower()] = contact
        
        print(f"✓ Loaded {len(exported)} existing Google Contacts")
        print(f"✓ Indexed {len(self.existing_contacts)} unique email addresses")
    
    def identify_new_contacts(self, bidirectional_contacts: List[Dict]) -> List[Dict]:
        """Identify contacts not in Google Contacts"""
        new_contacts = []
        
        for contact in bidirectional_contacts:
            email = contact['email']
            if email not in self.existing_contacts:
                new_contacts.append(contact)
        
        print(f"\n✓ Found {len(new_contacts)} new contacts not in Google Contacts")
        return new_contacts
    
    def add_contacts_to_google(self, new_contacts: List[Dict], batch_size: int = 10):
        """Add new contacts to Google Contacts"""
        if not new_contacts:
            print("\nNo new contacts to add")
            return []
        
        print("\n" + "="*80)
        print(f"ADDING {len(new_contacts)} NEW CONTACTS TO GOOGLE CONTACTS")
        print("="*80)
        
        added_contacts = []
        
        print(f"\n  Starting to add contacts...")
        for i, contact in enumerate(new_contacts):
            pct = ((i + 1) / len(new_contacts)) * 100
            email = contact['email']
            name = contact.get('name', '')
            
            # Parse name
            if name:
                parts = name.split()
                given_name = parts[0] if parts else email.split('@')[0]
                family_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
            else:
                given_name = email.split('@')[0]
                family_name = ''
            
            # Create note with context
            note = f"Email contact - {contact['total_exchanges']} exchanges (sent: {contact['sent_count']}, received: {contact['received_count']})"
            if contact['last_interaction']:
                note += f"\nLast interaction: {contact['last_interaction'].strftime('%Y-%m-%d')}"
            note += f"\nAdded automatically from email analysis on {datetime.now().strftime('%Y-%m-%d')}"
            
            try:
                created_contact = self.contacts_manager.create_contact(
                    given_name=given_name,
                    family_name=family_name,
                    email=email,
                    notes=note
                )
                
                if created_contact:
                    print(f"  ✓ [{i+1}/{len(new_contacts)}] ({pct:.0f}%) Added: {name or email}")
                    added_contacts.append({
                        'email': email,
                        'name': name,
                        'google_contact': created_contact
                    })
                else:
                    print(f"  ✗ Failed to add: {email}")
                
                # Rate limiting
                if (i + 1) % batch_size == 0:
                    print(f"\n  Pausing briefly (added {i + 1}/{len(new_contacts)})...")
                    import time
                    time.sleep(2)
                
            except Exception as e:
                print(f"  ✗ Error adding {email}: {e}")
        
        print(f"\n✓ Successfully added {len(added_contacts)} contacts to Google Contacts")
        return added_contacts
    
    def save_reports(self, bidirectional_contacts: List[Dict], new_contacts: List[Dict]):
        """Save analysis reports"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = Path(os.path.dirname(__file__))
        
        # All bidirectional contacts
        all_contacts_path = report_dir / f'email_bidirectional_contacts_{timestamp}.csv'
        with open(all_contacts_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'email', 'name', 'sent_count', 'received_count', 'total_exchanges',
                'thread_count', 'last_interaction', 'first_interaction', 'in_google_contacts'
            ])
            writer.writeheader()
            
            for contact in bidirectional_contacts:
                writer.writerow({
                    'email': contact['email'],
                    'name': contact.get('name', ''),
                    'sent_count': contact['sent_count'],
                    'received_count': contact['received_count'],
                    'total_exchanges': contact['total_exchanges'],
                    'thread_count': contact['thread_count'],
                    'last_interaction': contact['last_interaction'].strftime('%Y-%m-%d %H:%M:%S') if contact['last_interaction'] else '',
                    'first_interaction': contact['first_interaction'].strftime('%Y-%m-%d %H:%M:%S') if contact['first_interaction'] else '',
                    'in_google_contacts': 'Yes' if contact['email'] in self.existing_contacts else 'No'
                })
        
        print(f"\n✓ Saved all bidirectional contacts to: {all_contacts_path}")
        
        # New contacts to add
        if new_contacts:
            new_contacts_path = report_dir / f'email_new_contacts_to_add_{timestamp}.csv'
            with open(new_contacts_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'email', 'name', 'sent_count', 'received_count', 'total_exchanges',
                    'thread_count', 'last_interaction', 'first_interaction'
                ])
                writer.writeheader()
                
                for contact in new_contacts:
                    writer.writerow({
                        'email': contact['email'],
                        'name': contact.get('name', ''),
                        'sent_count': contact['sent_count'],
                        'received_count': contact['received_count'],
                        'total_exchanges': contact['total_exchanges'],
                        'thread_count': contact['thread_count'],
                        'last_interaction': contact['last_interaction'].strftime('%Y-%m-%d %H:%M:%S') if contact.get('last_interaction') else '',
                        'first_interaction': contact['first_interaction'].strftime('%Y-%m-%d %H:%M:%S') if contact.get('first_interaction') else ''
                    })
            
            print(f"✓ Saved new contacts to add to: {new_contacts_path}")
    
    def run(self, max_emails: int = 5000, add_to_google: bool = True):
        """Run the complete extraction and sync process"""
        print("\n" + "="*80)
        print("EMAIL CONTACT EXTRACTION AND SYNC")
        print("="*80)
        
        # Step 1: Analyze emails
        self.analyze_emails_last_6_months(max_results=max_emails)
        
        # Step 2: Filter bidirectional contacts
        bidirectional_contacts = self.filter_bidirectional_contacts()
        
        # Step 3: Load existing Google Contacts
        self.load_existing_google_contacts()
        
        # Step 4: Identify new contacts
        new_contacts = self.identify_new_contacts(bidirectional_contacts)
        
        # Step 5: Save reports
        self.save_reports(bidirectional_contacts, new_contacts)
        
        # Step 6: Add to Google Contacts if requested
        added_contacts = []
        if add_to_google and new_contacts:
            response = input(f"\nAdd {len(new_contacts)} new contacts to Google Contacts? (y/n): ").strip().lower()
            if response == 'y':
                added_contacts = self.add_contacts_to_google(new_contacts)
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total bidirectional email contacts: {len(bidirectional_contacts)}")
        print(f"Already in Google Contacts: {len(bidirectional_contacts) - len(new_contacts)}")
        print(f"New contacts found: {len(new_contacts)}")
        print(f"New contacts added: {len(added_contacts)}")
        print("="*80)
        
        return bidirectional_contacts, new_contacts, added_contacts


if __name__ == "__main__":
    extractor = EmailContactExtractor()
    extractor.run(max_emails=5000, add_to_google=True)

