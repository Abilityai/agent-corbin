#!/usr/bin/env python3
"""
Continue Adding Email Contacts to Google
Picks up from saved CSV file and adds remaining contacts
"""

import os
import sys
import csv
from datetime import datetime
from pathlib import Path
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src'))

from gmail import GoogleWorkspaceClient


def load_contacts_from_csv(csv_path: str):
    """Load contacts from bidirectional CSV"""
    contacts = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['in_google_contacts'] == 'No':
                contacts.append({
                    'email': row['email'],
                    'name': row['name'],
                    'sent_count': int(row['sent_count']),
                    'received_count': int(row['received_count']),
                    'total_exchanges': int(row['total_exchanges']),
                    'thread_count': int(row['thread_count']),
                    'last_interaction': row['last_interaction'],
                    'first_interaction': row['first_interaction']
                })
    return contacts


def add_contacts_to_google(contacts_manager, contacts_to_add, batch_size=10):
    """Add contacts to Google Contacts with progress indicators"""
    
    print(f"\n{'='*80}")
    print(f"ADDING {len(contacts_to_add)} CONTACTS TO GOOGLE")
    print(f"{'='*80}\n")
    
    added = []
    failed = []
    
    for i, contact in enumerate(contacts_to_add):
        pct = ((i + 1) / len(contacts_to_add)) * 100
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
        if contact.get('last_interaction'):
            note += f"\nLast interaction: {contact['last_interaction']}"
        note += f"\nAdded automatically from email analysis on {datetime.now().strftime('%Y-%m-%d')}"
        
        try:
            created_contact = contacts_manager.create_contact(
                given_name=given_name,
                family_name=family_name,
                email=email,
                notes=note
            )
            
            if created_contact:
                print(f"  ✓ [{i+1}/{len(contacts_to_add)}] ({pct:.0f}%) Added: {name or email}")
                added.append(contact)
            else:
                print(f"  ✗ [{i+1}/{len(contacts_to_add)}] ({pct:.0f}%) Failed: {email}")
                failed.append(contact)
            
            # Rate limiting
            if (i + 1) % batch_size == 0:
                print(f"\n  ⏸  Pausing briefly (processed {i + 1}/{len(contacts_to_add)})...")
                time.sleep(2)
            
        except Exception as e:
            print(f"  ✗ [{i+1}/{len(contacts_to_add)}] ({pct:.0f}%) Error: {email} - {e}")
            failed.append(contact)
    
    print(f"\n{'='*80}")
    print(f"RESULTS:")
    print(f"  ✓ Successfully added: {len(added)}")
    print(f"  ✗ Failed: {len(failed)}")
    print(f"{'='*80}\n")
    
    return added, failed


def main(auto_confirm=False):
    # Find the most recent CSV file
    csv_dir = Path(os.path.dirname(__file__))
    csv_files = list(csv_dir.glob('email_bidirectional_contacts_*.csv'))
    
    if not csv_files:
        print("❌ No bidirectional contacts CSV file found!")
        print("   Please run extract_and_sync_email_contacts.py first")
        return
    
    # Use the most recent file
    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    
    print(f"{'='*80}")
    print(f"CONTINUE ADDING EMAIL CONTACTS TO GOOGLE")
    print(f"{'='*80}\n")
    print(f"Using CSV file: {latest_csv.name}\n")
    
    # Load contacts
    print("Loading contacts from CSV...")
    contacts_to_add = load_contacts_from_csv(latest_csv)
    
    print(f"Found {len(contacts_to_add)} contacts that need to be added to Google\n")
    
    if not contacts_to_add:
        print("✓ All contacts are already in Google Contacts!")
        return
    
    # Show top contacts
    print("Top 10 contacts by exchange count:")
    sorted_contacts = sorted(contacts_to_add, key=lambda x: x['total_exchanges'], reverse=True)
    for i, c in enumerate(sorted_contacts[:10], 1):
        print(f"  {i}. {c.get('name') or c['email'][:30]} - {c['total_exchanges']} exchanges")
    
    print(f"\n{'='*80}\n")
    
    # Ask for confirmation (or auto-confirm)
    if not auto_confirm:
        response = input(f"Add these {len(contacts_to_add)} contacts to Google Contacts? (y/n): ").strip().lower()
        
        if response != 'y':
            print("\n❌ Operation cancelled")
            return
    else:
        print(f"Auto-confirming: Adding {len(contacts_to_add)} contacts to Google Contacts...")
    
    # Initialize Google client
    credentials_path = os.path.join(
        os.path.dirname(__file__), '..', 'linkedin_lead_generation', 'src', 'gmail', 'credentials.json'
    )
    
    google_client = GoogleWorkspaceClient(
        credentials_file=credentials_path,
        token_file=os.path.join(os.path.dirname(credentials_path), 'token.pickle')
    )
    
    # Add contacts
    added, failed = add_contacts_to_google(google_client.contacts, contacts_to_add)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if added:
        added_path = csv_dir / f'contacts_successfully_added_{timestamp}.csv'
        with open(added_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['email', 'name', 'total_exchanges'])
            writer.writeheader()
            for contact in added:
                writer.writerow({
                    'email': contact['email'],
                    'name': contact.get('name', ''),
                    'total_exchanges': contact['total_exchanges']
                })
        print(f"✓ Saved successfully added contacts to: {added_path.name}")
    
    if failed:
        failed_path = csv_dir / f'contacts_failed_to_add_{timestamp}.csv'
        with open(failed_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['email', 'name', 'total_exchanges'])
            writer.writeheader()
            for contact in failed:
                writer.writerow({
                    'email': contact['email'],
                    'name': contact.get('name', ''),
                    'total_exchanges': contact['total_exchanges']
                })
        print(f"✗ Saved failed contacts to: {failed_path.name}")
    
    print(f"\n✓ Process complete!")
    
    # Ask if they want to run the LinkedIn matcher
    if added and not auto_confirm:
        print(f"\n{'='*80}")
        response = input(f"\nRun LinkedIn matcher for newly added contacts? (y/n): ").strip().lower()
        if response == 'y':
            print("\nRunning LinkedIn matcher...")
            os.system(f"cd {csv_dir} && python improved_contact_matcher.py")
    elif added and auto_confirm:
        print("\nNote: Run improved_contact_matcher.py separately to match with LinkedIn profiles")


if __name__ == "__main__":
    import sys
    # Check if --auto-confirm flag is passed
    auto = '--auto-confirm' in sys.argv or '-y' in sys.argv
    main(auto_confirm=auto)

