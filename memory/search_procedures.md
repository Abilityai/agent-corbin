# Corbin 2.0 Workspace - Optimal Search Procedures Guide

## Quick Reference Decision Tree

```
WHAT ARE YOU LOOKING FOR?
│
├─→ CONTACTS / PEOPLE INFORMATION
│   → See Section 1: Contact Search
│
├─→ CALL TRANSCRIPTS / MEETING DISCUSSIONS
│   → See Section 2: Call Transcript Search
│
├─→ BUSINESS DOCS / PROCESSES / STRATEGY
│   → See Section 3: Business Documentation Search
│
├─→ SCRIPTS / CODE / AUTOMATION
│   → See Section 4: Script and Code Search
│
├─→ PAST DECISIONS / ACTION HISTORY
│   → See Section 5: Memory System Search
│
├─→ PROJECT FILES / SESSION WORK
│   → See Section 6: Project Files Search
│
└─→ GENERAL SEMANTIC SEARCH (concepts, ideas)
    → See Section 7: Vector Search
```

---

## Section 1: Contact Search

**Data Source**: Enriched contacts with LinkedIn + Apollo + Google Contacts data

### Search Method Selection

#### 1A: Exact Company Match (100% precision)
**Use when**: "Who works at [company]?" "Current employees at X"

```bash
# Direct grep - fastest and most accurate
grep -l "current_company: Google" \
  "$AGENTS_DIR/contact-management-agent/linkedin_contacts/"*.json
```

#### 1B: Employment History (past or present)
**Use when**: "Who worked at [company]?" "Anyone with Google background"

```bash
# Grep for wiki-link pattern in employment history
grep -l "at \[\[Google\]\]" \
  "$GOOGLE_DRIVE_PATH/ContactsDatabase/Contacts/People/"*.md
```

#### 1C: Location + Role (Multi-criteria)
**Use when**: "Find CTOs in San Francisco" "AI founders in NYC"

**Best Practice** (100% precision achieved):
1. Use Contact Management Agent (headless mode)
2. Query uses abbreviated terms: "CTO San Francisco" (NOT "Chief Technology Officer")
3. Agent performs dual validation (location AND current role)

```bash
cd $AGENTS_DIR/contact-management-agent
claude -p "Find CTOs in San Francisco" \
  --permission-mode bypassPermissions \
  --output-format json \
  --timeout 300000
```

#### 1D: Expertise / Skills Search
**Use when**: "Find machine learning experts" "AI researchers"

**Recommended**: Contact Management Agent with semantic search
- Agent validates across multiple fields (expertise_areas, professional background, employment history)
- NOT just current title (can be misleading)
- Target precision: 80-85%

```bash
cd $AGENTS_DIR/contact-management-agent
claude -p "Find machine learning experts" \
  --permission-mode bypassPermissions \
  --output-format json \
  --timeout 300000
```

#### 1E: Deep Profile / Relationship Network
**Use when**: "Tell me about [person]" "Who is similar to X?" "Connection map"

**Recommended**: Contact Management Agent (uses Smart Connections MCP)
- Full profile with career history
- Similar professionals via semantic similarity
- Connection graph (shared employers, geographic clusters)

```bash
cd $AGENTS_DIR/contact-management-agent
claude -p "Tell me about Shiv Sakhuja and find similar people" \
  --permission-mode bypassPermissions \
  --output-format json \
  --timeout 300000
```

### Critical Contact Search Rules

