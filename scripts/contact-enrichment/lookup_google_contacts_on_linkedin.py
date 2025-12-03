#!/usr/bin/env python3
"""
Lookup Google Contacts on LinkedIn
This script reads the unmatched Google contacts and attempts to find them on LinkedIn
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import requests
import time
import re

class LinkedInLookup:
    def __init__(self, unmatched_dir: str = None):
        """
        Initialize LinkedIn lookup tool
        
        Args:
            unmatched_dir: Directory containing unmatched Google contact JSON files
        """
        self.unmatched_dir = Path(unmatched_dir or os.path.join(
            os.path.dirname(__file__), 'linkedin_contacts', 'unmatched_google_contacts'
        ))
        self.linkedin_dir = self.unmatched_dir.parent
        
    def clean_name_for_username(self, name: str) -> str:
        """Convert a name to potential LinkedIn username format"""
        # Remove special characters and convert to lowercase
        clean_name = re.sub(r'[^\w\s-]', '', name.lower())
        # Replace spaces with hyphens
        username = re.sub(r'\s+', '-', clean_name.strip())
        return username
    
    def generate_username_variations(self, first_name: str, last_name: str, full_name: str) -> List[str]:
        """Generate possible LinkedIn username variations"""
        variations = []
        
        # Clean names
        first = self.clean_name_for_username(first_name)
        last = self.clean_name_for_username(last_name)
        full = self.clean_name_for_username(full_name)
        
        if first and last:
            # Common patterns
            variations.extend([
                f"{first}-{last}",          # john-doe
                f"{first}{last}",           # johndoe
                f"{last}-{first}",          # doe-john
                f"{first}.{last}",          # john.doe
                f"{first[0]}{last}",        # jdoe
                f"{first}{last[0]}",        # johnd
            ])
            
            # With middle initial if present in full name
            parts = full_name.split()
            if len(parts) > 2:
                middle_initial = parts[1][0].lower()
                variations.extend([
                    f"{first}-{middle_initial}-{last}",
                    f"{first}{middle_initial}{last}"
                ])
        
        # Add the full name variation
        if full:
            variations.append(full)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for v in variations:
            if v and v not in seen:
                seen.add(v)
                unique_variations.append(v)
        
        return unique_variations
    
    def check_linkedin_username(self, username: str) -> Optional[Dict]:
        """
        Check if a LinkedIn username exists (placeholder for actual implementation)
        In production, this would need to use LinkedIn API or web scraping
        """
        # This is a placeholder - actual implementation would need LinkedIn API access
        # For now, just return None to indicate not found
        print(f"  Checking username: {username}")
        time.sleep(0.5)  # Rate limiting placeholder
        return None
    
    def lookup_contact(self, contact_file: Path) -> Optional[Dict]:
        """Attempt to find a Google contact on LinkedIn"""
        with open(contact_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        google_contact = data.get('google_contact', {})
        basic_profile = data.get('basic_profile', {})
        
        first_name = basic_profile.get('first_name', '')
        last_name = basic_profile.get('last_name', '')
        full_name = basic_profile.get('full_name', '')
        
        print(f"\nLooking up: {full_name}")
        print(f"  Organization: {google_contact.get('organization', 'N/A')}")
        print(f"  Job Title: {google_contact.get('jobTitle', 'N/A')}")
        
        # Generate username variations
        variations = self.generate_username_variations(first_name, last_name, full_name)
        
        # Try each variation
        for username in variations:
            result = self.check_linkedin_username(username)
            if result:
                return {
                    'username': username,
                    'profile_data': result,
                    'google_contact': google_contact
                }
        
        return None
    
    def process_all_unmatched(self):
        """Process all unmatched Google contacts"""
        if not self.unmatched_dir.exists():
            print(f"No unmatched contacts directory found at {self.unmatched_dir}")
            return
        
        json_files = list(self.unmatched_dir.glob("*.json"))
        print(f"Found {len(json_files)} unmatched Google contacts to lookup")
        
        found_contacts = []
        not_found_contacts = []
        
        for contact_file in json_files:
            result = self.lookup_contact(contact_file)
            
            if result:
                found_contacts.append(result)
                print(f"  ✓ Found LinkedIn profile: {result['username']}")
            else:
                not_found_contacts.append(contact_file.stem)
                print(f"  ✗ No LinkedIn profile found")
        
        # Summary
        print("\n" + "=" * 50)
        print(f"Lookup Summary:")
        print(f"  Total contacts processed: {len(json_files)}")
        print(f"  LinkedIn profiles found: {len(found_contacts)}")
        print(f"  Not found on LinkedIn: {len(not_found_contacts)}")
        
        # Save results
        if found_contacts:
            self.save_found_profiles(found_contacts)
        
        if not_found_contacts:
            self.save_not_found_report(not_found_contacts)
    
    def save_found_profiles(self, found_contacts: List[Dict]):
        """Save newly found LinkedIn profiles"""
        print("\nNote: To actually fetch LinkedIn profiles, you would need to:")
        print("1. Use LinkedIn API (requires approval)")
        print("2. Use a web scraping service")
        print("3. Manually visit the profiles and export data")
        
        # Create a report of found profiles
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.linkedin_dir.parent / f'found_linkedin_profiles_{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'found_profiles': found_contacts
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved found profiles report to: {report_path}")
    
    def save_not_found_report(self, not_found_contacts: List[str]):
        """Save report of contacts not found on LinkedIn"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.linkedin_dir.parent / f'linkedin_not_found_{timestamp}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("Google Contacts not found on LinkedIn:\n")
            f.write("=" * 50 + "\n")
            for contact in not_found_contacts:
                f.write(f"{contact}\n")
        
        print(f"Saved not found report to: {report_path}")


def main():
    print("LinkedIn Lookup Tool for Google Contacts")
    print("=" * 50)
    print("\nNOTE: This is a demonstration script that shows how to:")
    print("1. Generate LinkedIn username variations from names")
    print("2. Structure the lookup process")
    print("\nActual LinkedIn profile fetching would require additional implementation.")
    print("=" * 50)
    
    lookup = LinkedInLookup()
    lookup.process_all_unmatched()


if __name__ == "__main__":
    main()
