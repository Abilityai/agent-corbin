---
name: linkedin-lead-research
description: Research and enrich LinkedIn profiles using professional-network-data API. Use this skill when the user needs to: fetch LinkedIn profile data by username, get recent activity and posts, analyze connection engagement, retrieve profile positions and career information, or enrich lead data for sales and business development. Works with LinkedIn usernames extracted from profile URLs (e.g., "johndoe" from linkedin.com/in/johndoe).
allowed-tools:
  - Bash
  - Read
  - Write
---

# LinkedIn Lead Research Skill

This skill provides comprehensive LinkedIn profile enrichment capabilities using the RapidAPI professional-network-data service.

## Capabilities

### Profile Enrichment
- **Basic Profile Data**: Full name, headline, location, summary, geo data
- **Career Information**: Current position, company, title, employment history
- **Recent Activity**: Last active timestamp, activity patterns
- **Content Analysis**: Recent posts (with engagement metrics), recent comments
- **Engagement Metrics**: Like counts, comment counts, activity rates

### Data Collection
- Extracts detailed profile information including location/geo data
- Fetches recent activity timestamps to identify active users
- Collects posts from specified timeframe with engagement metrics
- Gathers recent comments showing engagement patterns
- Retrieves current position and company information
- Tracks activity statistics and engagement rates

## Usage

This skill is automatically invoked when users request:
- "Get LinkedIn profile data for username X"
- "Enrich this LinkedIn profile"
- "Fetch recent activity for LinkedIn user Y"
- "What has this person posted recently on LinkedIn?"
- "Get profile information from this LinkedIn URL"

## API Configuration

**API Provider**: RapidAPI - professional-network-data
**API Host**: professional-network-data.p.rapidapi.com
**API Key**: Self-contained in `.env` file within this skill directory

This skill is **fully self-contained** with its own:
- Python virtual environment (venv/)
- API key configuration (.env)
- All dependencies (requirements.txt)
- No external dependencies on other projects

## Available Functions

### 1. Get Basic Profile
- **Endpoint**: `GET /?username={username}`
- **Returns**: Full profile including name, headline, location, summary, geo data

### 2. Get Recent Activity Time
- **Endpoint**: `GET /get-profile-recent-activity-time?username={username}`
- **Returns**: Last active timestamp

### 3. Get Top Position
- **Endpoint**: `GET /profiles/positions/top?username={username}`
- **Returns**: Current position, company, title, dates

### 4. Get Profile Posts
- **Endpoint**: `GET /get-profile-posts?username={username}&start={start}&postedAt={date}`
- **Parameters**:
  - `username`: LinkedIn username
  - `start`: Pagination offset (0, 50, 100, etc.)
  - `postedAt`: Filter for posts after date (format: YYYY-MM-DD HH:MM:SS)
- **Returns**: Posts with text, date, engagement metrics

### 5. Get Profile Comments
- **Endpoint**: `GET /get-profile-comments?username={username}`
- **Returns**: Recent comments with text, date, post URLs

## Implementation

The skill is completely self-contained within this directory with:
- **API Wrapper**: `linkedin_api.py` - Python script for LinkedIn API calls
- **Configuration**: `.env` - Local API key storage
- **Dependencies**: `venv/` - Isolated Python environment with requests library
- **Setup**: `setup.sh` - One-command installation script

When invoked, the skill:
1. Extracts username from LinkedIn URL or uses provided username
2. Calls the appropriate API endpoints
3. Enriches and structures the data
4. Returns formatted results for analysis

## Output Format

Results are returned in structured JSON format:
```json
{
  "username": "johndoe",
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

## Rate Limiting

- **Recommended Delay**: 0.3-0.5 seconds between requests
- **Retry Logic**: Exponential backoff with jitter for 429/500 errors
- **Max Retries**: 5 attempts per request

## Best Practices

1. **Username Extraction**: Always extract username from full LinkedIn URLs
2. **Batch Processing**: Use delays between multiple profile requests
3. **Error Handling**: Check for empty responses and API failures
4. **Data Validation**: Verify profile data exists before processing
5. **Activity Filtering**: Use time windows (7-30 days) for recent activity

## Example Queries

- "Research this LinkedIn profile: linkedin.com/in/johndoe"
- "Get recent posts for LinkedIn user jane-smith"
- "Enrich profile data for username: bob-jones"
- "What has this person been posting lately: linkedin.com/in/alice-williams"
- "Check if LinkedIn user mike-brown is active"

## Notes

- Requires valid RapidAPI key from source project
- Uses the same API endpoints and configuration as the linkedin_lead_generation automation
- No modifications to source project required - skill reads configuration directly
- All API keys and credentials remain in their original location
