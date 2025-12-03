#!/usr/bin/env python3
"""
Sync Google Contacts to LinkedIn JSON files
This script:
1. Pulls all Google contacts
2. Matches them with existing LinkedIn JSON files
3. Adds Google contact information to the JSON files
4. Creates a report of unmatched contacts
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import csv
from collections import defaultdict

# Add the linkedin_lead_generation/src/gmail path to import the Google modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src'))

from gmail.google_workspace_client import GoogleWorkspaceClient

class GoogleContactsLinkedInSync:
    def __init__(self, linkedin_contacts_dir: str = None, credentials_path: str = None):
        """
        Initialize the sync tool
        
        Args:
            linkedin_contacts_dir: Directory containing LinkedIn JSON files
            credentials_path: Path to Google credentials file
        """
        self.linkedin_dir = Path(linkedin_contacts_dir or os.path.join(os.path.dirname(__file__), 'linkedin_contacts'))
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src', 'gmail', 'credentials.json'
        )
        
        # Initialize Google client
        self.google_client = GoogleWorkspaceClient(
            credentials_file=self.credentials_path,
            token_file=os.path.join(os.path.dirname(self.credentials_path), 'token.pickle')
        )
        
        # Storage for processing
        self.google_contacts = []
        self.linkedin_files = {}
        self.matched_contacts = []
        self.unmatched_google_contacts = []
        self.unmatched_linkedin_profiles = []
        
    def load_linkedin_files(self) -> Dict[str, Dict]:
        """Load all LinkedIn JSON files"""
        print(f"Loading LinkedIn files from {self.linkedin_dir}")
        
        for file_path in self.linkedin_dir.glob("*.json"):
            # Skip schema.json
            if file_path.name == "schema.json":
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.linkedin_files[file_path.name] = {
                        'path': file_path,
                        'data': data
                    }
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
        print(f"Loaded {len(self.linkedin_files)} LinkedIn profiles")
        return self.linkedin_files
    
    def fetch_google_contacts(self) -> List[Dict]:
        """Fetch all Google contacts"""
        print("Fetching Google contacts...")
        
        # Get all contacts with comprehensive fields
        contacts = self.google_client.contacts.list_contacts(
            read_mask='names,emailAddresses,phoneNumbers,organizations,addresses,biographies,urls,metadata'
        )
        
        # Export to simplified format
        self.google_contacts = self.google_client.contacts.export_contacts_to_dict(contacts)
        
        print(f"Fetched {len(self.google_contacts)} Google contacts")
        return self.google_contacts
    
    def normalize_name(self, name: str) -> str:
        """Normalize name for matching"""
        if not name:
            return ""
        # Remove extra spaces, convert to lower
        return re.sub(r'\s+', ' ', name.strip().lower())
    
    def extract_names_from_linkedin(self, linkedin_data: Dict) -> Tuple[str, str, str]:
        """Extract normalized names from LinkedIn data"""
        basic_profile = linkedin_data.get('basic_profile', {})
        
        first_name = basic_profile.get('first_name', '')
        last_name = basic_profile.get('last_name', '')
        full_name = basic_profile.get('full_name', '')
        
        return (
            self.normalize_name(first_name),
            self.normalize_name(last_name),
            self.normalize_name(full_name)
        )
    
    def extract_emails_from_linkedin(self, linkedin_data: Dict) -> List[str]:
        """Extract all possible emails from LinkedIn data"""
        emails = []
        
        # Check Apollo enrichment for email
        apollo = linkedin_data.get('apollo_enrichment', {})
        person_data = apollo.get('person_data', {})
        
        if person_data and isinstance(person_data, dict):
            email = person_data.get('email')
            if email:
                emails.append(email.lower())
        
        return emails
    
    def match_contacts(self) -> List[Dict]:
        """Match Google contacts with LinkedIn profiles"""
        print("\nMatching contacts...")
        
        # Create lookup indices for faster matching
        google_by_email = defaultdict(list)
        google_by_name = defaultdict(list)
        
        for gc in self.google_contacts:
            # Index by email
            for email in gc.get('emails', []):
                google_by_email[email.lower()].append(gc)
            
            # Index by normalized full name
            full_name = f"{gc.get('givenName', '')} {gc.get('familyName', '')}"
            normalized_name = self.normalize_name(full_name)
            if normalized_name:
                google_by_name[normalized_name].append(gc)
            
            # Also index by display name
            display_name = self.normalize_name(gc.get('displayName', ''))
            if display_name and display_name != normalized_name:
                google_by_name[display_name].append(gc)
        
        # Match LinkedIn profiles with Google contacts
        matched_google_ids = set()
        
        for filename, file_info in self.linkedin_files.items():
            linkedin_data = file_info['data']
            matched = False
            matched_google_contact = None
            
            # Extract LinkedIn info
            li_first, li_last, li_full = self.extract_names_from_linkedin(linkedin_data)
            li_emails = self.extract_emails_from_linkedin(linkedin_data)
            
            # Try to match by email first (most reliable)
            for email in li_emails:
                if email in google_by_email:
                    matched_google_contact = google_by_email[email][0]
                    matched = True
                    break
            
            # If no email match, try name matching
            if not matched:
                # Try full name match
                if li_full in google_by_name:
                    matched_google_contact = google_by_name[li_full][0]
                    matched = True
                elif li_first and li_last:
                    # Try first + last name
                    combined_name = f"{li_first} {li_last}"
                    if combined_name in google_by_name:
                        matched_google_contact = google_by_name[combined_name][0]
                        matched = True
                    else:
                        # Try last + first name (some cultures reverse order)
                        reversed_name = f"{li_last} {li_first}"
                        if reversed_name in google_by_name:
                            matched_google_contact = google_by_name[reversed_name][0]
                            matched = True
            
            if matched and matched_google_contact:
                matched_google_ids.add(matched_google_contact['resourceName'])
                self.matched_contacts.append({
                    'linkedin_file': filename,
                    'linkedin_name': linkedin_data['basic_profile'].get('full_name'),
                    'google_contact': matched_google_contact,
                    'match_confidence': 'high' if li_emails else 'medium'
                })
            else:
                self.unmatched_linkedin_profiles.append({
                    'file': filename,
                    'name': linkedin_data['basic_profile'].get('full_name'),
                    'headline': linkedin_data['basic_profile'].get('headline'),
                    'location': linkedin_data['basic_profile'].get('location')
                })
        
        # Find unmatched Google contacts
        for gc in self.google_contacts:
            if gc['resourceName'] not in matched_google_ids:
                self.unmatched_google_contacts.append(gc)
        
        print(f"Matched {len(self.matched_contacts)} contacts")
        print(f"Unmatched Google contacts: {len(self.unmatched_google_contacts)}")
        print(f"Unmatched LinkedIn profiles: {len(self.unmatched_linkedin_profiles)}")
        
        return self.matched_contacts
    
    def update_linkedin_files(self):
        """Update LinkedIn JSON files with Google contact information"""
        print("\nUpdating LinkedIn files with Google contact data...")
        
        for match in self.matched_contacts:
            file_name = match['linkedin_file']
            file_info = self.linkedin_files[file_name]
            linkedin_data = file_info['data']
            google_contact = match['google_contact']
            
            # Add Google contact information
            linkedin_data['google_contact'] = {
                'resource_name': google_contact.get('resourceName'),
                'etag': google_contact.get('etag'),
                'emails': google_contact.get('emails', []),
                'phones': google_contact.get('phones', []),
                'organization': google_contact.get('organization'),
                'job_title': google_contact.get('jobTitle'),
                'notes': google_contact.get('notes'),
                'synced_at': datetime.now().isoformat(),
                'match_confidence': match['match_confidence']
            }
            
            # Save updated file
            file_path = file_info['path']
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(linkedin_data, f, indent=2, ensure_ascii=False)
            
            print(f"Updated {file_name}")
    
    def create_unmatched_reports(self, report_dir: str = None):
        """Create reports for unmatched contacts"""
        report_dir = Path(report_dir or self.linkedin_dir.parent)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Report for unmatched Google contacts
        if self.unmatched_google_contacts:
            google_report_path = report_dir / f'unmatched_google_contacts_{timestamp}.csv'
            with open(google_report_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['displayName', 'givenName', 'familyName', 'emails', 'organization', 'jobTitle', 'phones', 'notes'])
                writer.writeheader()
                
                for gc in self.unmatched_google_contacts:
                    writer.writerow({
                        'displayName': gc.get('displayName', ''),
                        'givenName': gc.get('givenName', ''),
                        'familyName': gc.get('familyName', ''),
                        'emails': ', '.join(gc.get('emails', [])),
                        'organization': gc.get('organization', ''),
                        'jobTitle': gc.get('jobTitle', ''),
                        'phones': ', '.join(gc.get('phones', [])),
                        'notes': gc.get('notes', '')
                    })
            
            print(f"\nCreated unmatched Google contacts report: {google_report_path}")
        
        # Report for unmatched LinkedIn profiles
        if self.unmatched_linkedin_profiles:
            linkedin_report_path = report_dir / f'unmatched_linkedin_profiles_{timestamp}.csv'
            with open(linkedin_report_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['file', 'name', 'headline', 'location'])
                writer.writeheader()
                writer.writerows(self.unmatched_linkedin_profiles)
            
            print(f"Created unmatched LinkedIn profiles report: {linkedin_report_path}")
        
        # Create JSON files for unmatched Google contacts (for potential LinkedIn lookup)
        unmatched_dir = self.linkedin_dir / 'unmatched_google_contacts'
        unmatched_dir.mkdir(exist_ok=True)
        
        for gc in self.unmatched_google_contacts:
            # Create a filename from the contact name
            name = gc.get('displayName', '') or f"{gc.get('givenName', '')} {gc.get('familyName', '')}"
            name = name.strip()
            
            if name:
                # Clean name for filename
                filename = re.sub(r'[^\w\s-]', '', name.lower())
                filename = re.sub(r'[-\s]+', '-', filename)
                filename = f"{filename}.json"
                
                # Create a structure similar to LinkedIn files but with Google data
                google_contact_data = {
                    'source': 'google_contacts',
                    'fetchedAt': datetime.now().isoformat(),
                    'google_contact': gc,
                    'needs_linkedin_lookup': True,
                    'basic_profile': {
                        'full_name': name,
                        'first_name': gc.get('givenName', ''),
                        'last_name': gc.get('familyName', ''),
                        'headline': f"{gc.get('jobTitle', '')} at {gc.get('organization', '')}".strip(' at '),
                        'location': 'Unknown'
                    }
                }
                
                file_path = unmatched_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(google_contact_data, f, indent=2, ensure_ascii=False)
        
        if self.unmatched_google_contacts:
            print(f"Created {len(self.unmatched_google_contacts)} JSON files for unmatched Google contacts in {unmatched_dir}")
    
    def run(self):
        """Run the complete sync process"""
        print("Starting Google Contacts to LinkedIn sync...")
        print("=" * 50)
        
        # Load LinkedIn files
        self.load_linkedin_files()
        
        # Fetch Google contacts
        self.fetch_google_contacts()
        
        # Match contacts
        self.match_contacts()
        
        # Update LinkedIn files
        self.update_linkedin_files()
        
        # Create reports
        self.create_unmatched_reports()
        
        print("\nSync completed!")
        print(f"Total LinkedIn profiles: {len(self.linkedin_files)}")
        print(f"Total Google contacts: {len(self.google_contacts)}")
        print(f"Successfully matched: {len(self.matched_contacts)}")
        

if __name__ == "__main__":
    # Run the sync
    sync = GoogleContactsLinkedInSync()
    sync.run()
