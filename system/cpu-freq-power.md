---
title: set cpu freq, depending on ac-state
description: Howto set cpu frequency of notebook depending on its AC-state
published: true
date: 2026-10-26T14:12:55.369Z
tags: cpu
editor: markdown
dateCreated: 2026-03-01T18:29:05.508Z
---

# Dynamically Capping CPU Frequency Based on AC / Battery State Using udev

This article documents a **clean, reliable, and distribution-agnostic** method to dynamically adjust CPU frequency limits based on whether a laptop is running on **AC power or battery**, using **udev** and **cpupower**.

The solution:
- Applies to **all CPUs**
- Works with **intel_pstate** and **amd_pstate**
- Reacts immediately to **plug / unplug events**
- Requires no cron jobs or systemd units
- Survives reboots and kernel upgrades

---

## Prerequisites

### 1. Ensure `cpupower` is available

On Debian/Ubuntu systems, the binary is typically provided by:

```bash
linux-tools-common
```

Verify:

```bash
which cpupower
cpupower --version
```

If missing:

```bash
apt install -y linux-tools-common
```

---

### 2. Verify CPU frequency driver (optional but recommended)

```bash
cpupower frequency-info | grep driver
```

Typical outputs:
- `intel_pstate`
- `amd_pstate`

This solution works correctly with both.

---

## The udev-Based Solution

The kernel exposes AC power state via:

```text
/sys/class/power_supply/*/online
```

- `online = 1` → AC connected
- `online = 0` → Running on battery

udev can react to these state changes.

---

## Create the udev Rule

Create the rule file:

```bash
vim /etc/udev/rules.d/99-cpu-power.rules
```

### Example policy

- **On AC power** → allow higher frequency (example: 3000 MHz)
- **On battery** → cap frequency to 2000 MHz
- Always use the `powersave` governor

```udev
SUBSYSTEM=="power_supply", ATTR{type}=="Mains", ATTR{online}=="1", RUN+="/usr/bin/cpupower frequency-set -g powersave -u 3000MHz"
SUBSYSTEM=="power_supply", ATTR{type}=="Mains", ATTR{online}=="0", RUN+="/usr/bin/cpupower frequency-set -g powersave -u 2000MHz"
```

Adjust the frequencies to match your hardware and thermal limits.

---

## Apply the Rule

Reload udev rules:

```bash
udevadm control --reload
```

Trigger the rule immediately (no reboot required):

```bash
udevadm trigger --subsystem-match=power_supply
```

---

## Verification

### 1. Check current limits

```bash
cpupower frequency-info
```

Look for:
- Governor: `powersave`
- Max frequency reflecting AC or battery state

---

### 2. Live test

1. Unplug AC power  
   ```bash
   cpupower frequency-info | grep "max frequency"
   ```
   Expected: `2.00 GHz`

2. Plug AC power back in  
   ```bash
   cpupower frequency-info | grep "max frequency"
   ```
   Expected: `3.00 GHz` (or your configured value)

---

## Why This Works Reliably

- udev reacts to **kernel power_supply events**
- `cpupower` uses **kernel-supported cpufreq interfaces**
- No polling, no timers, no race-prone startup logic
- Idempotent and fast execution

---

## Known Limitations (by design)

- udev runs commands asynchronously
- No logging unless explicitly redirected
- Desktop power managers (e.g. `power-profiles-daemon`) may override limits unless disabled

---

## Summary

| Aspect | Result |
|------|------|
| Dynamic AC/Battery switching | ✔ |
| Persistent across reboots | ✔ |
| Works with intel_pstate / amd_pstate | ✔ |
| No cron or systemd units | ✔ |
| Kernel-supported | ✔ |

This is one of the **simplest and most robust** ways to implement battery-aware CPU frequency control on Linux laptops.

---

**End of document**