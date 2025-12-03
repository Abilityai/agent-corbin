---
description: Initialize and verify system readiness
---

Initialize Corbin 2.0 and verify all systems are operational.

**System Checks:**

1. **Memory Map** - Load memory overview:
   ```bash
   cat memory/memory_map.yaml
   ```

2. **Google Workspace** - Test authentication:
   ```
   mcp__google_workspace__list_calendars with user_google_email: "eugene@ability.ai"
   ```

3. **Vertex AI Search** - Test transcript search:
   ```bash
   timeout 15 scripts/utilities/search_call_transcripts.py "test" -n 1
   ```

   **If authentication fails**, run reauthentication:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```
   Then retry the test.

4. **Load Profile** - Load basic user profile:
   ```bash
   jq '.profile' memory/memory_index.json
   ```

5. **Recent Actions** - Show last 10 activities:
   ```bash
   head -n 10 memory/action_log.txt
   ```

6. **Google Tasks** - Load current open tasks:
   Use `mcp__google_workspace__list_tasks`:
   - user_google_email: "eugene@ability.ai"
   - task_list_id: "@default"
   - show_completed: false
   - max_results: 10

**Output Summary:**
- ✓/✗ System status for each service
- Profile name and role
- Last 5 recent actions
- Open task count
- Note: Fibery, file index, and detailed memory available on-demand