✅ **DO:**
- Use Contact Management Agent for complex/semantic queries
- Use direct grep for exact field matches (company, location)
- Validate multi-criteria results (don't trust single field)
- Use abbreviated role terms ("CTO" not "Chief Technology Officer")

❌ **DON'T:**
- Query raw JSON files unless Contact Management Agent unavailable
- Trust current_title alone for expertise queries (check multiple fields)
- Use expanded role names (matches unintended results)

---

## Section 2: Call Transcript Search

**Data Source**: Google Drive folder with Vertex AI Search RAG engine

### When to Use
- "Who did I talk to about [topic]?"
- "What was discussed about [project]?"
- "Find mentions of [company/person] in calls"
- "Recent topics in meetings"

### Search Command

```bash
# Python script (formatted, recommended)
$AGENTS_DIR/Corbin20/scripts/utilities/search_call_transcripts.py \
  "your query" -n 10

# Verbose mode with snippets
$AGENTS_DIR/Corbin20/scripts/utilities/search_call_transcripts.py \
  "your query" -v

# Bash script (raw JSON)
$AGENTS_DIR/Corbin20/scripts/utilities/search_call_transcripts.sh \
  "your query" 10
```

### Features
- **Natural language queries** - Ask conversationally
- **Extractive answers** - AI extracts relevant passages
- **Auto query expansion** - Improves recall
- **Spell correction** - Handles typos
- **Direct links** - Returns Google Drive URLs

### Example Queries
```bash
# Topic-based
search_call_transcripts.py "media buying automation"

# Person-based
search_call_transcripts.py "Who did [User] talk to about AI agents?"

# Project-based
search_call_transcripts.py "Genesis 10 contract" -v

# Time-based
search_call_transcripts.py "What topics have been discussed in recent calls?"
```

### Performance
- **No API keys needed** - Uses gcloud auth
- **Response time**: 2-5 seconds
- **Access token**: Auto-refreshed by gcloud (1 hour expiry)

---

## Section 3: Business Documentation Search

**Data Source**: `source-of-truth/` git repository (31 folders)

### When to Use
- Sales processes and methodologies
- OKRs and strategic planning
- Company positioning and messaging
- ICP definitions and market analysis
- Case studies and delivery documentation

### Search Strategy

#### 3A: Known Document Name
```bash
# Direct file read if you know the filename
cat $AGENTS_DIR/Corbin20/source-of-truth/sales_process_3.0.md
cat $AGENTS_DIR/Corbin20/source-of-truth/Q4_2025_OKRs.md
```

#### 3B: Topic-Based Search (Semantic)
```bash
# Vector search across all source-of-truth documents
cd $AGENTS_DIR/vector-store-project
./run_search.sh "sales methodology" --folder source-of-truth
./run_search.sh "ideal customer profile" --folder source-of-truth
```

#### 3C: Keyword Search (Exact Match)
```bash
# Grep for exact terms
grep -r "Apollo.io" $AGENTS_DIR/Corbin20/source-of-truth/
grep -r "AI Copilot ICP" $AGENTS_DIR/Corbin20/source-of-truth/
```

#### 3D: Browse Structure
```bash
# List all business documentation areas
ls -la $AGENTS_DIR/Corbin20/source-of-truth/

# Key folders:
# - sales/ - Sales processes and playbooks
# - marketing/ - Marketing strategies and content
# - ceo_zone/ - Strategic CEO documentation
# - delivery/ - Implementation and delivery docs
# - case_studies/ - Customer success stories
# - SOLUTIONS/ - Product solutions and positioning
```

### Git Workflow Reminders
```bash
# Always pull before reading potentially stale docs
cd $AGENTS_DIR/Corbin20/source-of-truth
git pull

# At session end, remind user to commit changes
git status
# (prompt user to commit if files modified)
```

---

## Section 4: Script and Code Search

**Data Source**: `scripts/` folder with organized subdirectories

### Search Strategy

#### 4A: By Functional Area (Browse)
```bash
# List all script categories
ls -la $AGENTS_DIR/Corbin20/scripts/

# Key folders:
# - contact-enrichment/ - Contact database management (33 files)
# - utilities/ - General-purpose helpers (9 files)
# - scheduled-tasks/ - Automation and cron jobs (5 files)
# - integrations/ - Third-party API clients (2 files)
# - research/ - Research and analysis scripts (4 files)
```

#### 4B: By Purpose (Semantic Search)
```bash
# Vector search for script functionality
cd $AGENTS_DIR/vector-store-project
./run_search.sh "email automation script" --folder scripts
./run_search.sh "LinkedIn enrichment" --folder scripts/contact-enrichment
./run_search.sh "Google Contacts sync" --folder scripts
```

#### 4C: By Technology (Grep)
```bash
# Find scripts using specific APIs or libraries
grep -r "gmail" $AGENTS_DIR/Corbin20/scripts/ --include="*.py"
grep -r "Apollo.io" $AGENTS_DIR/Corbin20/scripts/ --include="*.py"
grep -r "vertex" $AGENTS_DIR/Corbin20/scripts/ --include="*.py"
```

#### 4D: By Filename Pattern (Glob)
```bash
# Find scripts by naming convention
find $AGENTS_DIR/Corbin20/scripts/ -name "*enrichment*.py"
find $AGENTS_DIR/Corbin20/scripts/ -name "*sync*.py"
find $AGENTS_DIR/Corbin20/scripts/ -name "*mcp*.py"
```

### Script Organization Rules
- **All scripts** must be in `scripts/` subdirectories (NEVER root)
- **Related files grouped** (code + artifacts + outputs in same folder)
- **README files** only when explicitly requested by user
- **Code is documentation** - prioritize clear, commented code

---

## Section 5: Memory System Search

**Data Source**: `memory/` folder (persistent agent memory)

### Memory Components

#### 5A: Recent Actions (Action Log)
**Use when**: "What did I do recently?" "Last session summary"

```bash
# Read top 50 recent actions (reverse chronological)
head -50 $AGENTS_DIR/Corbin20/memory/action_log.txt
```

**Format**: `YYYY-MM-DD HH:MM:SS - Action description`
**Note**: Newest entries at TOP

#### 5B: User Profile and Preferences
**Use when**: Need [User]'s communication style, business info, preferences

```bash
# Targeted jq queries (don't load entire file)
jq '.profile' $AGENTS_DIR/Corbin20/memory/memory_index.json
jq '.preferences.communication_style' $AGENTS_DIR/Corbin20/memory/memory_index.json
```

#### 5C: Key Facts and Past Decisions
**Use when**: Need context on previous choices, important statements

```bash
jq '.memory.key_facts' $AGENTS_DIR/Corbin20/memory/memory_index.json
jq '.memory.past_decisions' $AGENTS_DIR/Corbin20/memory/memory_index.json
```

#### 5D: Entities (People, Projects, Organizations)
**Use when**: Need relationship context, project details

```bash
jq '.entities.people' $AGENTS_DIR/Corbin20/memory/memory_index.json
jq '.entities.projects' $AGENTS_DIR/Corbin20/memory/memory_index.json
```

#### 5E: Current Context
**Use when**: Need to understand current work, active topics

```bash
jq '.context.current_task' $AGENTS_DIR/Corbin20/memory/memory_index.json
jq '.context.active_topics' $AGENTS_DIR/Corbin20/memory/memory_index.json
```

#### 5F: File System Index
**Use when**: Need to understand project structure, recent modifications

```bash
# Large file (424KB) - use grep to find specific folders/files
grep "source-of-truth" $AGENTS_DIR/Corbin20/memory/file_index.md
grep "scripts" $AGENTS_DIR/Corbin20/memory/file_index.md
```

### Memory Access Best Practices
✅ **Use targeted jq queries** - Don't load entire memory_index.json
✅ **Check memory_map.yaml first** - Understand what's available
✅ **Action log for recent context** - Top 50 lines sufficient
❌ **Don't load file_index.md entirely** - Use grep for specific lookups

---

## Section 6: Project Files Search

**Data Source**: `project_files/` and `session-files/` folders

### 6A: Ongoing Projects
**Location**: `project_files/[project_name]/`

```bash
# List all active projects
ls -la $AGENTS_DIR/Corbin20/project_files/

# Search within specific project
grep -r "keyword" $AGENTS_DIR/Corbin20/project_files/us_trip_planning/
```

### 6B: Session Work (Temporary)
**Location**: `session-files/YYYY-MM-DD_activity_name/`

```bash
# List recent sessions
ls -lt $AGENTS_DIR/Corbin20/session-files/ | head -10

# Search recent session files
find $AGENTS_DIR/Corbin20/session-files/ -name "*.md" -mtime -7
```

### 6C: Semantic Search Across Projects
```bash
# Vector search across all project files
cd $AGENTS_DIR/vector-store-project
./run_search.sh "conference planning" --folder project_files
./run_search.sh "stakeholder questionnaire" --folder session-files
```

---

## Section 7: Vector Search (General Semantic)

**Data Source**: 5,165 documents indexed in txtai vector store

### When to Use
- Conceptual search across entire workspace
- Don't know exact location of information
- Exploring related documents
- Finding similar content across different folders

### Search Commands

#### 7A: Single Query
```bash
cd $AGENTS_DIR/vector-store-project
./run_search.sh "your query" --limit 10
```

#### 7B: Folder-Scoped Search
```bash
./run_search.sh "query" --folder source-of-truth/marketing
./run_search.sh "query" --folder scripts/contact-enrichment
```

#### 7C: Interactive Mode (Exploratory)
```bash
./run_search.sh -i

# Then use:
Search> folder:source-of-truth sales methodology
Search> machine learning contacts
Search> quit
```

### Vector Search Performance
- **Indexed documents**: 5,165 files
- **Search speed**: Sub-second
- **Embedding model**: sentence-transformers/all-MiniLM-L6-v2 (384-dim)
- **Storage**: Persistent index in `$AGENTS_DIR/vector-store-project/index/`

### Re-indexing (When Needed)
```bash
cd $AGENTS_DIR/vector-store-project
./run_index.sh $AGENTS_DIR/Corbin20

# Re-index when:
# - New files added
# - Significant content changes
# - User requests it
```

---

## Section 8: Specialized Sub-Agents

### When to Delegate

#### 8A: Fibery Workspace Queries
**Delegate to**: @fibery-manager (CRM) or @fibery-task-manager (tasks)
```
User: "Show me all leads from Google"
→ Automatic delegation to @fibery-manager
```

#### 8B: YouTube Content Analysis
**Delegate to**: @youtube-manager
```
User: "How is my YouTube channel performing?"
→ Automatic delegation to @youtube-manager
```

#### 8C: Apollo.io Sales Intelligence
**Delegate to**: @apollo-manager
```
User: "Find AI startup founders in Bay Area"
→ Automatic delegation to @apollo-manager
```

#### 8D: File System Indexing
**Delegate to**: @file-system-indexer
```
Command: /re-index-files
→ Generates comprehensive directory tree
```

---

## Section 9: Abilities (User-Invoked)

### Slash Commands (User Must Call)

#### 9A: LinkedIn Profile Research
```
User: "Research this LinkedIn profile: [URL]"
You: /linkedin-lead-research
```

#### 9B: Apollo Campaign Management
```
User: "Search for prospects on Apollo"
You: /apollo-campaign-manager
```

**Important**: These are NOT automatically invoked - user must explicitly call them with `/command-name`

---

## Performance Optimization Tips

### Fastest Methods by Query Type

| Query Type | Fastest Method | Est. Time |
|------------|----------------|-----------|
| Exact company match | `grep` on JSON files | <1 sec |
| Known filename | Direct file read | <1 sec |
| Vector semantic search | txtai search | <1 sec |
| Contact relationship graph | Contact Management Agent | 2-5 min |
| Call transcript search | Vertex AI Search script | 2-5 sec |
| Memory lookup | `jq` query | <1 sec |

### When to Use Each Tool

- **grep**: Exact field matches, structured data, fast
- **find**: File name patterns, file discovery
- **jq**: JSON queries, memory access, targeted extraction
- **Vector search**: Semantic queries, concept exploration, unknown location
- **Sub-agents**: Complex domain-specific operations
- **Direct read**: Known file paths, quick lookups

---

## Common Search Patterns

### Pattern 1: "Find information about [topic]"
1. Check memory (action log, key facts) - 1 sec
2. Try vector search across workspace - 1 sec
3. If business-related → source-of-truth/ grep or vector search
4. If technical → scripts/ search
5. If person → Contact Management Agent

### Pattern 2: "What did I do about [X]?"
1. Action log (top 50 lines) - 1 sec
2. Memory key facts and past decisions - 1 sec
3. Vector search in relevant folder - 1 sec
4. Call transcript search if potentially discussed - 5 sec

### Pattern 3: "Who can help with [Y]?"
1. Contact Management Agent with expertise query - 2-5 min
2. Validate across multiple fields (not just title)
3. Get relationship network and connection opportunities

### Pattern 4: "Find the document about [Z]"
1. If business process → source-of-truth/ folder
2. If technical → scripts/ folder
3. If project-specific → project_files/
4. Use vector search if location uncertain
5. Grep for exact keywords if known

---

## Key Takeaways

✅ **Contact queries** → Contact Management Agent (semantic, validated) or grep (exact)
✅ **Call transcripts** → Vertex AI Search script (natural language)
✅ **Business docs** → source-of-truth/ (git pull first, then vector or grep)
✅ **Scripts** → scripts/ subdirectories (vector or grep)
✅ **Memory** → Targeted jq queries (efficient, fast)
✅ **Projects** → project_files/ (vector or grep)
✅ **General semantic** → Vector search with folder filters

❌ **Don't** query raw contact JSON files (use Contact Management Agent)
❌ **Don't** load entire memory_index.json (use jq queries)
❌ **Don't** search entire file_index.md (use grep for specific lookups)
❌ **Don't** skip git pull on source-of-truth/ (could be stale)
❌ **Don't** forget to validate multi-criteria contact queries

---

**This guide provides optimal search procedures for 95%+ precision across all information types in the Corbin 2.0 workspace.**
