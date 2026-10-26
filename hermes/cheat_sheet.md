---
title: Cheat Sheet
description: Hermes Helper Sheet
published: true
date: 2026-10-26T14:13:32.645Z
tags: helpers, ai, hermes
editor: markdown
dateCreated: 2026-06-05T16:27:43.602Z
---

# Hermes Agent — Command Cheat Sheet

> **Hermes Agent** is an open-source AI agent framework by Nous Research. This cheat sheet covers all CLI commands (shell), slash commands (in-chat), and practical usage patterns.

---

## Quick Start

```bash
# Start interactive chat
hermes

# Single query (non-interactive)
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider interactively
hermes model

# Health check
hermes doctor [--fix]

# Resume last session
hermes -c
```

---

## 1. CLI Commands (Shell)

### Global Options

| Option | Description |
|--------|-------------|
| `--version, -V` | Show version |
| `--profile <name>, -p <name>` | Use a named profile |
| `--resume <session>, -r <session>` | Resume session by ID or title |
| `--continue [name], -c [name]` | Resume most recent session |
| `--worktree, -w` | Isolated git worktree mode (parallel agents) |
| `--yolo` | Skip dangerous-command approval |
| `--pass-session-id` | Include session ID in system prompt |
| `--ignore-user-config` | Skip config.yaml, use defaults |
| `--ignore-rules` | Skip AGENTS.md, SOUL.md, .cursorrules, memory |
| `--tui` | Launch TUI instead of classic CLI |
| `--skills, -s SKILL` | Preload skills (comma-separated or repeat) |

### Chat

```bash
hermes                         # Interactive chat (default)
hermes chat -q "question"      # Single query, non-interactive
hermes chat -m anthropic/claude-sonnet-4    # Specify model
hermes chat -t terminal,file,web            # Specify toolsets
hermes chat --provider openrouter           # Force provider
hermes chat -Q                              # Quiet mode (no banner/spinner)
hermes chat --checkpoints                   # Enable filesystem checkpoints
```

### Configuration

```bash
hermes setup [section]         # Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                   # Interactive model/provider picker
hermes config                  # View current config
hermes config edit             # Open config.yaml in $EDITOR
hermes config set KEY VAL      # Set a config value (e.g. `hermes config set approvals.mode smart`)
hermes config path             # Print config.yaml path
hermes config env-path         # Print .env path
hermes config check            # Check for missing/outdated config
hermes config migrate          # Update config with new options
hermes auth                    # Interactive credential manager
hermes auth add PROVIDER       # Add OAuth or API-key credential
hermes auth list               # List stored credentials
hermes auth remove PROVIDER    # Remove a stored credential
hermes doctor [--fix]          # Check dependencies and config
hermes status [--all]          # Show component status
```

**Practical examples:**
```bash
# Enable smart approval mode (auto-approve low-risk commands)
hermes config set approvals.mode smart

# Change default model
hermes config set model.default deepseek/deepseek-v4-flash

# Set terminal timeout to 5 minutes
hermes config set terminal.timeout 300
```

### Tools & Skills

```bash
hermes tools                   # Interactive tool enable/disable (curses UI)
hermes tools list              # Show all tools and status
hermes tools enable NAME       # Enable a toolset (e.g. `hermes tools enable browser`)
hermes tools disable NAME      # Disable a toolset

hermes skills list             # List installed skills
hermes skills search QUERY     # Search the skills hub
hermes skills install ID       # Install a skill (hub ID or direct SKILL.md URL)
hermes skills inspect ID       # Preview without installing
hermes skills config           # Enable/disable skills per platform
hermes skills check            # Check for updates
hermes skills update           # Update outdated skills
hermes skills uninstall N      # Remove a hub skill
hermes skills publish PATH     # Publish to registry
hermes skills browse           # Browse all available skills
hermes skills tap add REPO     # Add a GitHub repo as skill source
```

**Practical examples:**
```bash
# Install debugging skills
hermes skills install systematic-debugging
hermes skills install test-driven-development

# Enable browser toolset for web testing
hermes tools enable browser

# Browse available skills
hermes skills browse
```

