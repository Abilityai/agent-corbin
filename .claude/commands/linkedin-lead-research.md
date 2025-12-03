---
description: Research and enrich LinkedIn profiles using professional-network-data API. Use this skill when the user needs to fetch LinkedIn profile data by username, get recent activity and posts, analyze connection engagement, retrieve profile positions and career information, or enrich lead data for sales and business development. Works with LinkedIn usernames extracted from profile URLs (e.g., "johndoe" from linkedin.com/in/johndoe).
---

# LinkedIn Lead Research

You are operating the LinkedIn Lead Research ability - a comprehensive tool for researching and enriching LinkedIn profiles using the RapidAPI professional-network-data service.

## Standard Operating Instructions

### Prerequisites Check
1. Verify the ability is properly installed at `.claude/abilities/linkedin-lead-research/`
2. Confirm virtual environment exists: `.claude/abilities/linkedin-lead-research/venv/`
3. Check that `.env` file is configured with RAPIDAPI_KEY

### Username Extraction
LinkedIn URLs come in various formats. Always extract the username first:

**Extract username from URL:**
```bash
cd .claude/abilities/linkedin-lead-research && source venv/bin/activate && python linkedin_api.py extract-username "https://linkedin.com/in/johndoe"
```

Common URL formats:
- `linkedin.com/in/johndoe` → username: `johndoe`
- `linkedin.com/in/john-doe-123` → username: `john-doe-123`
- `www.linkedin.com/in/johndoe/` → username: `johndoe`

### Available Operations

#### 1. Basic Profile Enrichment
Get core profile information:

**Fetch basic profile data:**
```bash
cd .claude/abilities/linkedin-lead-research && source venv/bin/activate && python linkedin_api.py profile USERNAME
```

Returns:
- Full name
- Headline
- Location (city, country)
- Profile summary
- Geographic data (country code, city)

#### 2. Recent Activity Tracking
Check when the person was last active:

**Get last active timestamp:**
```bash
cd .claude/abilities/linkedin-lead-research && source venv/bin/activate && python linkedin_api.py activity USERNAME
```

Returns:
- Last active timestamp (ISO format)
- Activity status

#### 3. Current Position
Get current job and company information:

**Fetch current position:**
```bash
cd .claude/abilities/linkedin-lead-research && source venv/bin/activate && python linkedin_api.py position USERNAME
```

Returns:
- Job title
- Company name
- Current employment status
- Start date

#### 4. Recent Posts Analysis
Fetch recent LinkedIn posts with engagement metrics:

**Get posts from last N days:**
```bash
cd .claude/abilities/linkedin-lead-research && source venv/bin/activate && python linkedin_api.py posts USERNAME 30
```

Parameters:
- `USERNAME`: LinkedIn username
- `30`: Number of days to look back (7-90 recommended)

Returns:
- Post text content
- Creation date
- Post URL
- Like count
- Comment count
- Engagement metrics

#### 5. Recent Comments
Get recent comments made by the user:

**Fetch recent comments:**
```bash
cd .claude/abilities/linkedin-lead-research && source venv/bin/activate && python linkedin_api.py comments USERNAME
```

Returns:
- Comment text
- Creation date
- URL of the post commented on
- Engagement patterns

#### 6. Full Profile Enrichment
Get all available data in one operation:

**Complete profile enrichment:**
```bash
cd .claude/abilities/linkedin-lead-research && source venv/bin/activate && python linkedin_api.py enrich USERNAME 30
```

Parameters:
- `USERNAME`: LinkedIn username
- `30`: Days to look back for posts/activity

Returns comprehensive JSON with:
- Basic profile data
- Current position
- Recent activity timestamp
- Recent posts with engagement
- Recent comments
- Full enrichment metadata

### Alternative: Shell Script
For quick enrichment, use the convenience shell script:

```bash
.claude/abilities/linkedin-lead-research/linkedin.sh "https://linkedin.com/in/johndoe" 30
```

This automatically:
1. Extracts username from URL
2. Performs full enrichment
3. Returns structured JSON

### Common Workflows

