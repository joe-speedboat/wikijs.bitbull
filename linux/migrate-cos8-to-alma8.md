---
title: Migrate COS8 to Alma8
description: Inplace migration of centos8
published: true
date: 2026-10-26T14:11:54.532Z
tags: linux, upgrade, centos, alma
editor: markdown
dateCreated: 2026-02-15T05:39:37.931Z
---

## Intro
In many forums I found the information, that the EOL of CentOS8 Stream needs a reinstall and can't get ugpraded or migrated into newer releases.
Since the repos have been removed, you need to switch to the vault repos to install any software in an old CentOS 8 Stream OS.

## Switch to Vault Repos
```bash
find /etc/yum.repos.d -type f -exec sed -i 's/mirrorlist=http:\/\/mirrorlist.centos.org/\#mirrorlist=http:\/\/mirrorlist.centos.org/g' {} \;
find /etc/yum.repos.d -type f -exec sed -i 's/\#baseurl=http:\/\/mirror.centos.org/baseurl=http:\/\/vault.centos.org/g' {} \;
dnf update -y
reboot
dnf swap centos-linux-repos centos-stream-repos -y
dnf update -y
```

## Upgrade to Rocky Linux 8
I migrated several Stream8 OS into Alma and never run into problems.
```bash
dnf install git -y
cd /tmp
git clone https://github.com/rocky-linux/rocky-tools.git
chmod +x /tmp/rocky-tools/migrate2rocky/migrate2rocky.sh
bash /tmp/rocky-tools/migrate2rocky/migrate2rocky.sh -r
reboot
```

## Links
* https://forums.centos.org/viewtopic.php?f=54&t=78708&sid=b90eb70d3585419896be85ab9ccce65f&start=20

