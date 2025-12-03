# Google Contacts to LinkedIn Sync

This system synchronizes your Google Contacts with LinkedIn profile data stored in JSON files, creating a centralized contact information repository.

## Overview

The sync process:
1. Fetches all Google Contacts
2. Matches them with existing LinkedIn JSON profiles
3. Adds Google contact information to matched LinkedIn files
4. Creates reports for unmatched contacts
5. Provides tools to lookup unmatched Google contacts on LinkedIn

## Prerequisites

1. Google API credentials (`credentials.json`) with access to:
   - Google Contacts API
   - Gmail API (for the existing gmail functionality)

2. Python packages:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

## File Structure

```
Corbin20/
├── linkedin_contacts/           # LinkedIn profile JSON files
│   ├── *.json                  # Individual profile files
│   ├── schema.json            # JSON schema for profile structure
│   └── unmatched_google_contacts/  # Created by sync script
├── sync_google_contacts_to_linkedin.py
├── lookup_google_contacts_on_linkedin.py
└── GOOGLE_CONTACTS_SYNC_README.md
```

## Usage

### Step 1: Sync Google Contacts with LinkedIn Profiles

Run the sync script to match and merge Google Contacts with LinkedIn profiles:

```bash
python sync_google_contacts_to_linkedin.py
```

This will:
- Load all LinkedIn JSON files from `linkedin_contacts/`
- Fetch all your Google Contacts
- Match contacts by email and name
- Add Google contact info to matched LinkedIn files
- Create CSV reports for unmatched contacts
- Create JSON files for unmatched Google contacts

### Step 2: Review Results

After syncing, check:

1. **Updated LinkedIn files**: Now contain a `google_contact` section:
   ```json
   {
     "username": "johndoe",
     "basic_profile": {...},
     "google_contact": {
       "resource_name": "people/c123456",
       "emails": ["john@example.com"],
       "phones": ["+1234567890"],
       "organization": "Example Corp",
       "job_title": "CEO",
       "notes": "Met at conference 2023",
       "synced_at": "2025-10-30T12:00:00",
       "match_confidence": "high"
     }
   }
   ```

2. **Reports generated**:
   - `unmatched_google_contacts_[timestamp].csv` - Google contacts without LinkedIn matches
   - `unmatched_linkedin_profiles_[timestamp].csv` - LinkedIn profiles without Google matches
   - `linkedin_contacts/unmatched_google_contacts/*.json` - Individual files for Google contacts

### Step 3: Lookup Unmatched Contacts (Optional)

For Google contacts not found in your LinkedIn files:

```bash
python lookup_google_contacts_on_linkedin.py
```

This demonstrates how to:
- Generate LinkedIn username variations from names
- Structure a lookup process

**Note**: Actual LinkedIn profile fetching requires additional implementation using:
- LinkedIn API (requires approval)
- Web scraping services
- Manual profile export

## Matching Logic

The sync script matches contacts using:

1. **Email matching** (highest confidence):
   - Compares Google contact emails with Apollo enrichment emails in LinkedIn data

2. **Name matching** (medium confidence):
   - Full name exact match
   - First + Last name combination
   - Last + First name (for different cultural naming orders)
   - All comparisons are case-insensitive and normalized

## Data Flow

```
Google Contacts API
      ↓
Fetch all contacts
      ↓
Match with LinkedIn JSONs ──→ Unmatched → Create report + JSON files
      ↓                                           ↓
Update LinkedIn JSONs                    Lookup on LinkedIn (manual/API)
      ↓                                           ↓
Centralized contact data                  New LinkedIn profiles
```

## Customization

### Modify matching logic

Edit the `match_contacts()` method in `sync_google_contacts_to_linkedin.py` to:
- Add fuzzy matching
- Include company matching
- Add confidence scoring

### Add more Google contact fields

Update the `fetch_google_contacts()` method to request additional fields:
```python
read_mask='names,emailAddresses,phoneNumbers,organizations,addresses,biographies,urls,metadata,events,relations'
```

### Change file locations

Initialize the sync with custom paths:
```python
sync = GoogleContactsLinkedInSync(
    linkedin_contacts_dir='/path/to/linkedin/files',
    credentials_path='/path/to/credentials.json'
)
```

## Troubleshooting

1. **Authentication issues**: 
   - Ensure `credentials.json` exists
   - Delete `token.pickle` to re-authenticate
   - Check OAuth scopes include contacts access

2. **No matches found**:
   - Verify email addresses in Apollo enrichment data
   - Check name formatting differences
   - Review unmatched reports for patterns

3. **File encoding issues**:
   - All files use UTF-8 encoding
   - JSON files preserve Unicode characters

## Security Notes

- `credentials.json` and `token.pickle` contain sensitive auth data
- Add them to `.gitignore`
- Google contact data includes personal information
- Store synced files securely

## Future Enhancements

1. Add LinkedIn API integration for automatic profile lookup
2. Implement fuzzy name matching for better match rates
3. Add bi-directional sync (LinkedIn → Google Contacts)
4. Create web interface for manual matching
5. Add incremental sync capability
6. Support for contact groups/tags synchronization
