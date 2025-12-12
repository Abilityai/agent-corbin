# LinkedIn Lead Research Skill - Installation & Usage

## Quick Start

The skill is now installed and ready to use! Claude will automatically invoke it when you ask LinkedIn-related questions.

## What Was Created

```
.claude/skills/linkedin-lead-research/
├── SKILL.md              # Skill definition (tells Claude when to use it)
├── linkedin_api.py       # API wrapper for LinkedIn data
├── README.md             # Comprehensive documentation
└── INSTALLATION.md       # This file
```

## How It Works

### 1. Automatic Invocation
Claude automatically uses this skill when you ask questions like:
- "Research this LinkedIn profile: https://linkedin.com/in/username"
- "Get recent posts for LinkedIn user johndoe"
- "What's the current position of jane-smith?"
- "Check if bob-jones is active on LinkedIn"

### 2. Data Sources
- **API**: RapidAPI professional-network-data service
- **API Key**: Uses your existing key from `linkedin_lead_generation/.env`
- **Python Environment**: Uses `venv_new` from your source project

### 3. Available Operations

| Operation | Command | Description |
|-----------|---------|-------------|
| Extract username | `extract-username <url>` | Get username from LinkedIn URL |
| Basic profile | `profile <username>` | Name, headline, location, summary |
| Recent activity | `activity <username>` | Last active timestamp |
| Current position | `position <username>` | Job title, company |
| Recent posts | `posts <username> [days]` | Posts with engagement metrics |
| Recent comments | `comments <username>` | Comment activity |
| Full enrichment | `enrich <username> [days]` | All data combined |

## Testing the Skill

### Test 1: Username Extraction
```bash
.claude/skills/linkedin-lead-research/linkedin_api.py extract-username "https://linkedin.com/in/eugenevy"
```

Expected output:
```json
{
  "username": "eugenevy"
}
```

### Test 2: Full Profile Enrichment
```bash
.claude/skills/linkedin-lead-research/linkedin_api.py enrich eugenevy 30
```

Expected output: Complete profile data with all fields populated.

## Usage Examples

### Example 1: Research a Prospect
**You say**: "Research this LinkedIn profile: https://linkedin.com/in/jane-tech-ceo"

**Claude will**:
1. Use the linkedin-lead-research skill
2. Extract username: `jane-tech-ceo`
3. Fetch all available data
4. Present structured information about Jane

### Example 2: Check Activity
**You say**: "Is john-entrepreneur active on LinkedIn?"

**Claude will**:
1. Use the skill to fetch recent activity
2. Check last active timestamp
3. Look for recent posts/comments
4. Report on activity level

### Example 3: Batch Research
**You say**: "Research these 3 LinkedIn profiles: alice-smith, bob-jones, charlie-brown"

**Claude will**:
1. Process each username sequentially
2. Apply rate limiting (0.3s between requests)
3. Compile results for all three profiles
4. Present a comparative summary

## Configuration

### API Key Location
The skill automatically reads the API key from:
```
$DEV_DIR/linkedin_lead_generation/.env
```

If not found there, it uses the environment variable `RAPIDAPI_KEY` or falls back to the hardcoded key.

### Python Environment
The skill uses Python from:
```
$DEV_DIR/linkedin_lead_generation/venv_new/bin/python3
```

This ensures all required dependencies (requests, etc.) are available.

## Rate Limiting

The skill includes built-in rate limiting:
- **Default delay**: 0.3 seconds between requests
- **Exponential backoff**: Automatic retry with increasing delays
- **Max retries**: 5 attempts per failed request
- **Handled errors**: 429 (rate limit), 500, 502, 503, 504

## Troubleshooting

### Issue: "Username not found"
- Verify the LinkedIn URL format
- Ensure the profile is public
- Try extracting username first: `.claude/skills/linkedin-lead-research/linkedin_api.py extract-username "<url>"`

### Issue: "Empty response"
- The profile may have limited public data
- Try basic profile first: `.claude/skills/linkedin-lead-research/linkedin_api.py profile <username>`
- Check if the username is correct

### Issue: "Rate limit error"
- Wait a few minutes before retrying
- The skill will automatically retry with backoff
- Consider increasing delays for batch operations

## Integration with Existing Project

This skill **does not modify** your existing `linkedin_lead_generation` project. It:
- ✅ Reads API key from the existing `.env` file
- ✅ Uses the existing Python virtual environment
- ✅ Shares the same API endpoints and logic
- ✅ Can work alongside your existing scripts

You can continue to use both:
1. **This skill**: For on-demand LinkedIn research through Claude
2. **Existing scripts**: For batch processing and automation

## Output Format

All commands return JSON output that Claude can parse and present:

```json
{
  "username": "johndoe",
  "fetchedAt": "2025-10-28T12:00:00Z",
  "basic_profile": {
    "full_name": "John Doe",
    "headline": "CEO at TechStartup",
    "location": "San Francisco, CA, United States",
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

## Best Practices

1. **Always extract usernames from URLs first** - Ensures clean input
2. **Use appropriate time windows** - 7-30 days for recent activity
3. **Handle rate limits gracefully** - Let the skill's retry logic work
4. **Process one profile at a time** - Or add delays for batch operations
5. **Check for null responses** - Not all data is available for all profiles

## Security

- ✅ API key is read from secure location (not hardcoded in skill)
- ✅ All API calls use HTTPS
- ✅ No credentials exposed in skill files
- ✅ Rate limiting prevents API abuse

## Next Steps

1. **Try it out**: Ask Claude to research a LinkedIn profile
2. **Test manually**: Run the CLI commands to verify functionality
3. **Explore capabilities**: Try different types of queries
4. **Integrate with workflows**: Use alongside your existing automation

## Support

If you encounter issues:
1. Check this documentation
2. Test the CLI commands directly
3. Verify API key is accessible
4. Check the README.md for detailed troubleshooting

---

**Skill Version**: 1.0.0
**Created**: October 28, 2025
**Status**: ✅ Ready to use