### MCP Servers

```bash
hermes mcp serve               # Run Hermes as an MCP server
hermes mcp add NAME            # Add an MCP server (--url or --command)
hermes mcp remove NAME         # Remove an MCP server
hermes mcp list                # List configured servers
hermes mcp test NAME           # Test connection
hermes mcp configure NAME      # Toggle tool selection
```

### Gateway (Messaging Platforms)

```bash
hermes gateway run             # Start gateway foreground
hermes gateway install         # Install as background service
hermes gateway start/stop      # Control the service
hermes gateway restart         # Restart the service
hermes gateway status          # Check status
hermes gateway setup           # Configure platforms
```

**Practical examples:**
```bash
# Start Telegram gateway
hermes gateway setup           # Then select telegram
hermes gateway run             # Run in foreground for testing

# Install as systemd service
hermes gateway install
systemctl --user start hermes-gateway
```

### Sessions

```bash
hermes sessions list           # List recent sessions
hermes sessions browse         # Interactive picker
hermes sessions export OUT     # Export to JSONL
hermes sessions rename ID T    # Rename a session
hermes sessions delete ID      # Delete a session
hermes sessions prune          # Clean up old sessions (--older-than N days)
hermes sessions stats          # Session store statistics
```

### Cron Jobs

```bash
hermes cron list               # List jobs (--all for disabled)
hermes cron create SCHED       # Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID            # Edit schedule, prompt, delivery
hermes cron pause/resume ID    # Control job state
hermes cron run ID             # Trigger on next tick
hermes cron remove ID          # Delete a job
hermes cron status             # Scheduler status
```

**Practical examples:**
```bash
# Daily security scan at 9am
hermes cron create "0 9 * * *" \
  --name "daily-scan" \
  --prompt "Run security audit on ~/work/projects and report findings" \
  --deliver telegram

# Send daily weather every morning
hermes cron create "every 8am" \
  --name "weather" \
  --prompt "Get today's weather forecast for Zurich"

# Every 30 minutes - check server health
hermes cron create "30m" \
  --name "health-check" \
  --prompt "Check disk usage and top 3 memory processes, alert if >80%"
```

### Webhooks

```bash
hermes webhook subscribe N     # Create route at /webhooks/<name>
hermes webhook list            # List subscriptions
hermes webhook remove NAME     # Remove a subscription
hermes webhook test NAME       # Send a test POST
```

### Profiles

```bash
hermes profile list            # List all profiles
hermes profile create NAME     # Create (--clone, --clone-all, --clone-from)
hermes profile use NAME        # Set sticky default
hermes profile delete NAME     # Delete a profile
hermes profile show NAME       # Show details
hermes profile alias NAME      # Manage wrapper scripts
hermes profile rename A B      # Rename a profile
hermes profile export NAME     # Export to tar.gz
hermes profile import FILE     # Import from archive
```

**Practical examples:**
```bash
# Create a coding-specific profile
hermes profile create coding --clone-from default

# Use a different profile for this session
hermes -p coding

# Export to share with teammates
hermes profile export coding
```

### Other

```bash
hermes insights [--days N]     # Usage analytics
hermes update                  # Update to latest version
hermes pairing list/approve/revoke  # DM authorization
hermes plugins list/install/remove   # Plugin management
hermes memory setup/status/off       # Memory provider config
hermes completion bash|zsh     # Shell completions
hermes acp                     # ACP server (IDE integration)
hermes uninstall               # Uninstall Hermes
```

---

## 2. Slash Commands (In-Session)

Type `/` in the CLI to open autocomplete. Commands are case-insensitive.

### Session Control

