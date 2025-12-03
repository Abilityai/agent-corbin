---
name: apollo-campaign-manager
description: Comprehensive Apollo.io operations including campaign management, people/company search, and enrichment. Use this skill for managing email sequences, campaigns, searching for prospects, enriching contacts, tracking email statistics, and analyzing outreach performance. Handles prospect discovery, contact enrichment, sequence management, and email tracking.
---

# Apollo Campaign Manager Skill

This skill provides comprehensive campaign and sequence management capabilities for Apollo.io, extending beyond the basic MCP tools to handle the full campaign lifecycle.

## Capabilities

### People Search & Enrichment
- **Search People**: Find prospects by title, location, seniority, company, and keywords
- **Enrich Person**: Get detailed contact information by email, name, or company
- **Bulk Operations**: Search and enrich multiple contacts at once
- **Filtering**: Advanced filters for targeting specific prospects

### Company Search & Enrichment
- **Search Companies**: Find companies by location, size, industry, and keywords
- **Enrich Company**: Get detailed company data by domain or name
- **Industry Targeting**: Filter by industry tags and company characteristics
- **Size Filtering**: Target companies by employee count ranges

### Sequence Management
- **Search Sequences**: Find and list all sequences in your Apollo account with filtering options
- **Add Contacts to Sequences**: Bulk add contacts to specific sequences with mailbox selection
- **Update Contact Status**: Mark contacts as finished or remove them from sequences
- **Sequence Analytics**: Get overview statistics and performance metrics for sequences

### Email Account Management
- **List Email Accounts**: Get all connected email accounts/mailboxes in your Apollo account
- **Manage Sending Mailboxes**: Configure which mailboxes send emails for specific sequences

### Email Campaign Tracking
- **Search Outreach Emails**: Find emails sent through Apollo sequences with advanced filtering
- **Check Email Statistics**: Get detailed metrics for individual emails (opens, clicks, replies)
- **Campaign Performance**: Analyze aggregate performance across sequences

### Contact List Operations
- **Add Contacts in Bulk**: Prepare and add multiple contacts to sequences at once
- **Remove/Pause Contacts**: Manage contact status in active sequences
- **Contact Validation**: Ensure contacts exist before adding to sequences

## When to Use This Skill

Use this skill when the user asks to:
- **Search**: "Find CTOs in San Francisco", "Search for AI companies in NYC"
- **Enrich**: "Get details for this email", "Enrich google.com"
- **Sequences**: "Show me my Apollo sequences", "Add these leads to a sequence"
- **Campaigns**: "Remove contacts from a campaign", "Check email statistics"
- **Email Tracking**: "How is my sequence performing?", "Find emails I sent last week"
- **Management**: "List my email accounts", "Pause contacts in sequence X"

## Usage Instructions

### Prerequisites
- Apollo.io Master API key configured in `.env` file in skill directory
- Paid Apollo plan (some features require paid subscription)

### Common Workflows

#### 1. Adding Contacts to a Sequence
```bash
# First, list available sequences to get sequence ID
python apollo_manager.py search-sequences

# Get email accounts to choose sending mailbox
python apollo_manager.py list-email-accounts

# Add contacts to sequence
python apollo_manager.py add-to-sequence \
  --sequence-id "SEQUENCE_ID" \
  --contact-ids "contact1,contact2,contact3" \
  --mailbox-id "MAILBOX_ID"
```

#### 2. Monitoring Campaign Performance
```bash
# Search for recent outreach emails
python apollo_manager.py search-emails \
  --date-from "2025-01-01" \
  --sequence-id "SEQUENCE_ID"

# Check specific email stats
python apollo_manager.py email-stats --email-id "EMAIL_ID"
```

#### 3. Managing Sequence Contacts
```bash
# Remove contacts from sequence
python apollo_manager.py remove-from-sequence \
  --sequence-id "SEQUENCE_ID" \
  --contact-ids "contact1,contact2"

# Mark contacts as finished
python apollo_manager.py finish-sequence \
  --sequence-id "SEQUENCE_ID" \
  --contact-ids "contact1,contact2"
```

## API Reference

All operations use the Apollo API v1 endpoints:
- `POST /api/v1/emailer_campaigns/search` - Search sequences
- `POST /api/v1/emailer_campaigns/{id}/add_contact_ids` - Add contacts to sequence
- `POST /api/v1/emailer_campaigns/remove_or_stop_contact_ids` - Update contact status
- `GET /api/v1/email_accounts` - List email accounts
- `GET /api/v1/emailer_messages/search` - Search outreach emails
- `GET /api/v1/emailer_messages/{id}/activities` - Get email statistics

## Error Handling

Common errors and solutions:
- **403 Forbidden**: Master API key required - check `.mcp.json` configuration
- **404 Not Found**: Invalid sequence or contact ID - verify IDs exist
- **Free Plan Limitation**: Sequences require paid plan
- **Contact Not Found**: Create contact first using existing MCP enrichment tools

## Standalone Skill

This skill is completely standalone and does not require the Apollo MCP server. It handles:
- People search and enrichment
- Company search and enrichment
- Campaign management and sequences
- Email tracking and analytics

## Configuration

The skill reads Apollo API credentials from `.env` file in the skill directory:
```bash
# .claude/skills/apollo-campaign-manager/.env
APOLLO_API_KEY=your_master_api_key
APOLLO_BASE_URL=https://api.apollo.io/api/v1
```

The `.env` file is gitignored for security.

## Examples

**Example 1: List all sequences**
```
"Show me all my Apollo sequences"
→ Skill searches sequences and displays formatted list with IDs, names, and stats
```

**Example 2: Add leads to nurture sequence**
```
"Add contacts abc123, def456, ghi789 to my nurture sequence"
→ Skill prompts for sequence ID if not known
→ Shows available email accounts
→ Adds contacts with chosen mailbox
→ Confirms successful addition
```

**Example 3: Check sequence performance**
```
"How is my cold outreach sequence performing?"
→ Skill searches for sequence by name
→ Retrieves email statistics
→ Shows open rates, click rates, reply rates
```

## Files

- `SKILL.md` - This skill definition
- `apollo_manager.py` - Python script for Apollo campaign API operations
- `requirements.txt` - Python dependencies

## Notes

- All operations require a Master API key (not regular API key)
- Results are paginated (100 records per page, up to 500 pages for emails)
- Email search limited to 50,000 records - use filters for large datasets
- Contacts must exist in Apollo before adding to sequences
- Use existing MCP tools for contact creation and enrichment
