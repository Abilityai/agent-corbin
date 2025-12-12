#!/bin/bash

# Corbin 2.0 Scheduled Task Runner
# Usage: ./corbin-scheduled-task.sh <task_name>
# Example: ./corbin-scheduled-task.sh calendar_check

set -e  # Exit on error

# Configuration
TASK_NAME="${1:-calendar_check}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKING_DIR="$(dirname "$SCRIPT_DIR")"
NOTIFICATIONS_DIR="$WORKING_DIR/notifications"
LOG_DIR="$WORKING_DIR/logs/scheduled"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ISO_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Ensure directories exist
mkdir -p "$NOTIFICATIONS_DIR" "$LOG_DIR"

# Log files
LOG_FILE="$LOG_DIR/${TASK_NAME}_${TIMESTAMP}.log"
NOTIFICATION_FILE="$NOTIFICATIONS_DIR/${TASK_NAME}_${TIMESTAMP}.md"

# Change to working directory
cd "$WORKING_DIR" || exit 1

echo "=== Corbin Scheduled Task Runner ===" | tee -a "$LOG_FILE"
echo "Task: $TASK_NAME" | tee -a "$LOG_FILE"
echo "Time: $ISO_TIMESTAMP" | tee -a "$LOG_FILE"
echo "Working Dir: $WORKING_DIR" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Get task configuration from memory
echo "Reading task configuration..." | tee -a "$LOG_FILE"
TASK_CONFIG=$(jq -r ".custom_memory.scheduled_tasks.\"${TASK_NAME}\"" memory/memory_index.json 2>/dev/null)

if [ "$TASK_CONFIG" = "null" ] || [ -z "$TASK_CONFIG" ]; then
    echo "ERROR: Task '${TASK_NAME}' not found in memory/memory_index.json" | tee -a "$LOG_FILE"
    echo "Available tasks:" | tee -a "$LOG_FILE"
    jq -r '.custom_memory.scheduled_tasks | keys[]' memory/memory_index.json 2>/dev/null | tee -a "$LOG_FILE"
    exit 1
fi

# Extract task details
TASK_ENABLED=$(echo "$TASK_CONFIG" | jq -r '.enabled // true')
TASK_PROMPT=$(echo "$TASK_CONFIG" | jq -r '.prompt')
TASK_DESCRIPTION=$(echo "$TASK_CONFIG" | jq -r '.description // "No description"')

echo "Task Description: $TASK_DESCRIPTION" | tee -a "$LOG_FILE"
echo "Task Enabled: $TASK_ENABLED" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Check if task is enabled
if [ "$TASK_ENABLED" != "true" ]; then
    echo "Task is disabled. Skipping execution." | tee -a "$LOG_FILE"
    exit 0
fi

# Build system prompt to indicate scheduled execution mode
SYSTEM_PROMPT="SCHEDULED TASK EXECUTION MODE

You are running autonomously as a scheduled task.
- Task Name: ${TASK_NAME}
- Execution Time: ${ISO_TIMESTAMP}
- Working Directory: ${WORKING_DIR}

IMPORTANT INSTRUCTIONS:
1. Execute the task prompt efficiently and completely
2. Save your final output/report to: ${NOTIFICATION_FILE}
3. Keep output concise but informative
4. Update action_log with what you did
5. Do NOT ask questions or wait for user input
6. Operate fully autonomously

Your task prompt is:
${TASK_PROMPT}"

echo "Executing Claude Code in headless mode..." | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

# Execute Claude Code in headless mode
# Using --print for non-interactive, --output-format json for structured output
# bypassPermissions allows autonomous operation without prompts
claude --print "$TASK_PROMPT" \
    --output-format json \
    --append-system-prompt "$SYSTEM_PROMPT" \
    --permission-mode bypassPermissions \
    --allowedTools "Bash Read Write Edit mcp__google_workspace__* mcp__fibery-mcp-server__* WebSearch WebFetch Glob Grep" \
    > "${LOG_FILE}.json" 2>&1

# Capture exit code
EXIT_CODE=$?

echo "" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" | tee -a "$LOG_FILE"

# Parse JSON output and extract result
if [ $EXIT_CODE -eq 0 ]; then
    echo "Task completed successfully" | tee -a "$LOG_FILE"

    # Extract the result text from JSON
    RESULT=$(jq -r '.result // "No result returned"' "${LOG_FILE}.json" 2>/dev/null)
    COST=$(jq -r '.total_cost_usd // "unknown"' "${LOG_FILE}.json" 2>/dev/null)
    DURATION=$(jq -r '.duration_ms // "unknown"' "${LOG_FILE}.json" 2>/dev/null)

    echo "Cost: \$$COST" | tee -a "$LOG_FILE"
    echo "Duration: ${DURATION}ms" | tee -a "$LOG_FILE"

    # Check if notification file was created by Claude
    if [ ! -f "$NOTIFICATION_FILE" ]; then
        echo "" | tee -a "$LOG_FILE"
        echo "Creating notification file with result..." | tee -a "$LOG_FILE"

        # Create notification file with the result
        cat > "$NOTIFICATION_FILE" <<EOF
# Scheduled Task Report: ${TASK_NAME}

**Executed:** ${ISO_TIMESTAMP}
**Status:** Success
**Duration:** ${DURATION}ms
**Cost:** \$${COST}

---

${RESULT}

---

*Generated automatically by Corbin 2.0*
EOF
    fi

    # Update last_run timestamp in memory
    echo "Updating memory with execution timestamp..." | tee -a "$LOG_FILE"
    jq ".custom_memory.scheduled_tasks.\"${TASK_NAME}\".last_run = \"${ISO_TIMESTAMP}\" | \
        .custom_memory.scheduled_tasks.\"${TASK_NAME}\".last_status = \"success\" | \
        .custom_memory.scheduled_tasks.\"${TASK_NAME}\".last_cost_usd = ${COST}" \
        memory/memory_index.json > memory/memory_index.json.tmp && \
        mv memory/memory_index.json.tmp memory/memory_index.json

else
    echo "ERROR: Task failed with exit code $EXIT_CODE" | tee -a "$LOG_FILE"

    # Create error notification
    cat > "$NOTIFICATION_FILE" <<EOF
# Scheduled Task FAILED: ${TASK_NAME}

**Executed:** ${ISO_TIMESTAMP}
**Status:** Failed (Exit Code: ${EXIT_CODE})

## Error Details

See log file: ${LOG_FILE}

---

*Generated automatically by Corbin 2.0*
EOF

    # Update memory with failure
    jq ".custom_memory.scheduled_tasks.\"${TASK_NAME}\".last_run = \"${ISO_TIMESTAMP}\" | \
        .custom_memory.scheduled_tasks.\"${TASK_NAME}\".last_status = \"failed\"" \
        memory/memory_index.json > memory/memory_index.json.tmp && \
        mv memory/memory_index.json.tmp memory/memory_index.json
fi

echo "" | tee -a "$LOG_FILE"
echo "Notification saved to: $NOTIFICATION_FILE" | tee -a "$LOG_FILE"
echo "Full log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "JSON output: ${LOG_FILE}.json" | tee -a "$LOG_FILE"

# Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null
find "$LOG_DIR" -name "*.json" -mtime +30 -delete 2>/dev/null
find "$NOTIFICATIONS_DIR" -name "*.md" -mtime +30 -delete 2>/dev/null

echo "" | tee -a "$LOG_FILE"
echo "=== Task Runner Complete ===" | tee -a "$LOG_FILE"

exit $EXIT_CODE
