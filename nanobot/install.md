---
title: Install Nanobot
description: Install Nanobot on Rocky10 with some features
published: true
date: 2026-10-26T14:13:05.662Z
tags: nanobot, ai
editor: markdown
dateCreated: 2026-03-13T06:20:01.705Z
---

# Nanobot Installation
* https://wiki.bitbull.ch/en/blog/ai_assitants_explained
* https://github.com/HKUDS/nanobot

## Infrastructure
I have a DGX Spark running in my LAB, so I only configure with ollama.
If you use own providers, just look into project documentation.
Note that ollama api is not working properly, so I use vllm api for now.
There are some drawbacks, but it goes to far to explain that here.

#### Install Ollama on DGX Spark
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

* `systemctl edit ollama`
```
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAM_KEEP_ALIVE=1h"
```
* open firewall port
```bash
ufw enable 11434/tcp
```
* configure bot model
```bash
cd
mkdir models
cd models
```
* `vi Modelfile-bot-qwen3.5-9b`
```
FROM qwen3.5:9b
# higher can hold more context in conversations, but uses more memory on ollama
PARAMETER num_ctx 131072
# Stable Instruct Mode
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER top_k 40
PARAMETER min_p 0.05
# loop control
PARAMETER presence_penalty 0.2
PARAMETER repeat_penalty 1.1
# tokenlimit
# align with nanobot setting if lower or higher
PARAMETER num_predict 8192                                       
# deterministic runs
PARAMETER seed 42
```
* create new bot model
```bash
ollama create qwen3.5-9b-bot -f Modelfile-bot-qwen3.5-9b
ollama ls | grep bot
```

## Nanobot setup
* Setup  and initialize nanobot
```bash
dnf install tar git tree
useradd nanobot

# enable systemd userspace config for nanobot user
loginctl enable-linger nanobot

# I do not cover SELinux here
vi /etc/selinux/config
setenforce 0

# install uv and nanobot
su - nanobot
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install nanobot-ai
 
# create file structure and sample config
nanobot onboard
```

Setup basis config, read and replace values as needed
If you do not understand what to insert in values, read project doc first
`vi .nanobot/config.json`
```
  "agents": {
    "defaults": {
      "workspace": "~/.nanobot/workspace",
      "model": "qwen3.5-9b-bot:latest",
      "provider": "auto",
      "maxTokens": 8192,
      "temperature": 0.7,
      "maxToolIterations": 40,
      "memoryWindow": 100,
      "reasoningEffort": null
    }
...
  "tools": {
    "web": {
      "search": {
        "apiKey": "BS..replace..Dz",
        "maxResults": 5
      }
    },
...
    "vllm": {
      "apiKey": "dummy",
      "apiBase": "http://1.1.replace.1.1:11434/v1",
      "extraHeaders": null
    },
...
  "channels": {
    "sendProgress": true,
    "sendToolHints": false,
    "telegram": {
      "enabled": true,
      "token": "86104....replace...hCfgs",
      "allowFrom": ["2...replace...8"],
      "proxy": null,
      "replyToMessage": false
    },
```

* get aware of whats in there
```bash
[nanobot@nanobot ~]$ tree -L 3 ~/.nanobot
/home/nanobot/.nanobot
├── config.json
├── cron
│   └── jobs.json
├── media
└── workspace
    ├── AGENTS.md
    ├── HEARTBEAT.md
    ├── memory
    │   ├── HISTORY.md
    │   └── MEMORY.md
    ├── sessions
    │   ├── cli_direct.jsonl
    │   ├── cron_xxx.jsonl
    │   └── telegram_xxx.jsonl
    ├── skills
    ├── SOUL.md
    ├── TOOLS.md
    └── USER.md
```

* create systemd service in user space
```bash
mkdir ~/.config/systemd/user/ -p
```
* `vi ~/.config/systemd/user/nanobot-gateway.service`
```
[Unit]
Description=Nanobot Gateway
After=network.target
 
[Service]
Type=simple
ExecStart=%h/.local/bin/nanobot gateway
Restart=always
RestartSec=10
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=%h
 
[Install]
WantedBy=default.target
```

