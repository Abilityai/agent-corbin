#!/bin/bash

# Corbin 2.0 Scheduler Management Script
# Usage: ./corbin-manage.sh <command> [task_name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKING_DIR="$(dirname "$SCRIPT_DIR")"
MEMORY_FILE="$WORKING_DIR/memory/memory_index.json"

cd "$WORKING_DIR" || exit 1

command="${1:-help}"
task_name="$2"

case "$command" in
    list)
        echo "=== Scheduled Tasks ==="
        echo ""
        jq -r '.custom_memory.scheduled_tasks | to_entries[] |
            "\(.key):\n  Description: \(.value.description)\n  Schedule: \(.value.schedule)\n  Enabled: \(.value.enabled)\n  Last Run: \(.value.last_run // "never")\n  Last Status: \(.value.last_status // "n/a")\n  Last Cost: $\(.value.last_cost_usd // "n/a")\n"' \
            "$MEMORY_FILE"
        ;;

    status)
        if [ -z "$task_name" ]; then
            echo "Usage: $0 status <task_name>"
            exit 1
        fi

        echo "=== Task Status: $task_name ==="
        jq -r ".custom_memory.scheduled_tasks.\"${task_name}\" // \"Task not found\"" "$MEMORY_FILE"
        ;;

    enable)
        if [ -z "$task_name" ]; then
            echo "Usage: $0 enable <task_name>"
            exit 1
        fi

        jq ".custom_memory.scheduled_tasks.\"${task_name}\".enabled = true" "$MEMORY_FILE" > tmp.json && \
            mv tmp.json "$MEMORY_FILE"
        echo "✓ Task '$task_name' enabled"
        ;;

    disable)
        if [ -z "$task_name" ]; then
            echo "Usage: $0 disable <task_name>"
            exit 1
        fi

        jq ".custom_memory.scheduled_tasks.\"${task_name}\".enabled = false" "$MEMORY_FILE" > tmp.json && \
            mv tmp.json "$MEMORY_FILE"
        echo "✓ Task '$task_name' disabled"
        ;;

    run)
        if [ -z "$task_name" ]; then
            echo "Usage: $0 run <task_name>"
            exit 1
        fi

        echo "Running task: $task_name"
        echo ""
        "$SCRIPT_DIR/corbin-scheduled-task.sh" "$task_name"
        ;;

    logs)
        if [ -z "$task_name" ]; then
            echo "Recent logs (all tasks):"
            ls -lht logs/scheduled/ | head -20
        else
            echo "Recent logs for: $task_name"
            ls -lht logs/scheduled/ | grep "$task_name" | head -10
        fi
        ;;

    notifications)
        if [ -z "$task_name" ]; then
            echo "Recent notifications (all tasks):"
            ls -lht notifications/ | head -20
        else
            echo "Recent notifications for: $task_name"
            ls -lht notifications/ | grep "$task_name" | head -10
        fi
        ;;

    view-notification)
        if [ -z "$task_name" ]; then
            # Show most recent notification
            latest=$(ls -t notifications/*.md | head -1)
            if [ -n "$latest" ]; then
                echo "=== Most Recent Notification ==="
                echo "File: $latest"
                echo ""
                cat "$latest"
            else
                echo "No notifications found"
            fi
        else
            # Show most recent notification for specific task
            latest=$(ls -t notifications/${task_name}_*.md 2>/dev/null | head -1)
            if [ -n "$latest" ]; then
                echo "=== Most Recent Notification: $task_name ==="
                echo "File: $latest"
                echo ""
                cat "$latest"
            else
                echo "No notifications found for task: $task_name"
            fi
        fi
        ;;

    clean)
        echo "Cleaning old logs and notifications (>30 days)..."
        find logs/scheduled -name "*.log" -mtime +30 -delete
        find logs/scheduled -name "*.json" -mtime +30 -delete
        find notifications -name "*.md" -mtime +30 -delete
        echo "✓ Cleanup complete"
        ;;

    help|*)
        cat <<EOF
Corbin 2.0 Scheduler Management

Usage: $0 <command> [task_name]

Commands:
  list                    List all scheduled tasks with status
  status <task>           Show detailed status for a specific task
  enable <task>           Enable a scheduled task
  disable <task>          Disable a scheduled task
  run <task>              Run a task manually (test execution)
  logs [task]             Show recent log files (optionally filter by task)
  notifications [task]    Show recent notifications (optionally filter by task)
  view-notification [task] View the most recent notification content
  clean                   Remove old logs and notifications (>30 days)
  help                    Show this help message

Examples:
  $0 list
  $0 run calendar_check
  $0 enable email_priority_scan
  $0 status simple_test
  $0 view-notification calendar_check
  $0 logs calendar_check

EOF
        ;;
esac
