---
title: tftpd setup
description: Setup tftpd on Rocky9
published: true
date: 2026-10-26T14:11:43.023Z
tags: howto, setup, tftpd, rocky9
editor: markdown
dateCreated: 2026-02-13T09:07:19.793Z
---

## TFTP Server Setup with systemd Sockets

It's always a pain to search through config. 
This works with systemd sockets, which is the way you should go.

**Check SELinux status:**
```bash
getenforce
# Enforcing
```

**List installed FTP-related packages:**
```bash
rpm -qa | grep ftp
# vsftpd-3.0.5-5.el9.x86_64
# lftp-4.9.2-4.el9.x86_64
# ftp-0.17-89.el9.x86_64
```

**Search for TFTP packages:**
```bash
dnf search tftp
# tftp.x86_64 : The client for the Trivial File Transfer Protocol (TFTP)
# erlang-tftp.x86_64 : TFTP client
# syslinux-tftpboot.noarch : SYSLINUX modules in /tftpboot, available for network booting
# tftp-server.x86_64 : The server for the Trivial File Transfer Protocol (TFTP)
```

**Install TFTP and TFTP server:**
```bash
dnf install tftp tftp-server
# ...output omitted...
# Installed:
#   tftp-5.2-38.el9.x86_64
#   tftp-server-5.2-38.el9.x86_64
```

**Open TFTP service in firewall and restart firewalld:**
```bash
firewall-cmd --permanent --add-service tftp
systemctl restart firewalld
```

**Check TFTP service status:**
```bash
systemctl status tftp
# ● tftp.service - Tftp Server
#      Loaded: loaded (/usr/lib/systemd/system/tftp.service; indirect; preset: disabled)
#      Active: active (running) since Mon 2024-10-14 09:51:41 CEST; 2min 23s ago
# TriggeredBy: ● tftp.socket
#        Docs: man:in.tftpd
#    Main PID: 632778 (in.tftpd)
#       Tasks: 1 (limit: 23173)
#      Memory: 176.0K
#         CPU: 14ms
#      CGroup: /system.slice/tftp.service
#              └─632778 /usr/sbin/in.tftpd -s /var/lib/tftpboot
# Oct 14 09:51:41 srv-tftp-01.mybuehl.local systemd[1]: Started Tftp Server.
```

**Allow anonymous write for TFTP:**
```bash
setsebool -P tftp_anon_write 1
```

**Check and modify TFTP ExecStart for blocksize option:**
```bash
grep -- -s /etc/systemd/system/tftp.service
# ExecStart=/usr/sbin/in.tftpd -s /var/lib/tftpboot

sed -i 's/-s /-c -s /' /etc/systemd/system/tftp.service

grep -- -s /etc/systemd/system/tftp.service
# ExecStart=/usr/sbin/in.tftpd -c -s /var/lib/tftpboot
```

**Reload systemd and restart TFTP:**
```bash
systemctl daemon-reload
systemctl restart tftp
```

**Test TFTP upload:**
```bash
tftp localhost -c put ./date
ll /var/lib/tftpboot/
# total 0
# -rw-rw-rw-. 1 nobody nobody 0 Oct 14 10:17 date
```