* activate service
```bash
[root@bob ~]# loginctl list-users
 UID USER    LINGER STATE    
   0 root    no     active
1000 nanobot yes    lingering

[root@bob ~]# su - bob

# if this is not present, lingering is not working
[bob@bob ~]# ls -ld /run/user/$(id -u myuser)

echo '
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=$XDG_RUNTIME_DIR/bus
' >> .bashrc

.  .bashrc

systemctl --user daemon-reload
systemctl --user enable --now nanobot-gateway
systemctl --user restart nanobot-gateway
```

## MCP Agent Setup
### Setup Docker
I do not want to compile on my "work horses" so I use docker to hook into my mcp agents
```bash
dnf install epel-release
dnf -y install dnf-plugins-core
dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
usermod -aG docker nanobot
mkdir /srv/docker
chown -R root:nanobot 750 /srv/docker
``` 

### Google Calendar
```bash
cd /srv/docker
git clone https://github.com/nspady/google-calendar-mcp.git
cd google-calendar-mcp
cp -av .env.example .env
 
# see here: https://github.com/nspady/google-calendar-mcp.git
cp /path/to/your/gcp-oauth.keys.json ./gcp-oauth.keys.json
chmod 644 ./gcp-oauth.keys.json
 
docker compose up -d
docker compose down
 
docker run --rm -it --mount type=bind,src=/srv/docker/google-calendar-mcp/gcp-oauth.keys.json,dst=/app/gcp-oauth.keys.json --mount type=volume,src=google-calendar-mcp_calendar-tokens,dst=/home/nodejs/.config/google-calendar-mcp google-calendar-mcp-calendar-mcp:latest npm run auth
# run link on any browser
# paste answer with curl on docker host, or within container if no access to network

docker ps
```
 
* `vi .nanobot/config.json`
```
"mcpServers": {
    "google-calendar": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--mount", "type=bind,src=/srv/docker/google-calendar-mcp/gcp-oauth.keys.json,dst=/app/gcp-oauth.keys.json",
        "--mount", "type=volume,src=google-calendar-mcp_calendar-tokens,dst=/home/nodejs/.config/google-calendar-mcp",
        "google-calendar-mcp-calendar-mcp:latest"
      ]
    }
  }
```
* reload nanobot config
```bash
systemctl --user restart nanobot-gateway
```

### Google Maps
* `vi .nanobot/config.json`                                                                     
```
    "google-maps": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "GOOGLE_MAPS_API_KEY=AI...Xqpg",
        "mcp/google-maps-comprehensive:latest"
      ]
    },
```
* reload nanobot config
```bash
systemctl --user restart nanobot-gateway
```
### Github
* `vi .nanobot/config.json`
```
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_PAT"
      }
    }
```
* reload nanobot config
```bash
systemctl --user restart nanobot-gateway
```

### Context7
* `vi .nanobot/config.json`
```
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "c...7",
        "Accept": "application/json, text/event-stream"
      }
    },
```
* reload nanobot config
```bash
systemctl --user restart nanobot-gateway
```

### DuckDuckGo
* `vi .nanobot/config.json`
```
     "duckduckgo": {
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "mcp/duckduckgo"
        ] 
      },
```
* reload nanobot config
```bash
systemctl --user restart nanobot-gateway
```

## Hardeing notes
Here you can restrict nanobot to only assess files withing its workspace
PathAppend is an applend to PATH, so you can put your tools under workspace
* `vi .nanobot/config.json`
```
  "tools": {
    "exec": {
      "timeout": 60,
      "pathAppend": "/home/nanobot/.nanobot/workspace/bin"
    },
    "restrictToWorkspace": true,
[...]
```

## Some Ideas of what you can do
```
If I tell you "remember that" then write it into `MEMORY.md` and show me what you 
changed for confirmation
```

```
Never change something in config.json unless I explicitly tell you. "remember that"
```

```
The code you made with is here: https://github.com/HKUDS/nanobot
So if I ask you about how you work, you can read this to understand and answer my quuestions
```

```
My Github account is `joe-speedboat` please look every day at 12:09 if I have any
- open issues
- pull requests
If yes, write me a telegram note, if no silently quit
```

```
"remember that" my calendars are:
- Work -> Relevant from Tuesday - Friday
- Private -> Relevant all the time
- Children -> Saturday - Monday
so if i ask you for free/busy information, follow this rules
```

