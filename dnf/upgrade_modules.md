---
title: Upgrade PHP (modules)
description: How to upgrade PHP installed with dnf modules
published: true
date: 2026-10-26T14:13:10.606Z
tags: dnf
editor: markdown
dateCreated: 2026-03-18T11:52:56.210Z
---

# Upgrade PHP

## Goal

Upgrade the system-wide PHP version using the distribution’s module system.

This approach ensures:
- consistent dependency resolution
- full upgrade of all PHP-related packages
- reproducible and deterministic results

---

## Background: PHP Lifecycle

PHP follows a defined support lifecycle:

- **2 years active support** (bug fixes + security fixes)
- **2 years security-only support**
- then **End of Life (EOL)** (no fixes at all)

### Relevant versions (as of 2026)

| Version | Status | Security Support Until |
|--------|--------|------------------------|
| 8.2 | Security only | 31 Dec 2026 |
| 8.3 | Supported | 31 Dec 2027 |
| 8.4 | Supported | 31 Dec 2028 |
| 8.5 | Supported | 31 Dec 2029 |

👉 Once a version reaches EOL:
- no security patches
- no bug fixes
- running it in production is a security risk

---

## Check Current State

### Show installed PHP version
```bash
php -v
````

---

### List available module streams

```bash
dnf module list php
```

Typical output includes:

* multiple PHP versions as module streams
* one active stream marked with `[e]` (enabled)

---

## Upgrade Strategy

### Key principle

PHP upgrades must be performed via the **module system**, not via `dnf upgrade`.

Reason:

* modules define a **complete dependency set**
* mixing versions leads to inconsistent package states

---

## Upgrade Procedure

### 1. Reset current module

```bash
dnf module reset php -y
```

This removes the currently active PHP stream.

---

### 2. Enable target version

Example: switch to PHP 8.3

```bash
dnf module enable php:8.3 -y
```

This defines the target version for all PHP packages.

---

### 3. Synchronize packages

```bash
dnf distro-sync -y
```

This step is critical:

* upgrades all `php-*` packages
* replaces incompatible packages
* installs new dependencies
* removes obsolete packages

Typical effects:

* full migration of all extensions
* replacement of incompatible packages with newer variants

---

## Restart Services

```bash
systemctl restart php-fpm
systemctl restart nginx   # or httpd
```

---

## Validation

```bash
php -v
systemctl status php-fpm
```

---

## Important Notes

### Configuration files

During upgrade, `.rpmnew` files may appear:

* `/etc/php.ini.rpmnew`
* `/etc/php.d/*.rpmnew`

👉 These must be reviewed and merged if needed.

---

### Extensions

PHP extensions are upgraded automatically, but:

* major version changes can occur
* compatibility issues are possible

Check loaded modules:

```bash
php -m
```

---

### Dependency changes

New dependencies may be installed during upgrade.

👉 This is expected and part of the dependency resolution.

---

## Best Practices

### Before upgrade

* create backup or snapshot
* simulate upgrade:

```bash
dnf distro-sync --assumeno
```

---

### After upgrade

* verify services
* test applications
* review logs

---

## Recommendation

* **PHP 8.3** → stable default choice
* **PHP 8.4+** → for newer environments
* avoid staying on security-only versions long-term

---

## Quick Runbook

```bash
dnf module reset php -y
dnf module enable php:8.3 -y
dnf distro-sync -y
systemctl restart php-fpm
systemctl restart nginx
```

---

## Summary

Using the module system for PHP upgrades guarantees:

* consistent package versions
* full dependency alignment
* predictable system state

This is the recommended and reliable method for PHP upgrades on enterprise Linux systems.

