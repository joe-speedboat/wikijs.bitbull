---
title: tmux helpers
description: Most important tmux shortcuts
published: true
date: 2026-10-26T14:12:52.025Z
tags: helpers, tmux
editor: markdown
dateCreated: 2026-02-21T20:56:08.324Z
---

# tmux Cheat Sheet

## General

**C => CTRL**

### Concepts

| Term     | Description                          |
|----------|--------------------------------------|
| Session  | Think of it as a browser instance    |
| Window   | Think of it as a browser tab         |
| Pane     | Think of it as a pane in a tiled window |

# Command Line (Session Management)

| Command                     | Description              |
|-----------------------------|--------------------------|
| `tmux new -s name`          | Start new session        |
| `tmux ls`                   | List sessions            |
| `tmux kill-ses -t name`     | Kill session             |
| `tmux a -t name`            | Attach to session        |

# Sessions (Prefix: C+b)

| Shortcut        | Description        |
|----------------|--------------------|
| **C+b $**       | Rename session     |
| **C+b d**       | Detach session     |
| C+b )           | Next session       |
| C+b (           | Previous session   |

# Windows (Prefix: C+b)

| Shortcut        | Description                   |
|----------------|-------------------------------|
| **C+b c**       | Create new window             |
| C+b n           | Next window                   |
| C+b p           | Previous window               |
| C+b l           | Last used window              |
| C+b [0-9]       | Select window by number       |
| C+b '           | Select window by name         |
| C+b .           | Change window number          |
| **C+b ,**       | Rename window                 |
| **C+b F**       | Search windows                |
| C+b &           | Kill window                   |

# Panes (Prefix: C+b)

| Shortcut                | Description                    |
|-------------------------|--------------------------------|
| **C+b %**               | Vertical split                 |
| **C+b "**               | Horizontal split               |
| **C+b ->**              | Move pane right                |
| **C+b <-**              | Move pane left                 |
| **C+b "arrow up"**      | Move pane up                   |
| **C+b "arrow down"**    | Move pane down                 |
| C+b O                   | Next pane                      |
| C+b ;                   | Last active pane               |
| C+b }                   | Move pane right                |
| C+b {                   | Move pane left                 |
| **C+b !**               | Convert pane into window       |
| **C+b X**               | Kill pane                      |

# Copy Mode (vi)

| Key        | Description              |
|------------|--------------------------|
| C+b [      | Enter copy mode          |
| C+b ]      | Paste from buffer        |
| space      | Start selection          |
| enter      | Copy selection           |
| esc        | Clear selection          |
| g          | Go to top                |
| G          | Go to bottom             |
| h          | Move cursor left         |
| j          | Move cursor down         |
| k          | Move cursor up           |
| l          | Move cursor right        |
| /          | Search                   |
| #          | List paste buffers       |
| q          | Quit                     |