# Meeting Preparation Command

## Objective
Prepare Eugene for an upcoming meeting by gathering comprehensive context about attendees through cascading research across multiple sources.

## Execution Steps

### 1. Get Current Time
- Query system time to establish "now" reference point

### 2. Find Upcoming Meeting
- Search calendar events from current time to +2 hours ahead
- Identify the next meeting (within 30-60 minutes is typical)
- Extract meeting details:
  - Title/subject
  - Start/end time
  - Attendee names and emails
  - Meeting description/agenda if available
  - Meeting platform (Google Meet, Zoom, etc.)

### 3. Identify Attendees
- Extract all attendee email addresses (excluding eugene@ability.ai)
- Parse names and associated domains/companies from email addresses
- Create a list of people to research

### 4. Cascading Research Strategy

For **EACH** attendee, follow this waterfall approach:

#### Level 1: Gmail Search (ALWAYS START HERE)
- Search emails from/to the attendee's email address
- Look for recent conversations (last 3-6 months prioritized)
- Extract key context:
  - Previous discussion topics
  - Relationship history (how we met, past meetings)
  - Current projects or initiatives discussed
  - Pain points or needs mentioned
  - Any pending action items or follow-ups

**Decision Point**: If Gmail provides substantial context (5+ relevant emails or clear conversation history), summarize and move to next attendee. If minimal/no context found, proceed to Level 2.

#### Level 2: LinkedIn Research (IF NEEDED)
- Search for the person's LinkedIn profile using name + company domain
- Extract professional context:
  - Current role and company
  - Career history (previous roles)
  - Recent posts or activity (last 30-90 days)
  - Shared connections or interests
  - Company information and industry

**Decision Point**: If LinkedIn provides good professional context, summarize and move to next attendee. If profile not found or minimal info, proceed to Level 3.

#### Level 3: Apollo.io Enrichment (IF NEEDED)
- Use Apollo to enrich contact information
- Search for:
  - Verified professional details
  - Company information and technographics
  - Recent company news or job postings
  - Decision-maker role and responsibilities
  - Company size, funding, and growth indicators

### 5. Compile Meeting Brief

Create a structured brief with:

**Meeting Overview:**
- Time: [exact time, how many minutes away]
- Duration: [length]
- Attendees: [names, roles, companies]
- Platform: [meeting link/location]

**Attendee Intelligence:**

For each person:
- **Name & Role**: [title at company]
- **Context Source**: [Gmail/LinkedIn/Apollo - which level provided info]
- **Key Background**:
  - Relationship history (if from Gmail)
  - Professional background (if from LinkedIn/Apollo)
  - Company context
- **Recent Activity/Topics**:
  - Last conversation date and topic
  - Recent LinkedIn posts or engagement
  - Company news or developments
- **Talking Points/Preparation**:
  - Questions to ask
  - Topics to discuss
  - Follow-ups needed

**Meeting Preparation Summary:**
- Suggested talking points
- Key questions to prepare
- Context flags (any urgent items, pending decisions, etc.)

## Output Format

Present the brief in clean markdown format, prioritized by relevance. Flag any critical information that requires immediate attention.

## Efficiency Rules

1. **Stop researching when you have enough**: Don't proceed to next level if current level provides substantial context
2. **Parallel research**: Research multiple attendees simultaneously when possible
3. **Focus on recency**: Prioritize recent information (last 90 days) over older data
4. **Actionable insights**: Focus on information that helps Eugene prepare, not exhaustive bios
5. **Time-sensitive**: Complete research quickly - this is prep for an imminent meeting

## Example Usage

User: "/prep-meeting" or "prep for my next meeting"

Expected outcome: Within 30-60 seconds, Eugene receives a comprehensive brief about upcoming meeting with actionable context about each attendee.
