# Containerized Claude Code Agent Platform

## System Overview
Self-contained, single-tenant AI agent platform providing Claude Code capabilities via Docker container with web-based configuration and multi-channel access (Slack initially).

## Core Principles
- **Data Sovereignty**: All user data remains within container boundaries
- **Single Tenant**: One container per user/organization
- **Zero Trust**: No external data transmission except to configured services
- **Git-Backed**: Configuration and state synchronized with user's repository
- **Plug-and-Play**: Pre-configured agent templates with customizable MCPs

## Architecture Components

### 1. Docker Container Structure
```
claude-agent-container/
├── claude-code/          # Claude Code CLI binary
├── workspace/            # User's working directory (git repo mount)
├── config/
│   ├── .mcp.json        # MCP server configurations
│   ├── claude.yaml      # Agent configuration
│   └── credentials/     # Encrypted credential store
├── web-interface/       # Configuration UI
├── api-gateway/         # Slack/External integration layer
└── supervisor/          # Process manager
```

### 2. Core Services

#### Claude Code Engine
- Runs in headless mode (`claude -p` interface)
- Configured via environment variables and mounted configs
- Access to workspace directory (user's repository)
- MCP servers for tool access

#### Web Configuration Interface
- **Port**: 8080 (configurable)
- **Auth**: Token-based authentication
- **Features**:
  - Credential management (encrypted storage)
  - MCP server configuration
  - Agent template selection
  - Git repository settings
  - Slack integration setup
  - Activity monitoring

#### API Gateway Service
- **Port**: 3000 (internal)
- **Endpoints**:
  - `/slack/events` - Slack event webhook
  - `/api/execute` - Direct command execution
  - `/api/status` - Health check
- **Queue**: Redis for request queuing
- **Session**: Maintains conversation context

#### Credential Vault
- AES-256 encryption for credentials at rest
- Environment variable injection for MCPs
- Web UI for secure credential entry
- No credential logging or transmission

### 3. Integration Layer

#### Slack Integration
```yaml
slack_config:
  app_token: ${SLACK_APP_TOKEN}
  bot_token: ${SLACK_BOT_TOKEN}
  channels:
    - allowed: ["general", "ai-agent"]
    - dm_enabled: true
  commands:
    - /agent <message>
    - /agent-status
    - /agent-config
```

#### MCP Server Configuration
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["--workspace", "/workspace"],
      "env": {}
    },
    "google-workspace": {
      "command": "mcp-server-google",
      "env": {
        "GOOGLE_CREDENTIALS": "${VAULT:google_oauth}"
      }
    }
  }
}
```

### 4. Data Flow

```
User -> Slack -> API Gateway -> Queue -> Claude Code -> Response
                     ↓
            Web UI Config -> Credential Vault
                     ↓
              Git Repository (state sync)
```

## Security Model

### Container Isolation
- No outbound connections except configured services
- Read-only root filesystem
- Non-root user execution
- Capabilities dropped (CAP_DROP: ALL)

### Credential Management
- Credentials never leave container
- Web UI uses HTTPS with self-signed cert
- Token rotation for API access
- Audit logging for all credential access

### Git Synchronization
- SSH key for repository access
- Hourly config backup to `.claude-agent/` folder
- Workspace changes committed with agent signature

## Configuration Templates

### Base Agent Template
```yaml
name: base-agent
version: 1.0
capabilities:
  - filesystem
  - web_search
  - code_execution
permissions:
  allowed_tools:
    - Read
    - Write
    - Edit
    - Bash
  workspace_access: full
```

### Business Assistant Template
```yaml
extends: base-agent
additional_mcps:
  - google-workspace
  - slack
  - notion
custom_instructions: |
  You are a business assistant helping with daily operations.
  Focus on email management, calendar scheduling, and document creation.
```

## Deployment Configuration

### Docker Compose
```yaml
version: '3.8'
services:
  claude-agent:
    image: claude-agent:latest
    volumes:
      - ./workspace:/workspace
      - ./config:/config
      - credentials:/credentials
    ports:
      - "8080:8080"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - AGENT_TOKEN=${AGENT_TOKEN}
      - GIT_REPO=${GIT_REPO}
    restart: unless-stopped

volumes:
  credentials:
    driver: local
    driver_opts:
      type: none
      o: bind,encrypt=aes256
      device: ./credentials
```

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
AGENT_TOKEN=<random-32-char>
GIT_REPO=git@github.com:user/agent-workspace.git

# Optional
WEB_PORT=8080
API_PORT=3000
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
LOG_LEVEL=info
```

## Web Interface Components

### Dashboard
- Current status and health
- Recent activities log
- Active MCP connections
- Resource usage metrics

### Configuration Pages
1. **Credentials Manager**
   - Service selection dropdown
   - Secure input fields
   - Test connection button
   - Encryption status indicator

2. **MCP Servers**
   - Available servers list
   - Enable/disable toggles
   - Custom server addition
   - Configuration editor

3. **Agent Settings**
   - Template selection
   - Custom instructions editor
   - Tool permissions matrix
   - Model selection (when available)

4. **Integrations**
   - Slack workspace connection
   - Channel permissions
   - Command prefix settings
   - Webhook configuration

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- Docker container with Claude Code CLI
- Basic workspace mounting
- Headless execution capability
- Simple API endpoint

### Phase 2: Web Interface (Week 2-3)
- FastAPI/Flask web server
- Credential management UI
- Basic authentication
- Configuration persistence

### Phase 3: Slack Integration (Week 3-4)
- Slack app scaffold
- Event handling
- Message queuing
- Response formatting

### Phase 4: Security & Polish (Week 4-5)
- Credential encryption
- Git synchronization
- Audit logging
- Error handling

### Phase 5: Templates & Documentation (Week 5-6)
- Agent templates library
- User documentation
- Deployment guides
- Example configurations

## Technical Stack

### Backend
- **Claude Code**: Latest CLI version
- **Web Framework**: FastAPI (async, modern, fast)
- **Queue**: Redis (lightweight, persistent)
- **Process Manager**: Supervisor
- **Encryption**: cryptography library (Fernet)

### Frontend
- **Framework**: Vue.js 3 (simple, reactive)
- **UI Library**: Tailwind CSS
- **Build Tool**: Vite
- **State**: Pinia

### Infrastructure
- **Base Image**: Ubuntu 22.04 slim
- **Runtime**: Python 3.11
- **Node**: 20.x (for MCP servers)
- **Git**: 2.x

## Success Metrics
- Container start time < 30 seconds
- API response time < 2 seconds
- Credential encryption/decryption < 100ms
- Memory usage < 1GB idle, < 2GB active
- Zero credential leakage incidents