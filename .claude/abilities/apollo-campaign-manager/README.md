# Apollo Campaign Manager Skill

Comprehensive campaign and sequence management for Apollo.io.

## Features

This standalone skill provides complete Apollo.io functionality:
- **People Search & Enrichment**: Find and enrich contacts by title, location, company
- **Company Search & Enrichment**: Find and enrich companies by industry, size, location
- **Sequences/Campaigns**: Search, create, and manage email sequences
- **Contact Management**: Add/remove contacts from sequences
- **Email Tracking**: Monitor email performance (opens, clicks, replies)
- **Mailbox Management**: List and configure sending email accounts

## Requirements

### 1. Master API Key Required

**IMPORTANT**: This skill requires an Apollo.io **Master API Key**, not a regular API key.

Regular API keys provide access to:
- People search
- Company search
- Enrichment operations

Master API keys additionally provide access to:
- Sequence management
- Email campaign tracking
- Email account configuration
- Outreach analytics

#### How to Get a Master API Key

1. Log in to your Apollo.io account
2. Navigate to Settings → Integrations → API
3. Click "Create New Key" and select **"Master API Key"**
4. Copy the generated key
5. Update your `.mcp.json` with the new key

**Note**: Master API keys are only available on paid Apollo.io plans.

### 2. Installation

The skill uses Python 3 and requires the `requests` library:

```bash
cd .claude/skills/apollo-campaign-manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the skill directory with your Master API key:

```bash
# .claude/skills/apollo-campaign-manager/.env
APOLLO_API_KEY=your_master_api_key_here
APOLLO_BASE_URL=https://api.apollo.io/api/v1
```

The `.env` file is gitignored for security. The skill automatically loads credentials from this file.

## Usage

### Command-Line Interface

The skill provides a Python CLI for all operations:

```bash
# Activate virtual environment
source venv/bin/activate

# All commands automatically use .env file for credentials

# Search for people
python apollo_manager.py search-people --titles "CEO" --locations "San Francisco"

# Search for companies
python apollo_manager.py search-companies --query "AI" --locations "NYC"

# Enrich person
python apollo_manager.py enrich-person --email "test@example.com"

# Enrich company
python apollo_manager.py enrich-company --domain "google.com"

# List all sequences
python apollo_manager.py search-sequences

# Search sequences by query
python apollo_manager.py search-sequences --query "cold outreach"

# List email accounts
python apollo_manager.py list-email-accounts

# Add contacts to sequence
python apollo_manager.py add-to-sequence \
  --sequence-id "SEQ123" \
  --contact-ids "contact1,contact2,contact3" \
  --mailbox-id "MAILBOX123"

# Remove contacts from sequence
python apollo_manager.py update-status \
  --sequence-id "SEQ123" \
  --contact-ids "contact1,contact2" \
  --action remove

# Mark contacts as finished in sequence
python apollo_manager.py update-status \
  --sequence-id "SEQ123" \
  --contact-ids "contact1,contact2" \
  --action finish

# Search outreach emails
python apollo_manager.py search-emails \
  --sequence-id "SEQ123" \
  --date-from "2025-01-01" \
  --date-to "2025-01-31"

# Get email statistics
python apollo_manager.py email-stats --email-id "EMAIL123"
```

### Natural Language (via Claude)

When the skill is active, you can use natural language:

```
"Show me all my Apollo sequences"
"Add these leads to my cold outreach sequence"
"How many people opened emails from my nurture campaign?"
"List my connected email accounts"
"Remove contact ABC123 from sequence XYZ"
```

## API Endpoints

This skill uses the following Apollo API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/emailer_campaigns/search` | POST | Search sequences |
| `/emailer_campaigns/{id}/add_contact_ids` | POST | Add contacts to sequence |
| `/emailer_campaigns/remove_or_stop_contact_ids` | POST | Update contact status |
| `/email_accounts` | GET | List email accounts |
| `/emailer_messages/search` | GET | Search outreach emails |
| `/emailer_messages/{id}/activities` | GET | Get email statistics |

## Troubleshooting

### 403 Forbidden Error

**Problem**: Getting 403 errors when calling sequence endpoints

**Solution**: You're using a regular API key instead of a Master API key. Create a Master API key in Apollo settings.

### 422 Unprocessable Entity

**Problem**: Getting 422 errors

**Possible causes**:
1. API key doesn't have Master permissions
2. Account is on free plan (sequences require paid plan)
3. Invalid request parameters

**Solution**: Verify your Apollo plan and API key type.

### Contact Not Found

**Problem**: Cannot add contact to sequence - contact ID not found

**Solution**: First create the contact using the existing Apollo MCP tools:
1. Use people enrichment to get contact data
2. Use create contact endpoint to add to Apollo
3. Then use this skill to add to sequence

### Rate Limiting

Apollo API has rate limits. If you hit them:
- Wait a few minutes before retrying
- Reduce batch sizes
- Space out requests

## Standalone Skill

This is a **standalone skill** that does not require the Apollo MCP server. It handles:
- People search and enrichment
- Company search and enrichment
- Campaign management
- Sequence operations
- Email tracking
- Mailbox configuration

All operations use the Master API key configured in the `.env` file.

## Examples

### Example 1: Build and Launch a Sequence

```bash
# 1. Find prospects using existing MCP
# (via natural language: "Find CTOs at AI startups in San Francisco")

# 2. Create contacts from enriched data
# (existing MCP handles this)

# 3. List available sequences
python apollo_manager.py search-sequences

# 4. Get email accounts
python apollo_manager.py list-email-accounts

# 5. Add contacts to sequence
python apollo_manager.py add-to-sequence \
  --sequence-id "abc123" \
  --contact-ids "contact1,contact2,contact3" \
  --mailbox-id "mailbox123"
```

### Example 2: Monitor Campaign Performance

```bash
# Search emails from a sequence
python apollo_manager.py search-emails \
  --sequence-id "abc123" \
  --date-from "2025-01-01"

# Get detailed stats for specific email
python apollo_manager.py email-stats --email-id "email456"
```

### Example 3: Clean Up Sequences

```bash
# Remove bounced contacts
python apollo_manager.py update-status \
  --sequence-id "abc123" \
  --contact-ids "contact1,contact2" \
  --action remove

# Mark completed contacts as finished
python apollo_manager.py update-status \
  --sequence-id "abc123" \
  --contact-ids "contact3,contact4" \
  --action finish
```

## Limitations

1. **Master API Key Required**: Most features require Master API access
2. **Paid Plan Required**: Sequences not available on free plans
3. **Rate Limits**: Apollo enforces API rate limits
4. **Pagination**: Large result sets require pagination handling
5. **Email Search Limit**: Maximum 50,000 records per search

## Support

For issues with:
- **This skill**: Check the skill configuration and Python environment
- **Apollo API**: Check Apollo.io API documentation
- **API key issues**: Contact Apollo.io support

## Version

Current version: 1.0.0

Built for Apollo API v1
