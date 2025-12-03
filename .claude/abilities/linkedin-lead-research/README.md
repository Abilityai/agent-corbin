# LinkedIn Lead Research Skill

A Claude Code skill for researching and enriching LinkedIn profiles using the RapidAPI professional-network-data service.

## Overview

This skill enables Claude to fetch comprehensive LinkedIn profile data including:
- Basic profile information (name, headline, location, summary)
- Current position and company details
- Recent activity timestamps
- Recent posts with engagement metrics
- Recent comments and interactions

## Setup

### Prerequisites

1. **Python Requirements**: Install the `requests` library
   ```bash
   pip install requests
   ```

2. **API Key**: The skill uses the RapidAPI key from your existing `linkedin_lead_generation` project
   - Location: `/Users/eugene/Dropbox/Coding/N8N_Main_repos/linkedin_lead_generation/.env`
   - Variable: `RAPIDAPI_KEY`
   - No additional configuration needed - the skill reads it automatically

### Installation

The skill is already installed in your project at:
```
.claude/skills/linkedin-lead-research/
```

Claude Code will automatically discover and use it based on context.

## Usage

### Automatic Invocation

Claude will automatically use this skill when you ask questions like:
- "Research this LinkedIn profile: linkedin.com/in/johndoe"
- "Get recent posts for LinkedIn user jane-smith"
- "What's the current position of bob-jones on LinkedIn?"
- "Enrich profile data for username: alice-williams"
- "Check if LinkedIn user mike-brown is active"

### Manual Testing

You can test the skill directly from the command line:

```bash
# Extract username from URL
python3 .claude/skills/linkedin-lead-research/linkedin_api.py extract-username "https://linkedin.com/in/johndoe"

# Get basic profile
python3 .claude/skills/linkedin-lead-research/linkedin_api.py profile johndoe

# Get recent activity
python3 .claude/skills/linkedin-lead-research/linkedin_api.py activity johndoe

# Get current position
python3 .claude/skills/linkedin-lead-research/linkedin_api.py position johndoe

# Get recent posts (last 30 days)
python3 .claude/skills/linkedin-lead-research/linkedin_api.py posts johndoe 30

# Get recent comments
python3 .claude/skills/linkedin-lead-research/linkedin_api.py comments johndoe

# Full profile enrichment (all data)
python3 .claude/skills/linkedin-lead-research/linkedin_api.py enrich johndoe 30
```

## API Endpoints

The skill uses the following RapidAPI endpoints:

| Endpoint | Purpose | Parameters |
|----------|---------|------------|
| `GET /` | Basic profile info | `username` |
| `GET /get-profile-recent-activity-time` | Last active timestamp | `username` |
| `GET /profiles/positions/top` | Current position | `username` |
| `GET /get-profile-posts` | Recent posts | `username`, `start`, `postedAt` |
| `GET /get-profile-comments` | Recent comments | `username` |

## Output Format

The skill returns structured JSON data:

```json
{
  "username": "johndoe",
  "fetchedAt": "2025-10-28T12:00:00Z",
  "basic_profile": {
    "full_name": "John Doe",
    "headline": "CEO at TechStartup",
    "location": "San Francisco, CA",
    "summary": "Entrepreneur and technologist...",
    "geo": {
      "country": "United States",
      "city": "San Francisco",
      "countryCode": "us"
    }
  },
  "top_position": {
    "title": "CEO",
    "company": "TechStartup Inc",
    "isCurrent": true,
    "startDate": "2023-01-01"
  },
  "recent_activity": {
    "last_active": "2025-10-27T10:30:00Z"
  },
  "recent_posts": [
    {
      "text": "Excited to announce...",
      "createdAt": "2025-10-25T14:20:00Z",
      "url": "https://linkedin.com/posts/...",
      "likeCount": 45,
      "commentCount": 12
    }
  ],
  "recent_comments": [
    {
      "text": "Great insights!",
      "createdAt": "2025-10-26T09:15:00Z",
      "postUrl": "https://linkedin.com/posts/..."
    }
  ]
}
```

## Rate Limiting

- **Default delay**: 0.3 seconds between requests
- **Retry logic**: Exponential backoff for rate limit errors (429)
- **Max retries**: 5 attempts per request
- **Best practice**: Process profiles one at a time or with delays for batch operations

## Integration with Existing Project

This skill uses the same API and configuration as your `linkedin_lead_generation` project:

- **API Key Source**: `/Users/eugene/Dropbox/Coding/N8N_Main_repos/linkedin_lead_generation/.env`
- **Compatible with**: All existing enrichment scripts and workflows
- **No modifications needed**: The skill reads configuration directly from the source project

## Troubleshooting

### Common Issues

1. **"requests module not found"**
   - Install: `pip install requests`

2. **"API key not found"**
   - Verify `.env` file exists in linkedin_lead_generation project
   - Check `RAPIDAPI_KEY` is set in the `.env` file

3. **Empty responses**
   - Verify the username is correct (no slashes, lowercase)
   - Check if the profile exists and is public
   - Some profiles may have limited public data

4. **Rate limit errors**
   - Increase delay between requests
   - Use exponential backoff (built into the skill)
   - Wait a few minutes before retrying

### Debugging

Enable verbose output by checking stderr when running commands:

```bash
python3 .claude/skills/linkedin-lead-research/linkedin_api.py enrich johndoe 2>&1
```

## Best Practices

1. **Username Format**: Always use the vanity name (e.g., "johndoe" not the numeric ID)
2. **URL Extraction**: Use the `extract-username` command to get username from URLs
3. **Batch Processing**: Add delays between requests when processing multiple profiles
4. **Error Handling**: Check for null/empty responses before processing data
5. **Time Filters**: Use appropriate day ranges (7-30 days) for recent activity

## Examples

### Example 1: Research a Lead
```
User: "Research this LinkedIn profile: https://linkedin.com/in/jane-tech-founder"

Claude will:
1. Extract username: jane-tech-founder
2. Fetch all profile data
3. Return structured information about Jane including her position, recent posts, and activity
```

### Example 2: Check Multiple Profiles
```
User: "Check if these LinkedIn users are active: alice-smith, bob-jones, charlie-brown"

Claude will:
1. Fetch activity data for each username
2. Compare last active timestamps
3. Summarize which profiles show recent activity
```

### Example 3: Analyze Content
```
User: "What has john-entrepreneur been posting about lately?"

Claude will:
1. Fetch recent posts for john-entrepreneur
2. Analyze post content and topics
3. Summarize themes and engagement patterns
```

## Security Notes

- API keys are stored securely in the source project
- No credentials are exposed in this skill
- All API calls use HTTPS
- Rate limiting prevents abuse

## Version History

- **v1.0.0** (2025-10-28): Initial release
  - Basic profile enrichment
  - Recent activity tracking
  - Posts and comments retrieval
  - Integration with linkedin_lead_generation project
