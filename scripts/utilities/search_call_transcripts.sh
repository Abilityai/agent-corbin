#!/bin/bash

# Vertex AI Search - Call Transcripts Query Script
# Usage: ./search_call_transcripts.sh "your query here" [page_size]

QUERY="$1"
PAGE_SIZE="${2:-10}"  # Default to 10 results if not specified

if [ -z "$QUERY" ]; then
    echo "Usage: $0 \"your query\" [page_size]"
    echo "Example: $0 \"What did we discuss about AI?\" 5"
    exit 1
fi

# API endpoint
ENDPOINT="https://discoveryengine.googleapis.com/v1alpha/projects/664255702042/locations/global/collections/default_collection/engines/transcript-rag_1762512457762/servingConfigs/default_search:search"

# Execute the search
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "$ENDPOINT" \
  -d "{
    \"query\": \"$QUERY\",
    \"pageSize\": $PAGE_SIZE,
    \"queryExpansionSpec\": {\"condition\": \"AUTO\"},
    \"spellCorrectionSpec\": {\"mode\": \"AUTO\"},
    \"languageCode\": \"en-US\",
    \"contentSearchSpec\": {
      \"extractiveContentSpec\": {\"maxExtractiveAnswerCount\": 1}
    },
    \"userInfo\": {\"timeZone\": \"Europe/Lisbon\"}
  }"
