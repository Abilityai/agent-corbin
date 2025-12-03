# Corbin 2.0 Scheduler

Autonomous task execution system for scheduled operations.

## Architecture

```
Task Config (memory/memory_index.json)
  → corbin-scheduled-task.sh
  → claude --print (headless mode)
  → Output saved to notifications/
  → Memory updated with execution data
```

## Usage

```bash
# Run task manually
./scripts/corbin-manage.sh run <task_name>

# List all tasks
./scripts/corbin-manage.sh list

# Enable/disable tasks
./scripts/corbin-manage.sh enable <task_name>
./scripts/corbin-manage.sh disable <task_name>

# View results
./scripts/corbin-manage.sh view-notification [task_name]
./scripts/corbin-manage.sh logs [task_name]
```

## Task Configuration

Tasks defined in `memory/memory_index.json` under `custom_memory.scheduled_tasks`:

```json
{
  "task_name": {
    "description": "What the task does",
    "prompt": "Instructions for Corbin to execute",
    "schedule": "daily|every_10_minutes|weekly|manual",
    "enabled": true|false,
    "last_run": "ISO timestamp",
    "last_status": "success|failed",
    "last_cost_usd": 0.23
  }
}
```

## Available Tasks

- **calendar_check**: Daily calendar review with conflict detection
- **email_priority_scan**: Monitor inbox for urgent items (disabled by default)
- **simple_test**: Verify scheduler functionality

## Output

- **Notifications**: `notifications/<task>_<timestamp>.md` - Human-readable reports
- **Logs**: `logs/scheduled/<task>_<timestamp>.log` - Execution logs
- **JSON**: `logs/scheduled/<task>_<timestamp>.log.json` - Structured output

## Automation Setup

Use launchd (macOS) or cron for scheduled execution:

```bash
# Example: Run calendar_check daily at 8 AM
# Add to ~/Library/LaunchAgents/com.corbin.calendar_check.plist
```

See `corbin-scheduled-task.sh` for launchd plist examples in comments.

## How It Works

1. Script reads task config from memory
2. Builds system prompt with "SCHEDULED TASK EXECUTION MODE" flag
3. Launches Claude in headless mode with `--print --permission-mode bypassPermissions`
4. Claude detects scheduled mode via system prompt, operates autonomously
5. Output saved to notifications/, memory updated with timestamp/cost
6. Old logs/notifications cleaned up (30 days retention)

## Cost Tracking

Each execution logs cost in memory. Example costs:
- Simple test: ~$0.23
- Calendar check: ~$0.15
- Email scan: ~$0.10 (estimated)

Daily automation with calendar_check + hourly email_scan ≈ $0.15 + (24 × $0.10) = ~$2.55/day
