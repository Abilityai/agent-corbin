#!/usr/bin/env python3
"""
Complete Contact Sync Workflow
This script runs the complete workflow:
1. Extract contacts from email exchanges (last 6 months)
2. Add missing contacts to Google Contacts
3. Run the improved LinkedIn matcher
4. Generate comprehensive reports
"""

import os
import sys
from datetime import datetime

# Import our scripts
from extract_and_sync_email_contacts import EmailContactExtractor
from improved_contact_matcher import ImprovedContactMatcher


def main():
    print("="*80)
    print("COMPLETE CONTACT SYNCHRONIZATION WORKFLOW")
    print("="*80)
    print("\nThis workflow will:")
    print("1. Extract contacts from email exchanges (last 6 months)")
    print("2. Identify contacts with bidirectional communication")
    print("3. Add missing contacts to Google Contacts")
    print("4. Match Google Contacts with LinkedIn profiles")
    print("5. Generate comprehensive reports")
    print("\n" + "="*80)
    
    input("\nPress Enter to start the workflow...")
    
    # =========================================================================
    # STEP 1: Extract Email Contacts
    # =========================================================================
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "STEP 1: EMAIL CONTACT EXTRACTION" + " "*25 + "║")
    print("╚" + "="*78 + "╝")
    
    extractor = EmailContactExtractor()
    bidirectional, new_contacts, added_contacts = extractor.run(
        max_emails=5000,
        add_to_google=True
    )
    
    # =========================================================================
    # STEP 2: Match with LinkedIn
    # =========================================================================
    if added_contacts or True:  # Always run matcher
        print("\n\n")
        print("╔" + "="*78 + "╗")
        print("║" + " "*18 + "STEP 2: LINKEDIN CONTACT MATCHING" + " "*25 + "║")
        print("╚" + "="*78 + "╝")
        
        print("\nRunning improved contact matcher...")
        print("This will match Google Contacts (including newly added) with LinkedIn profiles\n")
        
        matcher = ImprovedContactMatcher()
        matcher.run(
            fuzzy_threshold=0.85,
            auto_match_threshold=0.95,
            interactive=False
        )
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*28 + "WORKFLOW COMPLETE" + " "*33 + "║")
    print("╚" + "="*78 + "╝")
    
    print("\n📊 FINAL SUMMARY:")
    print(f"\n  Email Analysis:")
    print(f"    • Bidirectional email contacts found: {len(bidirectional)}")
    print(f"    • New contacts added to Google: {len(added_contacts)}")
    
    print(f"\n  Files Generated:")
    print(f"    • Email bidirectional contacts report")
    print(f"    • New contacts added report")
    print(f"    • LinkedIn matching report")
    print(f"    • Needs review report (for manual verification)")
    
    print("\n  Next Steps:")
    print("    1. Review the 'needs_review_*.csv' file for potential matches")
    print("    2. Check 'email_new_contacts_added_*.csv' for newly added contacts")
    print("    3. Run the workflow periodically to keep contacts in sync")
    
    print("\n" + "="*80)
    print("All reports saved in: /Users/eugene/Dropbox/Coding/N8N_Main_repos/Corbin20/")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

