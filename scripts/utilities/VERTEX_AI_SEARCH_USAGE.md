# Vertex AI Search - Call Transcripts

## Overview
Semantic search and Q&A over call transcripts stored in Google Drive using Vertex AI Search RAG engine.

## API Details
- **Project ID**: 664255702042
- **Engine ID**: transcript-rag_1762512457762
- **Data Source**: Google Drive folder - Call Transcripts
- **Authentication**: gcloud auth (OAuth 2.0)

## Usage

### Python Script (Recommended)
```bash
# Basic search
./search_call_transcripts.py "your query here"

# Limit results
./search_call_transcripts.py "your query" -n 5

# Verbose output with snippets
./search_call_transcripts.py "your query" -v

# Raw JSON output
./search_call_transcripts.py "your query" --json
```

### Bash Script
```bash
# Basic search (10 results)
./search_call_transcripts.sh "your query"

# Custom page size
./search_call_transcripts.sh "your query" 5
```

### Direct cURL
```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/664255702042/locations/global/collections/default_collection/engines/transcript-rag_1762512457762/servingConfigs/default_search:search" \
  -d '{
    "query": "your query",
    "pageSize": 10,
    "queryExpansionSpec": {"condition": "AUTO"},
    "spellCorrectionSpec": {"mode": "AUTO"},
    "languageCode": "en-US",
    "contentSearchSpec": {
      "extractiveContentSpec": {"maxExtractiveAnswerCount": 1}
    },
    "userInfo": {"timeZone": "Europe/Lisbon"}
  }'
```

## Example Queries
```bash
# Find discussions about specific topics
./search_call_transcripts.py "media buying automation"

# Find who you talked to about something
./search_call_transcripts.py "Who did Eugene talk to about AI agents?"

# Find contract discussions
./search_call_transcripts.py "Genesis 10 contract" -v

# Recent topics
./search_call_transcripts.py "What topics have been discussed in recent calls?"
```

## Response Format
Each result includes:
- **Title**: Transcript filename
- **Owner**: Document owner (email)
- **Link**: Direct Google Drive link
- **Extractive Answer**: AI-extracted relevant passage
- **Snippets**: Context snippets (in verbose mode)

## Authentication
Requires active gcloud authentication:
```bash
# Check current auth status
gcloud auth list

# Re-authenticate if needed
gcloud auth login

# Print access token (for debugging)
gcloud auth print-access-token
```

## API Features
- **Query Expansion**: Automatically expands queries for better results
- **Spell Correction**: Auto-corrects spelling mistakes
- **Extractive Answers**: Returns relevant passages from transcripts
- **Semantic Search**: Uses vector embeddings for context-aware search
- **Pagination**: Support for large result sets with nextPageToken

## Notes
- No API keys needed - uses gcloud OAuth tokens
- Access tokens expire after 1 hour (automatically refreshed by gcloud)
- Search is case-insensitive and handles natural language queries
- Results are ranked by relevance using Google's ranking algorithms
