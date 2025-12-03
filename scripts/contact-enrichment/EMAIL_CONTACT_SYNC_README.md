# Email Contact Extraction and Sync Workflow

This workflow automatically extracts contacts from your email exchanges and syncs them with Google Contacts and LinkedIn profiles.

## Overview

The system performs the following steps:
1. **Analyzes Gmail** for the last 6 months
2. **Identifies bidirectional contacts** (contacts you've both sent to and received from)
3. **Compares with Google Contacts** to find missing contacts
4. **Adds new contacts** to Google Contacts
5. **Matches with LinkedIn profiles** using fuzzy matching
6. **Generates comprehensive reports**

## Why Bidirectional Exchanges?

We only extract contacts where there was **at least one sent AND one received message** because:
- These represent actual relationships, not just mailing lists or newsletters
- Reduces noise from automated emails and spam
- Focuses on contacts you actively communicate with
- More likely to have LinkedIn profiles and be relevant connections

## Usage

### Quick Start - Complete Workflow

Run the entire workflow in one go:

```bash
python complete_contact_sync_workflow.py
```

This will:
1. Extract email contacts (interactive prompts for adding to Google)
2. Match with LinkedIn profiles automatically
3. Generate all reports

### Individual Scripts

#### 1. Extract Email Contacts Only

```bash
python extract_and_sync_email_contacts.py
```

**What it does:**
- Analyzes last 6 months of email (default: 5000 messages)
- Finds contacts with bidirectional exchanges
- Compares with existing Google Contacts
- Prompts to add new contacts to Google
- Saves reports

**Configuration:**
```python
extractor = EmailContactExtractor()
extractor.run(
    max_emails=5000,        # Number of emails to analyze
    add_to_google=True      # Prompt to add new contacts
)
```

#### 2. Match with LinkedIn (After Adding Contacts)

```bash
python improved_contact_matcher.py
```

Runs the fuzzy matcher to find LinkedIn profiles for Google Contacts.

## Reports Generated

### 1. Email Bidirectional Contacts Report
**File**: `email_bidirectional_contacts_[timestamp].csv`

Contains all contacts with bidirectional exchanges:
- Email address
- Name (if available)
- Sent count
- Received count
- Total exchanges
- Thread count
- Last interaction date
- First interaction date
- Whether in Google Contacts

### 2. New Contacts Added
**File**: `email_new_contacts_added_[timestamp].csv`

Lists contacts that were added to Google Contacts:
- Email
- Name
- Exchange statistics

### 3. LinkedIn Matches
**File**: `new_matches_report_[timestamp].csv`

Shows LinkedIn profiles matched with Google Contacts.

### 4. Needs Review
**File**: `needs_review_[timestamp].csv`

Potential matches requiring manual verification.

## How Contacts Are Added to Google

When new contacts are found, they are added with:

```
Given Name: First name from email or email username
Family Name: Remaining parts of name
Email: Email address
Notes: 
  - Exchange statistics (sent/received counts)
  - Last interaction date
  - Date added via automation
```

**Example note:**
```
Email contact - 15 exchanges (sent: 8, received: 7)
Last interaction: 2025-10-15
Added automatically from email analysis on 2025-10-30
```

## Advanced Configuration

### Adjust Time Period

Edit `extract_and_sync_email_contacts.py`:

```python
# Change from 6 months to 3 months
three_months_ago = datetime.now() - timedelta(days=90)

# Or 1 year
one_year_ago = datetime.now() - timedelta(days=365)
```

### Customize Email Query

Modify the Gmail query in `analyze_emails_last_6_months()`:

```python
# Example: Only from specific domain
query = f'after:{date_str} from:*@company.com'

# Example: Exclude certain addresses
query = f'after:{date_str} -from:noreply@* -from:notifications@*'
```

### Adjust Matching Thresholds

In `improved_contact_matcher.py`:

```python
matcher.run(
    fuzzy_threshold=0.85,        # Minimum similarity (0-1)
    auto_match_threshold=0.95,   # Auto-match threshold (0-1)
    interactive=False            # Set True for manual review
)
```

## Filtering Criteria

### Emails Analyzed
- ✅ Last 6 months by default
- ✅ Both sent and received
- ✅ All folders (inbox, sent, archives)
- ❌ Excludes spam and trash (unless specified)

### Contacts Extracted
- ✅ Must have at least 1 sent email
- ✅ Must have at least 1 received email
- ✅ Unique email addresses only
- ❌ Excludes your own email addresses
- ❌ Excludes malformed email addresses

### Google Contact Addition
- ✅ Only contacts not already in Google Contacts
- ✅ Rate-limited to avoid API throttling
- ✅ Validates email format
- ❌ Skips if contact creation fails

## Troubleshooting

### "Rate limit exceeded"
- Wait a few minutes between batch operations
- Reduce `batch_size` in `add_contacts_to_google()`
- The script includes automatic rate limiting

### "Too many emails to process"
- Reduce `max_emails` parameter
- Narrow the date range
- Use more specific Gmail queries

### "No new contacts found"
All your email contacts are already in Google Contacts! ✓

### "Matching quality is poor"
- Lower `fuzzy_threshold` (try 0.80)
- Check `needs_review_*.csv` for uncertain matches
- Use `interactive=True` for manual review

## Data Privacy

- All processing happens locally
- No data sent to third parties
- Google API uses OAuth2 authentication
- Email content is not stored, only metadata
- Reports contain only contact information

## Automation

### Run Weekly

Add to crontab (Mac/Linux):
```bash
# Every Sunday at 2 AM
0 2 * * 0 cd /path/to/Corbin20 && python complete_contact_sync_workflow.py
```

### Run on Demand

Create an alias in `.zshrc` or `.bashrc`:
```bash
alias sync-contacts="cd /path/to/Corbin20 && python complete_contact_sync_workflow.py"
```

Then run: `sync-contacts`

## Example Output

```
================================================================================
EMAIL CONTACT EXTRACTION AND SYNC
================================================================================

Fetching emails after 2025/04/30...
Found 4234 messages to analyze

  Processed 100/4234 messages...
  Processed 200/4234 messages...
  ...

✓ Processed 4234 messages
✓ Found 342 unique email contacts
✓ Found 187 contacts with bidirectional exchanges

================================================================================
LOADING EXISTING GOOGLE CONTACTS
================================================================================
✓ Loaded 239 existing Google Contacts
✓ Indexed 295 unique email addresses

✓ Found 45 new contacts not in Google Contacts

Add 45 new contacts to Google Contacts? (y/n): y

================================================================================
ADDING 45 NEW CONTACTS TO GOOGLE CONTACTS
================================================================================
  ✓ Added: John Doe
  ✓ Added: Jane Smith
  ...

✓ Successfully added 45 contacts to Google Contacts

================================================================================
SUMMARY
================================================================================
Total bidirectional email contacts: 187
Already in Google Contacts: 142
New contacts found: 45
New contacts added: 45
================================================================================
```

## Next Steps After Running

1. **Review Reports**
   - Check who was added
   - Verify bidirectional contact list
   - Review LinkedIn matches

2. **Manual Verification**
   - Open `needs_review_*.csv`
   - Verify uncertain matches
   - Update `manual_match_contacts.py` if needed

3. **Clean Up**
   - Remove any incorrectly added contacts
   - Add additional information to Google Contacts
   - Tag or group contacts as needed

4. **Schedule Regular Runs**
   - Monthly or quarterly re-sync
   - Catches new email relationships
   - Keeps LinkedIn profiles updated

---

Last updated: 2025-10-30

