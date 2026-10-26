---
title: Prevent parallel exec
description: Prevent shell script to run twice at same time
published: true
date: 2026-10-26T14:13:08.922Z
tags: shell
editor: markdown
dateCreated: 2026-03-18T07:00:29.597Z
---

# Prevent Bash Script from Running Twice

**Purpose:**
Ensure that only **one instance of a script runs at a time** (mutual exclusion), preventing race conditions, duplicate work, or resource conflicts.

This pattern is commonly used for:

* cron jobs
* maintenance scripts
* backup/rotation tasks
* automation pipelines

---

## Implementation (flock-based locking)

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT="$(basename "$0")"
UID="$(id -u)"

# select lock dir
if [ "$UID" -eq 0 ]; then
    DIR="/run/lock/$SCRIPT"
    mkdir -p "$DIR" && chmod 0755 "$DIR"
else
    DIR="/tmp/$SCRIPT-$UID"
    mkdir -p "$DIR" && chmod 0700 "$DIR"
fi

# acquire lock
exec 200>"$DIR/lock"
flock -n 200 || {
    command -v logger >/dev/null 2>&1 \
        && logger -t "$SCRIPT" "already running" \
        || echo "$SCRIPT: already running" >&2
    exit 1
}

echo "$$" 1>&200
```

---

## How it works

* Uses **`flock` (kernel-level file locking)** on a file descriptor
* Lock is:

  * **atomic** → no race conditions
  * **process-bound** → released automatically on exit/crash
* No PID file validation required

---

## Lock location strategy

* **root user**

  * `/run/lock/<script>`
  * ephemeral (tmpfs), cleared on reboot
  * system-standard for runtime locks

* **non-root user**

  * `/tmp/<script>-<uid>`
  * per-user namespace prevents cross-user interference

---

## Why not PID lockfiles?

PID-based locking:

* vulnerable to race conditions
* affected by PID reuse
* requires manual cleanup
* susceptible to spoofing / symlink attacks

`flock` avoids all of these by delegating locking to the kernel.

---

## Behavior characteristics

* **Non-blocking (`-n`)**

  * script exits immediately if already running
* **Reboot-safe**

  * no stale locks (file descriptors vanish)
* **Crash-safe**

  * lock automatically released

---

## context

* This is a **mutual exclusion mechanism**, not a scheduler
* The lock file’s *existence is irrelevant* — only the lock state matters
* Safe to use in:

  * cron jobs
  * systemd services
  * parallel execution environments
* Not suitable for:

  * distributed locking across multiple hosts (use etcd/consul/DB instead)

---

## Minimal variant (for simple use cases)

```bash
exec 200>/tmp/$(basename "$0")-$(id -u).lock
flock -n 200 || exit 1
```

---

