#!/usr/bin/env python3
"""
Improved Contact Matcher with Fuzzy Matching and Manual Verification
"""

import json
import os
import sys
import re
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'linkedin_lead_generation', 'src'))

from gmail.google_workspace_client import GoogleWorkspaceClient


class ImprovedContactMatcher:
    def __init__(self, linkedin_contacts_dir: str = None, credentials_path: str = None):
        self.linkedin_dir = Path(linkedin_contacts_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'linkedin_contacts'))
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'linkedin_lead_generation', 'src', 'gmail', 'credentials.json'
        )
        
        self.google_client = GoogleWorkspaceClient(
            credentials_file=self.credentials_path,
            token_file=os.path.join(os.path.dirname(self.credentials_path), 'token.pickle')
        )
        
        self.google_contacts = []
        self.linkedin_files = {}
        self.new_matches = []
        
    def similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""
        # Remove extra spaces, punctuation
        name = re.sub(r'[^\w\s]', '', name)
        return re.sub(r'\s+', ' ', name.strip().lower())
    
    def load_linkedin_files(self):
        """Load all LinkedIn JSON files"""
        print(f"Loading LinkedIn files from {self.linkedin_dir}")
        
        for file_path in self.linkedin_dir.glob("*.json"):
            if file_path.name == "schema.json":
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Skip if already has google_contact
                    if 'google_contact' not in data:
                        self.linkedin_files[file_path.name] = {
                            'path': file_path,
                            'data': data
                        }
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(self.linkedin_files)} LinkedIn profiles without Google contacts")
    
    def fetch_google_contacts(self):
        """Fetch unmatched Google contacts"""
        print("Fetching Google contacts...")
        
        contacts = self.google_client.contacts.list_contacts(
            read_mask='names,emailAddresses,phoneNumbers,organizations,addresses,biographies,urls,metadata'
        )
        
        self.google_contacts = self.google_client.contacts.export_contacts_to_dict(contacts)
        print(f"Fetched {len(self.google_contacts)} Google contacts")
    
    def fuzzy_match_by_name(self, google_contact: Dict, threshold: float = 0.85) -> List[Tuple[str, float, Dict]]:
        """Find potential matches using fuzzy name matching"""
        matches = []
        
        gc_first = self.normalize_name(google_contact.get('givenName', ''))
        gc_last = self.normalize_name(google_contact.get('familyName', ''))
        gc_full = self.normalize_name(google_contact.get('displayName', ''))
        
        for filename, file_info in self.linkedin_files.items():
            linkedin_data = file_info['data']
            basic_profile = linkedin_data.get('basic_profile', {})
            
            li_first = self.normalize_name(basic_profile.get('first_name', ''))
            li_last = self.normalize_name(basic_profile.get('last_name', ''))
            li_full = self.normalize_name(basic_profile.get('full_name', ''))
            
            # Calculate various similarity scores
            scores = []
            
            # Full name match
            if gc_full and li_full:
                scores.append(self.similarity_score(gc_full, li_full))
            
            # First + Last match
            if gc_first and gc_last and li_first and li_last:
                gc_combined = f"{gc_first} {gc_last}"
                li_combined = f"{li_first} {li_last}"
                scores.append(self.similarity_score(gc_combined, li_combined))
                
                # Also try reversed
                li_reversed = f"{li_last} {li_first}"
                scores.append(self.similarity_score(gc_combined, li_reversed))
            
            # Last name match (important for unique surnames)
            if gc_last and li_last:
                last_score = self.similarity_score(gc_last, li_last)
                if last_score > 0.9:  # High confidence on last name
                    scores.append(last_score * 1.1)  # Boost the score
            
            if scores:
                max_score = max(scores)
                if max_score >= threshold:
                    matches.append((filename, max_score, linkedin_data))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def match_by_organization(self, google_contact: Dict) -> List[Tuple[str, str]]:
        """Find potential matches by organization"""
        matches = []
        
        gc_org = self.normalize_name(google_contact.get('organization', ''))
        if not gc_org or len(gc_org) < 3:
            return matches
        
        for filename, file_info in self.linkedin_files.items():
            linkedin_data = file_info['data']
            
            # Check top position
            top_pos = linkedin_data.get('top_position', {})
            top_desc = self.normalize_name(top_pos.get('description', ''))
            
            # Check headline
            basic_profile = linkedin_data.get('basic_profile', {})
            headline = self.normalize_name(basic_profile.get('headline', ''))
            
            # Check Apollo organization
            apollo = linkedin_data.get('apollo_enrichment', {})
            person_data = apollo.get('person_data', {})
            if isinstance(person_data, dict):
                org_data = person_data.get('organization', {})
                if isinstance(org_data, dict):
                    apollo_org = self.normalize_name(org_data.get('name', ''))
                    if gc_org in apollo_org or apollo_org in gc_org:
                        matches.append((filename, apollo_org))
            
            # Search in headline and description
            if gc_org in headline or gc_org in top_desc:
                matches.append((filename, headline or top_desc))
        
        return matches
    
    def manual_review_match(self, google_contact: Dict, linkedin_data: Dict) -> bool:
        """Display contact info for manual review"""
        print("\n" + "="*80)
        print("POTENTIAL MATCH - Please review:")
        print("="*80)
        
        print("\n📧 GOOGLE CONTACT:")
        print(f"  Name: {google_contact.get('displayName', '')}")
        print(f"  Emails: {', '.join(google_contact.get('emails', []))}")
        print(f"  Organization: {google_contact.get('organization', 'N/A')}")
        print(f"  Job Title: {google_contact.get('jobTitle', 'N/A')}")
        notes = google_contact.get('notes', '')
        if notes:
            print(f"  Notes: {notes[:200]}...")
        
        print("\n🔗 LINKEDIN PROFILE:")
        basic = linkedin_data.get('basic_profile', {})
        print(f"  Name: {basic.get('full_name', '')}")
        print(f"  Headline: {basic.get('headline', '')[:100]}")
        print(f"  Location: {basic.get('location', 'N/A')}")
        
        apollo = linkedin_data.get('apollo_enrichment', {})
        person_data = apollo.get('person_data', {})
        if isinstance(person_data, dict):
            print(f"  Apollo Email: {person_data.get('email', 'N/A')}")
            org = person_data.get('organization', {})
            if isinstance(org, dict):
                print(f"  Apollo Organization: {org.get('name', 'N/A')}")
        
        print("\n" + "="*80)
        response = input("Is this a match? (y/n/skip): ").strip().lower()
        
        if response == 'y':
            return True
        elif response == 's' or response == 'skip':
            return None  # Skip this contact
        return False
    
    def find_and_match_contacts(self, fuzzy_threshold: float = 0.85, auto_match_threshold: float = 0.95, interactive: bool = False):
        """Find and match contacts with optional manual review"""
        print("\n" + "="*80)
        print("IMPROVED CONTACT MATCHING")
        print("="*80)
        
        processed = 0
        auto_matched = 0
        manually_matched = 0
        skipped = 0
        needs_review = []
        
        for gc in self.google_contacts:
            # Skip if already in new matches
            if any(m['google_contact']['resourceName'] == gc['resourceName'] for m in self.new_matches):
                continue
            
            display_name = gc.get('displayName', '')
            print(f"\nProcessing: {display_name}")
            processed += 1
            
            # Try fuzzy name matching
            name_matches = self.fuzzy_match_by_name(gc, threshold=fuzzy_threshold)
            
            if name_matches:
                best_match = name_matches[0]
                filename, score, linkedin_data = best_match
                
                print(f"  Found fuzzy match: {filename} (score: {score:.2f})")
                
                # Auto-match if score is very high
                if score >= auto_match_threshold:
                    print(f"  ✓ Auto-matched (high confidence)")
                    self.new_matches.append({
                        'linkedin_file': filename,
                        'google_contact': gc,
                        'match_method': 'fuzzy_name_auto',
                        'confidence_score': score
                    })
                    auto_matched += 1
                    continue
                
                # For non-interactive mode, save for review
                if not interactive:
                    print(f"  → Needs review (medium confidence)")
                    needs_review.append({
                        'google_contact': gc,
                        'linkedin_file': filename,
                        'linkedin_data': linkedin_data,
                        'confidence_score': score,
                        'match_type': 'fuzzy_name'
                    })
                else:
                    # Manual review for lower confidence matches
                    review_result = self.manual_review_match(gc, linkedin_data)
                    
                    if review_result is True:
                        self.new_matches.append({
                            'linkedin_file': filename,
                            'google_contact': gc,
                            'match_method': 'fuzzy_name_manual',
                            'confidence_score': score
                        })
                        manually_matched += 1
                    elif review_result is None:
                        print("  ⊘ Skipped")
                        skipped += 1
            else:
                # Try organization match
                org_matches = self.match_by_organization(gc)
                if org_matches:
                    print(f"  Found {len(org_matches)} organization matches")
                    filename, org_name = org_matches[0]
                    file_info = self.linkedin_files.get(filename)
                    if file_info:
                        if not interactive:
                            print(f"  → Needs review (organization match)")
                            needs_review.append({
                                'google_contact': gc,
                                'linkedin_file': filename,
                                'linkedin_data': file_info['data'],
                                'confidence_score': 0.75,
                                'match_type': 'organization'
                            })
                        else:
                            review_result = self.manual_review_match(gc, file_info['data'])
                            if review_result is True:
                                self.new_matches.append({
                                    'linkedin_file': filename,
                                    'google_contact': gc,
                                    'match_method': 'organization_manual',
                                    'confidence_score': 0.75
                                })
                                manually_matched += 1
        
        # Save needs review to file
        if needs_review:
            self.save_review_file(needs_review)
        
        print("\n" + "="*80)
        print("MATCHING SUMMARY:")
        print(f"  Processed: {processed}")
        print(f"  Auto-matched: {auto_matched}")
        print(f"  Manually matched: {manually_matched}")
        print(f"  Needs review: {len(needs_review)}")
        print(f"  Skipped: {skipped}")
        print(f"  Total new matches: {len(self.new_matches)}")
        print("="*80)
    
    def save_review_file(self, needs_review: List[Dict]):
        """Save potential matches that need manual review"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        review_path = self.linkedin_dir.parent / f'needs_review_{timestamp}.csv'
        
        with open(review_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'google_name', 'google_emails', 'google_org', 'google_notes',
                'linkedin_file', 'linkedin_name', 'linkedin_headline', 'linkedin_location',
                'confidence_score', 'match_type'
            ])
            writer.writeheader()
            
            for item in needs_review:
                gc = item['google_contact']
                linkedin_data = item['linkedin_data']
                basic = linkedin_data.get('basic_profile', {})
                
                writer.writerow({
                    'google_name': gc.get('displayName', ''),
                    'google_emails': ', '.join(gc.get('emails', [])),
                    'google_org': gc.get('organization', ''),
                    'google_notes': (gc.get('notes', '') or '')[:100],
                    'linkedin_file': item['linkedin_file'],
                    'linkedin_name': basic.get('full_name', ''),
                    'linkedin_headline': (basic.get('headline', '') or '')[:100],
                    'linkedin_location': basic.get('location', ''),
                    'confidence_score': item['confidence_score'],
                    'match_type': item['match_type']
                })
        
        print(f"\nSaved {len(needs_review)} potential matches for review: {review_path}")
    
    def update_linkedin_files(self):
        """Update LinkedIn files with new Google contact matches"""
        if not self.new_matches:
            print("No new matches to update")
            return
        
        print(f"\nUpdating {len(self.new_matches)} LinkedIn files...")
        
        for match in self.new_matches:
            filename = match['linkedin_file']
            gc = match['google_contact']
            
            file_info = self.linkedin_files.get(filename)
            if not file_info:
                continue
            
            linkedin_data = file_info['data']
            
            # Add Google contact information
            linkedin_data['google_contact'] = {
                'resource_name': gc.get('resourceName'),
                'etag': gc.get('etag'),
                'emails': gc.get('emails', []),
                'phones': gc.get('phones', []),
                'organization': gc.get('organization'),
                'job_title': gc.get('jobTitle'),
                'notes': gc.get('notes'),
                'synced_at': datetime.now().isoformat(),
                'match_confidence': match['match_method'],
                'confidence_score': match.get('confidence_score', 0)
            }
            
            # Save
            with open(file_info['path'], 'w', encoding='utf-8') as f:
                json.dump(linkedin_data, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Updated {filename}")
        
        # Create report
        self.create_match_report()
    
    def create_match_report(self):
        """Create a report of new matches"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.linkedin_dir.parent / f'new_matches_report_{timestamp}.csv'
        
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'linkedin_file', 'google_name', 'linkedin_name', 'emails', 
                'match_method', 'confidence_score'
            ])
            writer.writeheader()
            
            for match in self.new_matches:
                gc = match['google_contact']
                filename = match['linkedin_file']
                file_info = self.linkedin_files.get(filename)
                
                if file_info:
                    linkedin_data = file_info['data']
                    basic = linkedin_data.get('basic_profile', {})
                    
                    writer.writerow({
                        'linkedin_file': filename,
                        'google_name': gc.get('displayName', ''),
                        'linkedin_name': basic.get('full_name', ''),
                        'emails': ', '.join(gc.get('emails', [])),
                        'match_method': match['match_method'],
                        'confidence_score': match.get('confidence_score', 0)
                    })
        
        print(f"\nCreated match report: {report_path}")
    
    def run(self, fuzzy_threshold: float = 0.85, auto_match_threshold: float = 0.95, interactive: bool = False):
        """Run the improved matching process"""
        print("Starting Improved Contact Matching...")
        
        self.load_linkedin_files()
        self.fetch_google_contacts()
        self.find_and_match_contacts(fuzzy_threshold, auto_match_threshold, interactive)
        self.update_linkedin_files()
        
        print("\nMatching completed!")


if __name__ == "__main__":
    matcher = ImprovedContactMatcher()
    # Run in non-interactive mode by default
    matcher.run(fuzzy_threshold=0.85, auto_match_threshold=0.95, interactive=False)

