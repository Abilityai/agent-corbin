#!/usr/bin/env python3
"""
Manual matcher for specific contacts that need verification
"""

import json
from pathlib import Path
from datetime import datetime

# Define manual matches based on review
MANUAL_MATCHES = {
    # Google contact email -> LinkedIn filename
    'anton.polishko@gmail.com': 'antonpolishko.json',
    'lolejniczak@google.com': 'lukasz-olejniczak-phd-1a75a613.json',
    'markus@bynd.vc': 'markustb.json',
    # Add more as verified
}

def update_manual_matches():
    """Update LinkedIn files with manually verified Google contact matches"""
    linkedin_dir = Path('/Users/eugene/Dropbox/Coding/N8N_Main_repos/Corbin20/linkedin_contacts')
    
    # Load Google contacts to get full data
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src'))
    from gmail.google_workspace_client import GoogleWorkspaceClient
    
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src', 'gmail', 'credentials.json')
    google_client = GoogleWorkspaceClient(
        credentials_file=credentials_path,
        token_file=os.path.join(os.path.dirname(credentials_path), 'token.pickle')
    )
    
    contacts = google_client.contacts.list_contacts(
        read_mask='names,emailAddresses,phoneNumbers,organizations,addresses,biographies,urls,metadata'
    )
    
    google_contacts = google_client.contacts.export_contacts_to_dict(contacts)
    
    # Create lookup by email
    contacts_by_email = {}
    for gc in google_contacts:
        for email in gc.get('emails', []):
            contacts_by_email[email] = gc
    
    # Process matches
    updated = 0
    for email, linkedin_file in MANUAL_MATCHES.items():
        gc = contacts_by_email.get(email)
        if not gc:
            print(f"⚠️  Google contact not found for email: {email}")
            continue
        
        linkedin_path = linkedin_dir / linkedin_file
        if not linkedin_path.exists():
            print(f"⚠️  LinkedIn file not found: {linkedin_file}")
            continue
        
        # Load LinkedIn data
        with open(linkedin_path, 'r', encoding='utf-8') as f:
            linkedin_data = json.load(f)
        
        # Check if already has google_contact
        if 'google_contact' in linkedin_data:
            print(f"⊘  Already has Google contact: {linkedin_file}")
            continue
        
        # Add Google contact info
        linkedin_data['google_contact'] = {
            'resource_name': gc.get('resourceName'),
            'etag': gc.get('etag'),
            'emails': gc.get('emails', []),
            'phones': gc.get('phones', []),
            'organization': gc.get('organization'),
            'job_title': gc.get('jobTitle'),
            'notes': gc.get('notes'),
            'synced_at': datetime.now().isoformat(),
            'match_confidence': 'manual_verified',
            'confidence_score': 1.0
        }
        
        # Save
        with open(linkedin_path, 'w', encoding='utf-8') as f:
            json.dump(linkedin_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓  Updated {linkedin_file} with {gc.get('displayName', '')}")
        updated += 1
    
    print(f"\nManually matched and updated {updated} contacts")

if __name__ == "__main__":
    update_manual_matches()

