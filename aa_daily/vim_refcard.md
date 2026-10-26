---
title: vim refcard
description: All the Vim commands you need
published: true
date: 2026-10-26T14:12:50.281Z
tags: helpers, vim
editor: markdown
dateCreated: 2026-02-21T20:46:22.960Z
---

# Top used
| Command            | Description                              |
|--------------------|------------------------------------------|
| `:help<Enter>`     | help                                     |
| `<Esc>`            | back to normal mode                      |
| `V`                | visual line mode                         |
| `i`                | insert mode                              |
| `:`                | command-line mode                        |
| `:set tw=72`       | set text width to 72                     |
| `<F11>`            | paste mode                               |
| `<Esc>!!date`      | insert date                              |
| `qa`               | record keystrokes into register a        |
| `q`                | stop recording                           |
| `@a`               | execute keystrokes from register a       |
| `%s/from/to/g`     | replace string in whole file             |
| `<Esc>:wq!`        | force write and quit                     |
| `<Esc>:q!`         | force quit and dont write                |

# Vim Reference Card

## Modes
* `i`              insert before cursor  
* `I`              insert at beginning of line  
* `a`              append after cursor  
* `A`              append at end of line  
* `o`              open new line below  
* `O`              open new line above  
* `v`              visual mode (character)  
* `V`              visual line mode  
* `<Ctrl-v>`       visual block mode  
* `<Esc>`          back to normal mode  

## Movement
* `h` `j` `k` `l`  left / down / up / right  
* `w`              next word  
* `b`              previous word  
* `e`              end of word  
* `0`              beginning of line  
* `^`              first non-blank character  
* `$`              end of line  
* `gg`             beginning of file  
* `G`              end of file  
* `:n`             go to line n  
* `%`              jump to matching bracket  

## Editing
* `x`              delete character  
* `dd`             delete line  
* `yy`             yank (copy) line  
* `p`              paste after cursor  
* `P`              paste before cursor  
* `u`              undo  
* `<Ctrl-r>`       redo  
* `r`              replace single character  
* `cw`             change word  
* `cc`             change line  
* `>>`             indent line  
* `<<`             unindent line  
* `.`              repeat last command  

## Search & Replace
* `/text`          search forward  
* `?text`          search backward  
* `n`              next match  
* `N`              previous match  
* `:%s/old/new/g`  replace in whole file  
* `:%s/old/new/gc` replace with confirmation  

## Files
* `:w`             write file  
* `:q`             quit  
* `:wq`            write and quit  
* `:q!`            quit without saving  
* `:e file`        edit file  
* `:split file`    horizontal split  
* `:vsplit file`   vertical split  
* `<Ctrl-w> w`     switch window  

## Macros & Registers
* `qa`             record macro in register a  
* `q`              stop recording  
* `@a`             run macro a  
* `"ayy`           yank into register a  
* `"ap`            paste from register a  

## Useful Settings
* `:set number`        show line numbers  
* `:set relativenumber` show relative numbers  
* `:set expandtab`     use spaces instead of tabs  
* `:set tabstop=4`     tab width  
* `:set shiftwidth=4`  indent width  
* `:set ignorecase`    case-insensitive search  
* `:set smartcase`     smart case search  

## Hints
* Combine operators and motions:  
  * `d` + `w` → `dw` (delete word)  
  * `c` + `$` → `c$` (change to end of line)  
* Prefix with number to repeat:  
  * `5dd` delete 5 lines  
  * `3w`  move 3 words  
* Use `.` to repeat the last change  
* Learn to stay in normal mode as much as possible  