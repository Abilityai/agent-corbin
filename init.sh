#!/bin/bash
# Trinity agent initialization script
# This script is run by Trinity when the agent container starts

set -e

echo "Initializing Corbin agent..."

# Check for required environment variables
if [ -z "$GOOGLE_CLOUD_PROJECT_ID" ]; then
    echo "Warning: GOOGLE_CLOUD_PROJECT_ID not set"
fi

# Create necessary directories
mkdir -p memory
mkdir -p .claude/memory
mkdir -p session-files
mkdir -p project_files

echo "Corbin agent initialized successfully"
