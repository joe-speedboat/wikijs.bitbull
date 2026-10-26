---
title: helpers
description: Useful commands with dnf/yum
published: true
date: 2026-10-26T14:12:07.730Z
tags: linux, dnf, rpm
editor: markdown
dateCreated: 2026-02-15T07:24:17.428Z
---

## DNF – Configure Fastest Mirror

### Overview

DNF supports automatic mirror selection using the `fastestmirror` option. When enabled, DNF prioritizes mirrors based on network connection latency.

Applicable to **DNF 4** on RHEL, Rocky Linux, AlmaLinux, and Fedora versions using DNF 4.

### Configuration

#### Option 1: Using DNF Config Manager

Enable fastest mirror selection permanently:

```bash
sudo dnf config-manager --save --setopt=fastestmirror=True
```

#### Option 2: Manual Configuration

Edit `/etc/dnf/dnf.conf`:

```ini
[main]
fastestmirror=True
max_parallel_downloads=10
```

| Parameter | Description |
|---|---|
| `fastestmirror=True` | Prioritize mirrors with the lowest connection latency |
| `max_parallel_downloads=10` | Allow up to 10 simultaneous package downloads |

### Apply Configuration

Refresh repository metadata:

```bash
sudo dnf clean metadata
sudo dnf makecache --refresh
```

### Verify Configuration

```bash
dnf config-manager --dump | grep -i fastestmirror
```

Expected output:

```text
fastestmirror = True
```

### Temporary Override

Enable fastest mirror selection for a single transaction:

```bash
sudo dnf --setopt=fastestmirror=True upgrade
```

### Notes

- `fastestmirror` selects mirrors based on connection latency, not actual download bandwidth.
- Repository metalink services may already provide an optimized mirror order.
- `max_parallel_downloads=10` allows multiple package downloads simultaneously.
- DNF 5 uses different `config-manager` syntax.


## find rpm depending on files
* what provides the manpage I need
```bash
dnf provides */tcp.7*
dnf provides *bin/mailx
```