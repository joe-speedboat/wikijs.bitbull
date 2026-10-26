---
title: shell
description: shell hints
published: true
date: 2026-10-26T14:11:31.526Z
tags: cmd, helpers
editor: markdown
dateCreated: 2026-02-13T09:07:08.190Z
---

## count processes per user
```bash
ps hax -o user | sort | uniq -c
```

## Get the 10 biggest files/folders for the current directory
```bash
du -sm * .[^\.]* | sort -n | tail
```
