---
title: Setup Hardening
description: Hardened Setup of Nanobot on Rocky 10
published: true
date: 2026-10-26T14:13:14.269Z
tags: nanobot, rocky10
editor: markdown
dateCreated: 2026-03-23T06:23:01.505Z
---

# 🐈 Nanobot Setup Guide - Rocky Linux 10 Minimal

> WARNING: This document is KI Generated and needs a review

## 📋 Overview

This setup is optimized for **Rocky Linux 10 Minimal** and meets all security requirements.

## 📁 Directory Structure

```bash
/opt/nanobot/
├── etc/              # Configuration (read-only)
├── workspace/        # Working directory (writable)
├── spool/            # Cron, Logs, Media, History
│   ├── cron/
│   ├── logs/
│   ├── media/
│   └── history/
└── bin/              # Binary files
```

## 🔧 Installation

### 1. Create User

```bash
# Create user 'nanobot' (no shell for security)
useradd -r -s /sbin/nologin -m nanobot

# Create group
groupadd nanobot
usermod -aG nanobot root

# Create directory structure
mkdir -p /opt/nanobot/{etc,workspace,spool/{cron,logs,media,history},bin}
```

### 2. Set Permissions

```bash
# Main directory (only root:nanobot)
chown -R root:nanobot /opt/nanobot
chmod -R 750 /opt/nanobot

# Workspace (writable)
chmod -R u+rwX,g+rxX /opt/nanobot/workspace

# Spool (writable)
chmod -R u+rwX,g+rxX /opt/nanobot/spool

# Config (read-only)
chmod -R 440 /opt/nanobot/etc
```

### 3. Python & Dependencies

```bash
# Install UV (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Install nanobot
uv sync --frozen

# Create config
cat > /opt/nanobot/etc/config.json << 'EOF'
{
  "restrictToWorkspace": true,
  "tools.exec.enable": true,
  "allowFrom": ["xxx"]
}
EOF

# Config permissions
chmod 600 /opt/nanobot/etc/config.json
```

### 4. Systemd Service

```bash
cat > /etc/systemd/system/nanobot.service << 'EOF'
[Unit]
Description=Nanobot AI Agent
After=network.target

[Service]
Type=simple
User=nanobot
Group=nanobot
WorkingDirectory=/opt/nanobot/workspace
Environment="PATH=/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin"
Environment="PYTHONPATH=/opt/nanobot"
ExecStart=/opt/nanobot/.venv/bin/nanobot
Restart=on-failure
RestartSec=10
StandardOutput=append:/opt/nanobot/spool/logs/nanobot.log
StandardError=append:/opt/nanobot/spool/logs/nanobot-error.log

# Security settings
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
NoNewPrivileges=true
ReadOnlyPaths=/opt/nanobot/etc
ReadWritePaths=/opt/nanobot/workspace /opt/nanobot/spool

[Install]
WantedBy=multi-user.target
EOF

# Enable service
systemctl daemon-reload
systemctl enable nanobot
systemctl start nanobot
```

### 5. Configure Logging

```bash
# Logrotate for nanobot
cat > /etc/logrotate.d/nanobot << 'EOF'
/opt/nanobot/spool/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 640 root nanobot
    postrotate
        systemctl reload nanobot
    endscript
}
EOF
```

## 🔐 Security Checks

```bash
# Verify installation
echo "=== User ==="
id nanobot

echo "=== Directory permissions ==="
ls -la /opt/nanobot/

echo "=== Config permissions ==="
ls -la /opt/nanobot/etc/config.json

echo "=== Service status ==="
systemctl status nanobot

echo "=== Logs ==="
tail -f /opt/nanobot/spool/logs/nanobot.log
```

## 📊 Logging

Each tool call is logged:

```bash
# Adjust log level
echo 'LOG_LEVEL="INFO"' >> /opt/nanobot/etc/config.json

# Check logs
tail -f /opt/nanobot/spool/logs/nanobot.log
```

## 🛠️ Maintenance

### Stop/Start Service

```bash
systemctl stop nanobot
systemctl start nanobot
systemctl restart nanobot
```

### View Logs

```bash
journalctl -u nanobot -f
tail -f /opt/nanobot/spool/logs/nanobot.log
```

### Updates

```bash
# Update nanobot
cd /opt/nanobot/workspace
uv sync --upgrade

# Restart service
systemctl restart nanobot
```

## 🚀 Startup

```bash
# First run
systemctl start nanobot

# Check status
systemctl status nanobot

# View logs
journalctl -u nanobot -n 50
```

## 📝 Best Practices

1. **Regular updates**: `uv sync --upgrade`
2. **Check logs daily**: `journalctl -u nanobot`
3. **Verify permissions monthly**: `ls -la /opt/nanobot/`
4. **Backups**: regularly back up `/opt/nanobot/etc/`

## 🔍 Troubleshooting

### Service not starting?

```bash
# Check logs
journalctl -u nanobot -xe

# Check service file
systemctl cat nanobot

# Check permissions
id nanobot
ls -la /opt/nanobot/etc/config.json
```

### Invalid config?

```bash
# Validate syntax
cat /opt/nanobot/etc/config.json | python -m json.tool

# Reload
systemctl daemon-reload
systemctl restart nanobot
```

## 📞 Support

Questions or issues? Check the logs first:

* `/opt/nanobot/spool/logs/nanobot.log`
* `/opt/nanobot/spool/logs/nanobot-error.log`

---

**Created:** 2026-03-23
**For:** Rocky Linux 10 Minimal
**Status:** ✅ Production Ready