| Command | Description | Example |
|---------|-------------|---------|
| `/new [name]` (alias: `/reset`) | Fresh session | `/new my-experiment` |
| `/clear` | Clear screen + new session | |
| `/retry` | Resend last message | After a bad response |
| `/undo` | Remove last exchange | Correct a mistake |
| `/title [name]` | Name the session | `/title API Refactor` |
| `/compress [here N]` | Manually compress context | `/compress here 3` (keep last 3 turns verbatim) |
| `/rollback [N]` | Restore filesystem checkpoint | `/rollback 2` |
| `/snapshot` | Create/restore state snapshots | `/snapshot` → `/snapshot restore` |
| `/stop` | Kill background processes | |
| `/queue <prompt>` (alias: `/q`) | Queue next turn | `/q Check disk space too` |
| `/steer <prompt>` | Inject mid-run note | `/steer Focus on the auth module` |
| `/goal <text>` | Set standing goal (Ralph loop) | `/goal Add unit tests to all new functions` |
| `/goal status/pause/resume/clear` | Manage goals | `/goal status` |
| `/subgoal <text>` | Append criterion to active goal | `/subgoal Check edge cases` |
| `/resume [name]` | Resume named session | `/resume API-Refactor` |
| `/sessions` | Browse/resume sessions | |
| `/redraw` | Force UI repaint | After tmux resize artifacts |
| `/status` | Show session info + recap | Model, provider, tokens, files touched |
| `/agents` (alias: `/tasks`) | Show active agents | |
| `/background <prompt>` (alias: `/bg`) | Run in background | `/bg Analyze these logs` |
| `/branch [name]` (alias: `/fork`) | Branch session | `/branch experiment-v2` |
| `/handoff <platform>` | Hand session to messaging | `/handoff telegram` |

### Configuration

| Command | Description | Example |
|---------|-------------|---------|
| `/config` | Show current config | |
| `/model [name]` | Show/change model | `/model claude-sonnet-4` |
| `/model provider:model` | Switch provider too | `/model openai/gpt-4o` |
| `/model fav --global` | Use alias + persist | `/model grok --global` |
| `/personality [name]` | Set personality | `/personality concise` |
| `/reasoning [level]` | Set reasoning effort | `/reasoning high` |
| `/reasoning show/hide` | Toggle reasoning display | |
| `/verbose` | Cycle tool progress display | off → new → all → verbose |
| `/fast [normal/fast/status]` | Toggle fast mode | `/fast fast` (priority processing) |
| `/skin [name]` | Change theme (CLI) | `/skin solarized` |
| `/statusbar` (alias: `/sb`) | Toggle status bar (CLI) | |
| `/voice [on/off/tts]` | Toggle voice mode | `/voice on` |
| `/yolo` | Toggle approval bypass | |
| `/footer [on/off]` | Toggle metadata footer | Shows model, tool counts, timing |
| `/busy [queue/steer/interrupt]` | Enter behavior (CLI) | `/busy queue` |
| `/indicator [kaomoji/emoji/...]` | Busy indicator style | `/indicator kaomoji` |

### Tools & Skills

| Command | Description |
|---------|-------------|
| `/tools [list/disable/enable]` | Manage tools |
| `/toolsets` | List available toolsets |
| `/browser [connect/disconnect/status]` | Manage CDP browser connection |
| `/skills` | Search/install/inspect skills |
| `/bundles` | List configured skill bundles |
| `/cron` | Manage scheduled tasks |
| `/curator` | Background skill maintenance |
| `/kanban <action>` | Multi-profile collaboration board |
| `/reload-mcp` | Reload MCP servers |
| `/reload-skills` | Re-scan skills directory |
| `/reload` | Reload .env variables |
| `/plugins` | List plugins |

### Gateway (Messaging)

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Confirm gateway is reachable | First contact |
| `/sethome` | Set current chat as home channel | |
| `/restart` | Restart gateway | After config changes |
| `/approve [session/always]` | Approve dangerous command | `/approve session` |
| `/deny` | Reject dangerous command | |
| `/update` | Update Hermes | |
| `/topic [off/help/id]` | Telegram DM multi-session | `/topic` |
| `/platforms` (alias: `/gateway`) | Platform connection status | |
| `/platform <list/pause/resume>` | Operate gateway platform | `/platform resume telegram` |
| `/commands [page]` | Browse all commands | `/commands 2` |