#### Workflow 1: Research a Single Lead
1. Extract username from LinkedIn URL
2. Perform full enrichment with 30-day lookback
3. Analyze profile data, current position, and recent activity
4. Identify engagement patterns and personalization hooks

#### Workflow 2: Check Activity Status
1. Extract username from URL
2. Get recent activity timestamp
3. Determine if the person is actively using LinkedIn
4. Use this to prioritize outreach timing

#### Workflow 3: Content Analysis
1. Extract username from URL
2. Fetch recent posts from last 30 days
3. Analyze post topics and engagement rates
4. Identify interests and conversation starters for outreach

#### Workflow 4: Batch Profile Research
1. For each LinkedIn URL in the list:
   - Extract username
   - Perform enrichment
   - Add 0.5 second delay between requests (rate limiting)
2. Compile results into structured format
3. Identify patterns and insights across profiles

### Important Notes

**Rate Limiting:**
- **Recommended delay**: 0.3-0.5 seconds between requests
- **Retry logic**: Built-in exponential backoff for rate limit errors
- **Max retries**: 5 attempts per request
- Always add delays when processing multiple profiles

**Data Availability:**
- Some profiles may have limited public data
- Private profiles return minimal information
- Activity data depends on user's privacy settings
- Posts older than 90 days may not be available

**Username Format:**
- Always use the vanity name (e.g., "johndoe")
- Do not use numeric profile IDs
- Lowercase format preferred
- No slashes or special characters

**Error Handling:**
- Empty responses: Profile may not exist or is private
- 429 errors: Rate limit hit, increase delays
- 500 errors: API temporary issue, retry with backoff

### Response Format
When operations complete:
1. Parse the JSON output from the script
2. Present data in a clear, readable format
3. Highlight key information:
   - Current role and company
   - Recent activity status
   - Top posts and engagement
   - Personalization opportunities
4. Provide actionable insights for sales/outreach

### Output Structure
All operations return JSON format:

```json
{
  "username": "johndoe",
  "fetchedAt": "2025-10-29T13:00:00Z",
  "basic_profile": {
    "full_name": "John Doe",
    "headline": "CEO at TechStartup",
    "location": "San Francisco, CA",
    "summary": "...",
    "geo": {
      "country": "United States",
      "city": "San Francisco",
      "countryCode": "us"
    }
  },
  "top_position": {
    "title": "CEO",
    "company": "TechStartup Inc",
    "isCurrent": true
  },
  "recent_activity": {
    "last_active": "2025-10-27T10:30:00Z"
  },
  "recent_posts": [...],
  "recent_comments": [...]
}
```

## Examples

**Example 1: "Research this LinkedIn profile: linkedin.com/in/jane-tech-founder"**
→ Extract username: `jane-tech-founder`
→ Execute full enrichment with 30-day lookback
→ Present structured profile with current role, recent posts, and activity

**Example 2: "Check if these LinkedIn users are active: alice-smith, bob-jones"**
→ For each username:
  - Fetch recent activity timestamp
  - Add 0.5s delay between requests
→ Compare last active dates
→ Summarize active vs inactive profiles

**Example 3: "What has john-entrepreneur been posting about lately?"**
→ Fetch recent posts for john-entrepreneur (30 days)
→ Analyze post content and topics
→ Show engagement metrics (likes, comments)
→ Identify key themes and interests

**Example 4: "Get profile details for this person: linkedin.com/in/sarah-cto-123"**
→ Extract username: `sarah-cto-123`
→ Get basic profile, position, and activity
→ Present current role, company, location, and last active date

## When to Use This Command

Invoke this command when the user requests:
- LinkedIn profile enrichment or research
- Extracting data from LinkedIn URLs
- Checking if someone is active on LinkedIn
- Analyzing recent LinkedIn posts or activity
- Getting current position and company information
- Lead research for sales or business development
- Gathering personalization data for outreach
- Batch processing multiple LinkedIn profiles

## Integration Notes

This ability uses the same API and configuration as the `linkedin_lead_generation` project:
- API Key location: `/Users/eugene/Dropbox/Coding/N8N_Main_repos/linkedin_lead_generation/.env`
- Shared RapidAPI professional-network-data service
- No modifications to source project required
- All credentials remain in their original location
