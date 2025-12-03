---
description: Comprehensive Apollo.io operations including campaign management, people/company search, and enrichment. Use this skill for managing email sequences, campaigns, searching for prospects, enriching contacts, tracking email statistics, and analyzing outreach performance. Handles prospect discovery, contact enrichment, sequence management, and email tracking.
---

# Apollo Campaign Manager

You are operating the Apollo Campaign Manager ability - a comprehensive tool for Apollo.io operations including campaign management, prospect discovery, contact enrichment, and email tracking.

## Standard Operating Instructions

### Prerequisites Check
1. Verify the ability is properly installed at `.claude/abilities/apollo-campaign-manager/`
2. Confirm virtual environment exists: `.claude/abilities/apollo-campaign-manager/venv/`
3. Check that `.env` file is configured with APOLLO_API_KEY

### Available Operations

#### 1. People Search & Enrichment
Search for and enrich contact information:

**Search people by criteria:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py search-people --titles "CEO,CTO" --locations "San Francisco,New York"
```

**Enrich person by email:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py enrich-person --email "contact@example.com"
```

#### 2. Company Search & Enrichment
Find and enrich company data:

**Search companies:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py search-companies --query "AI startup" --locations "San Francisco"
```

**Enrich company:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py enrich-company --domain "example.com"
```

#### 3. Sequence Management
Manage Apollo email sequences:

**List all sequences:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py search-sequences
```

**Search sequences by name:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py search-sequences --query "cold outreach"
```

**Add contacts to sequence:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py add-to-sequence --sequence-id "SEQUENCE_ID" --contact-ids "contact1,contact2,contact3" --mailbox-id "MAILBOX_ID"
```

**Remove contacts from sequence:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py update-status --sequence-id "SEQUENCE_ID" --contact-ids "contact1,contact2" --action remove
```

**Mark contacts as finished:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py update-status --sequence-id "SEQUENCE_ID" --contact-ids "contact1,contact2" --action finish
```

#### 4. Email Account Management
List and manage email accounts:

**List all email accounts/mailboxes:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py list-email-accounts
```

#### 5. Email Tracking & Analytics
Monitor campaign performance:

**Search outreach emails:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py search-emails --sequence-id "SEQUENCE_ID" --date-from "2025-01-01" --date-to "2025-01-31"
```

**Get email statistics:**
```bash
cd .claude/abilities/apollo-campaign-manager && source venv/bin/activate && python apollo_manager.py email-stats --email-id "EMAIL_ID"
```

### Common Workflows

#### Workflow 1: Build and Launch a Campaign
1. Search for prospects using people search
2. List available sequences to get sequence ID
3. Get email accounts to choose sending mailbox
4. Add contacts to the selected sequence

#### Workflow 2: Monitor Campaign Performance
1. Search for recent outreach emails from a sequence
2. Get detailed stats for specific emails
3. Analyze open rates, click rates, and reply rates

#### Workflow 3: Clean Up Sequences
1. Search sequences to find active campaigns
2. Remove bounced or unresponsive contacts
3. Mark completed contacts as finished

### Important Notes

**API Key Requirements:**
- This ability requires an Apollo.io **Master API Key** (not a regular API key)
- Master API keys are only available on paid Apollo.io plans
- Regular API keys only support search and enrichment operations
- Master API keys additionally provide access to sequences, campaigns, and email tracking

**Rate Limiting:**
- Apollo API has rate limits - space out requests if needed
- Large result sets are paginated automatically
- Email search limited to 50,000 records - use filters for large datasets

**Error Handling:**
- 403 Forbidden: Master API key required
- 404 Not Found: Invalid sequence or contact ID
- 422 Unprocessable Entity: Check API key permissions or account plan

### Response Format
When operations complete:
1. Present the results in a clear, formatted manner
2. Extract key information (IDs, names, statistics)
3. Provide actionable insights based on the data
4. Suggest next steps if applicable

### Exports
The ability automatically saves detailed results to:
`.claude/abilities/apollo-campaign-manager/exports/`

All JSON output files are timestamped for easy reference.

## Examples

**Example 1: "Show me all my Apollo sequences"**
→ Execute `search-sequences` command
→ Display formatted list with IDs, names, and stats

**Example 2: "Find CTOs in San Francisco"**
→ Execute `search-people` with title filter and location
→ Display enriched contact information

**Example 3: "Add these contacts to my cold outreach sequence"**
→ First list sequences to identify the right one
→ Show available email accounts
→ Execute `add-to-sequence` with provided contact IDs
→ Confirm successful addition

**Example 4: "How is my nurture campaign performing?"**
→ Search for the sequence by name
→ Retrieve email statistics for that sequence
→ Show open rates, click rates, and reply rates

## When to Use This Command

Invoke this command when the user requests:
- Searching for prospects or companies
- Enriching contact or company data
- Managing Apollo sequences or campaigns
- Adding/removing contacts from sequences
- Tracking email performance and statistics
- Analyzing campaign metrics
- Listing email accounts or sequences