### Info

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/usage` | Token usage + cost breakdown + account limits |
| `/insights [days]` | Usage analytics (default: 30 days) |
| `/paste` | Attach clipboard image |
| `/copy [N]` | Copy last assistant response to clipboard |
| `/image <path>` | Attach local image file |
| `/debug` | Upload debug report + get shareable links |
| `/profile` | Show active profile |
| `/gquota` | Google Gemini quota usage |

### Exit

| Command | Description |
|---------|-------------|
| `/quit` (also `/exit`, `/q`) | Exit CLI |

### Dynamic / Skill Commands

Every installed skill becomes a slash command automatically:

```bash
/<skill-name>        # Load any skill on demand
```

**Examples:**
```text
/gif-search           # Search and send GIFs
/github-pr-workflow   # Create/merge PRs
/excalidraw           # Create hand-drawn diagrams
/plan                 # Open plan mode (writes .hermes/plans/*.md)
/obsidian             # Read/write Obsidian vault notes
/systematic-debugging # Debug with 4-phase root cause approach
/test-driven-development  # RED-GREEN-REFACTOR cycle
```

---

## 3. Quick Commands (Custom)

Define your own shortcuts in `~/.hermes/config.yaml`:

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-gateway
  deploy:
    type: exec
    command: cd ~/myapp && git pull && docker compose up -d
  inbox:
    type: alias
    target: /gmail unread
  weather:
    type: exec
    command: curl wttr.in/Zurich?format=3
```

Then just type: `/status`, `/deploy`, `/inbox`, `/weather`

---

## 4. Model Aliases

Define short names for models you use often in `~/.hermes/config.yaml`:

```yaml
model_aliases:
  fav:
    model: claude-sonnet-4
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
  fast:
    model: deepseek/deepseek-v4-flash
    provider: openrouter
  local:
    model: qwen3-coder:30b
    provider: custom
    base_url: http://localhost:11434/v1
```

Or set from the shell:
```bash
hermes config set model.aliases.fav anthropic/claude-opus-4
hermes config set model.aliases.grok x-ai/grok-4
```

Use in chat: `/model fav`, `/model grok`, `/model local --global`

---

## 5. Practical Workflows

### Development Workflow

```text
1. Start session with relevant skills:
   hermes -s systematic-debugging,test-driven-development

2. Set a persistent goal:
   /goal Implement user authentication with JWT

3. During work, steer mid-task:
   /steer Don't forget rate limiting middleware

4. Check token usage:
   /usage

5. Save progress and resume later:
   /title Auth-Module-Implementation
   /quit
   hermes -c Auth-Module  # Resume next day
```

### Daily Briefing Cron

```bash
hermes cron create "0 8 * * 1-5" \
  --name "daily-briefing" \
  --prompt "Summarize: 1) Last 10 GitHub commits in ~/work 2) Today's weather 3) 3 top priorities from my TODO" \
  --deliver telegram
```

### Multi-Agent Parallel Work

```bash
# Terminal 1: Backend agent (git worktree for isolation)
hermes -w -p backend

# Terminal 2: Frontend agent
hermes -w -p frontend

# Or via tmux spawning from Hermes itself
# See hermes-agent skill for full tmux multi-agent setup
```

### Debugging Session

```text
1. Load debugging skill:
   /skill systematic-debugging

2. Enable higher reasoning:
   /reasoning high

3. If agent goes wrong path:
   /undo

4. Steer mid-task:
   /steer Check the error logs in /var/log first

5. Retry with model switch:
   /model claude-sonnet-4
   /retry
```

### Gateway + Telegram Setup

```bash
# 1. Configure
hermes gateway setup

# 2. Start
hermes gateway run

# 3. In Telegram, set home channel:
/sethome

# 4. Now cron jobs deliver here automatically

# 5. Check status anytime:
/platforms
```

---

## 6. Platform Compatibility Matrix

