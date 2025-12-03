#!/bin/bash
# Wrapper script to run linkedin_api.py with the skill's local venv

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
API_SCRIPT="$SCRIPT_DIR/linkedin_api.py"

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found. Run ./setup.sh first" >&2
    exit 1
fi

# Run the API script with all arguments
exec "$VENV_PYTHON" "$API_SCRIPT" "$@"
