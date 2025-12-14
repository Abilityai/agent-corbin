# Corbin - Business Management Assistant

Advanced business operations and Google Workspace management agent.

## Overview

Corbin 2.0 is an advanced business management assistant providing intelligent automation of daily operations through:

- **Google Workspace Integration**: Gmail, Calendar, Drive, Docs, Sheets, Tasks
- **Email Management**: Triage, draft, send, search, and reply to emails
- **Calendar Coordination**: Schedule meetings, check availability, manage events
- **Contact Database**: Enriched contacts with LinkedIn and Apollo.io data
- **Task Management**: Google Tasks integration for personal task tracking
- **Meeting Intelligence**: Transcript search and analysis via Vertex AI
- **Sales Intelligence**: Apollo.io prospect research and lead enrichment
- **File System Awareness**: Comprehensive project and document navigation

## Trinity Deployment

This agent is designed for deployment via [Trinity](https://github.com/abilityai/trinity) platform.

### Quick Start

1. Configure credentials in Trinity credential store:
   - Google Workspace OAuth (handled by MCP server)
   - `LINKEDIN_NETWORK_API_KEY`: RapidAPI professional-network-data key
   - `APOLLO_API_KEY`: Apollo.io Master API key
   - `GOOGLE_CLOUD_PROJECT_ID`: GCP project for Vertex AI Search

2. Deploy agent:
   ```bash
   POST /api/agents
   {
     "name": "corbin",
     "template": "github:abilityai/agent-corbin"
   }
   ```

3. Complete Google OAuth flow using provided authorization URL

### Example Queries

- "Triage my emails from today"
- "Schedule a meeting with John next Tuesday at 2pm"
- "Find emails about the Q4 webinar project"
- "What's on my calendar this week?"
- "Create a task to follow up with Sarah tomorrow"
- "Search contacts for people at Y Combinator"
- "Find prospects in Bay Area working on AI"

## Local Development

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys

# Run Claude Code
claude
```

## Architecture

- **MCP Server**: google_workspace (Gmail, Calendar, Drive, Docs, Sheets, Tasks)
- **Sub-Agents**: fibery-manager, fibery-task-manager, file-system-indexer, youtube-manager, apollo-manager, scheduled-task-executor, vector-store-indexer
- **Memory System**: Persistent memory in memory/ folder with action logs
- **Capabilities**: LinkedIn lead research, Apollo.io campaign management, call transcript search

## Version

Version 2.0 - Initial Trinity-compatible release