| Command | CLI | TUI | Messaging (Telegram/Discord etc.) |
|---------|:---:|:---:|:---:|
| `/new`, `/reset` | ✅ | ✅ | ✅ |
| `/retry`, `/undo` | ✅ | ✅ | ✅ |
| `/model` | ✅ | ✅ | ✅ |
| `/personality` | ✅ | ✅ | ✅ |
| `/reasoning` | ✅ | ✅ | ✅ |
| `/voice` | ✅ | ✅ | ✅ (Discord voice) |
| `/yolo` | ✅ | ✅ | ✅ |
| `/compress` | ✅ | ✅ | ✅ |
| `/rollback` | ✅ | ✅ | ✅ |
| `/background` | ✅ | ✅ | ✅ |
| `/queue`, `/steer` | ✅ | ✅ | ✅ |
| `/goal` | ✅ | ✅ | ✅ |
| `/status` | ✅ | ✅ | ✅ |
| `/debug` | ✅ | ✅ | ✅ |
| `/footer` | ✅ | ✅ | ✅ |
| `/curator` | ✅ | ✅ | ✅ |
| `/kanban` | ✅ | ✅ | ✅ |
| `/fast` | ✅ | ✅ | ✅ |
| `/sessions` | ✅ | ✅ TUI live | ❌ |
| `/tools`, `/toolsets` | ✅ | ✅ | ❌ |
| `/browser` | ✅ | ✅ | ❌ |
| `/skin`, `/statusbar` | ✅ | ✅ | ❌ |
| `/history`, `/save`, `/copy` | ✅ | ✅ | ❌ |
| `/paste`, `/image` | ✅ | ✅ | ❌ |
| `/plugins`, `/cron` | ✅ | ✅ | ❌ |
| `/handoff` | ✅ | ❌ | ❌ |
| `/sethome` | ❌ | ❌ | ✅ |
| `/approve`, `/deny` | ❌ | ❌ | ✅ |
| `/update`, `/restart` | ❌ | ❌ | ✅ |
| `/topic` | ❌ | ❌ | ✅ (Telegram) |
| `/commands` | ❌ | ❌ | ✅ |
| `/start` | ❌ | ❌ | ✅ |

---

## 7. Config Quick Reference

Key config sections you'll tweak most often:

```yaml
model:
  default: deepseek/deepseek-v4-flash
  provider: openrouter

agent:
  max_turns: 90
  tool_use_enforcement: true

terminal:
  backend: local      # local, docker, ssh, modal
  timeout: 180        # seconds

approvals:
  mode: smart         # manual, smart, off

compression:
  enabled: true
  threshold: 0.50    # compress when context is 50% full
  target_ratio: 0.20

display:
  skin: default
  tool_progress: new
  show_reasoning: false
  show_cost: true

memory:
  memory_enabled: true
  user_profile_enabled: true

security:
  redact_secrets: true

delegation:
  model: deepseek/deepseek-v4-flash
  max_iterations: 50

checkpoints:
  enabled: true
  max_snapshots: 50
```

Edit with: `hermes config edit` or `hermes config set <section.key> <value>`

---

## 8. Key Paths

```
~/.hermes/config.yaml              Main configuration
~/.hermes/.env                     API keys and secrets
~/.hermes/skills/                  Installed skills
~/.hermes/sessions/                Session transcripts
~/.hermes/state.db                 Canonical session store (SQLite + FTS5)
~/.hermes/logs/gateway.log         Gateway logs
~/.hermes/auth.json                OAuth tokens and credential pools
~/.hermes/gateway-config.yaml      Gateway/messaging config
~/.hermes/profiles/<name>/         Profile-specific config
~/.hermes/hermes-agent/            Source code (if git-installed)
```

---

## Resources

- **Docs:** https://hermes-agent.nousresearch.com/docs/
- **Slash Commands (official):** https://hermes-agent.nousresearch.com/docs/reference/slash-commands
- **CLI Commands (official):** https://hermes-agent.nousresearch.com/docs/reference/cli-commands
- **Config Reference:** https://hermes-agent.nousresearch.com/docs/user-guide/configuration
- **GitHub:** https://github.com/NousResearch/hermes-agent
- **Discord:** https://discord.gg/nousresearch
