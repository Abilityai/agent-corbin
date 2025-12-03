# Contact Enrichment Scripts

This folder contains all scripts and artifacts related to contact database management, enrichment, and synchronization.

## Overview

The contact enrichment system identifies collaboration partners from Gmail, syncs them with Google Contacts, matches them with LinkedIn profiles, and enriches contact data using LinkedIn and Apollo.io APIs.

## Core Scripts

### Email Collaborator Extraction

#### `enrich_email_collaborators.py`
**Purpose**: Identifies collaboration partners from Gmail and adds them to Google Contacts

**Features**:
- Searches emails from last N days (default: 90)
- Extracts sender information (excluding automated/marketing emails)
- Filters by minimum message count (default: 2+)
- Checks against existing contact database
- Adds new contacts to Google Contacts
- Generates enrichment report

**Usage**:
```bash
python enrich_email_collaborators.py --days 90 --min-messages 2
```

**Output**: JSON report with new contacts added

#### `enrich_email_collaborators_mcp.py`
MCP-enabled version of the email collaborator enrichment script with Google Workspace integration.

#### `batch_email_enrichment.py` / `batch_email_enrichment_mcp.py`
Batch processing versions for handling large email datasets.

#### `process_email_batch.py`
Processes email batches for contact extraction with configurable batch sizes.

#### `process_month_contacts.py`
Monthly contact extraction focused on specific time periods.

### Google Contacts Synchronization

#### `sync_google_contacts_to_linkedin.py`
**Purpose**: Syncs Google Contacts with LinkedIn profile database

**Features**:
- Matches contacts by email and name
- Updates LinkedIn JSON files with Google Contact data
- Creates reports for unmatched contacts
- Generates confidence scores (high, medium, fuzzy)

**Usage**:
```bash
python sync_google_contacts_to_linkedin.py
```

**Output**:
- Updated LinkedIn JSON files in `linkedin_contacts/`
- Unmatched contacts report

#### `lookup_google_contacts_on_linkedin.py`
Searches for Google Contacts on LinkedIn and retrieves profile data.

#### `extract_and_sync_email_contacts.py`
Combined workflow that extracts from email and syncs to Google Contacts in one operation.

### Contact Matching and Deduplication

#### `improved_contact_matcher.py`
**Purpose**: Enhanced matching algorithms for difficult contact matching cases

**Features**:
- Fuzzy name matching
- Email domain analysis
- Company name normalization
- Multiple confidence level scoring

**Usage**:
```bash
python improved_contact_matcher.py
```

#### `smart_contact_finder.py`
Intelligent contact search and matching across multiple data sources.

#### `manual_match_contacts.py`
Interactive script for manually matching unmatched contacts with high confidence.

### Workflow Orchestration

#### `complete_contact_sync_workflow.py`
**Purpose**: Complete end-to-end contact enrichment workflow

**Workflow Steps**:
1. Extract email collaborators from Gmail
2. Add new contacts to Google Contacts
3. Sync Google Contacts with LinkedIn profiles
4. Generate comprehensive reports
5. Identify contacts needing manual enrichment

**Usage**:
```bash
python complete_contact_sync_workflow.py
```

## Output Files and Artifacts

### JSON Reports
- `email_collaborator_enrichment_YYYYMMDD_HHMMSS.json`: Email extraction results
- `email_enrichment_report_YYYYMMDD_HHMMSS.json`: Detailed enrichment reports
- `contact_progress.json`: Progress tracking for batch operations

### Documentation
- `CONTACT_SYNC_SUMMARY.md`: Summary of sync operations and results
- `EMAIL_CONTACT_SYNC_README.md`: Email-specific sync documentation
- `GOOGLE_CONTACTS_SYNC_README.md`: Google Contacts integration guide
- `extract_contacts_oct.txt`: Extraction logs and notes

## Enrichment Workflow

### Standard Operating Procedure

**Step 1: Identify Email Collaborators**
```bash
python enrich_email_collaborators.py --days 90 --min-messages 2
```

**Step 2: Sync with LinkedIn Profiles**
```bash
python sync_google_contacts_to_linkedin.py
```

**Step 3: Manual Enrichment for Unmatched**
For contacts that couldn't be automatically matched:
- Use `/linkedin-lead-research` ability for LinkedIn profile data
- Use `/apollo-campaign-manager` ability for Apollo.io enrichment

**Step 4: Review and Clean**
```bash
python improved_contact_matcher.py  # For difficult matches
python manual_match_contacts.py     # For manual review
```

## Data Integration

### Google Contacts Fields
- Primary email addresses
- Phone numbers
- Organization/company
- Job titles
- Notes and custom fields

### LinkedIn Enrichment
- Profile URL and username
- Headline and summary
- Career history and positions
- Location details
- Posts and engagement metrics
- Connection counts

### Apollo.io Enrichment
- Company details and size
- Technologies used
- Funding information
- Revenue data
- Organizational charts
- Contact scoring

## Automated Detection

The system automatically filters out:
- Newsletter subscriptions
- System notifications
- Calendar invites (Calendly, etc.)
- Marketing automation emails
- Non-human senders

**Focus**: Real human collaboration (2+ message threshold by default)

## Data Quality

### Match Confidence Levels
- **High**: Exact email match + name match
- **Medium**: Email domain match + fuzzy name match
- **Fuzzy**: Partial matches requiring manual review
- **No match**: Requires manual enrichment

### Quality Checks
- Duplicate detection across sources
- Email validation
- Name normalization
- Company name standardization

## Dependencies

### Required Python Packages
- google-auth
- google-api-python-client
- anthropic (for MCP versions)
- requests
- fuzzywuzzy (for contact matching)

### Required Access
- Google Workspace account (eugene@ability.ai)
- Gmail API access
- Google Contacts API access
- Google People API access
- LinkedIn contact database (`linkedin_contacts/` folder)

### Optional Integrations
- RapidAPI professional-network-data (for LinkedIn enrichment)
- Apollo.io Master API Key (for Apollo enrichment)

## File Naming Conventions

- `*_mcp.py`: MCP-enabled versions with Google Workspace integration
- `*_enrichment_*.json`: Timestamped enrichment reports
- `*_README.md`: Task-specific documentation
- `*_SUMMARY.md`: Result summaries and analytics

## Best Practices

1. **Run regularly**: Weekly or bi-weekly to keep contacts fresh
2. **Review outputs**: Check JSON reports for quality issues
3. **Manual review**: Use manual matching tools for high-value contacts
4. **Update thresholds**: Adjust minimum message counts based on needs
5. **Archive old reports**: Move outdated JSON reports to archive after review

## Troubleshooting

### Common Issues

**"No contacts found"**
- Check Gmail API permissions
- Verify date range is appropriate
- Confirm minimum message threshold isn't too high

**"LinkedIn match failures"**
- Ensure `linkedin_contacts/` folder is accessible
- Check schema.json is present and valid
- Verify email addresses in LinkedIn JSON files

**"Google Contacts API errors"**
- Re-authenticate Google Workspace access
- Check API quotas and rate limits
- Verify contact permissions

## Related Resources

- Main contact database: `/linkedin_contacts/`
- Contact schema: `/linkedin_contacts/schema.json`
- LinkedIn enrichment ability: `/.claude/abilities/linkedin-lead-research/`
- Apollo enrichment ability: `/.claude/abilities/apollo-campaign-manager/`

## Maintenance

- Clean up old JSON reports monthly
- Review and update matching algorithms quarterly
- Audit contact quality and duplicates regularly
- Update filter rules for automated email detection as needed
