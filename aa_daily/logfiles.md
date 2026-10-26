---
title: logfiles
description: All about logfiles, journald, auditd
published: true
date: 2026-10-26T14:11:26.298Z
tags: cmd, helpers, logs, rh10
editor: markdown
dateCreated: 2026-02-13T09:07:04.845Z
---

## auditd logrotate generations
Tested on Rocky Linux 10
```bash
sed -i 's/max_log_file_action =.*/max_log_file_action = rotate/' /etc/audit/auditd.conf
sed -i 's/max_log_file =.*/max_log_file = 30/' /etc/audit/auditd.conf
pkill -9 -f /sbin/auditd
ps -ef | grep -i auditd
systemctl start auditd.service
systemctl status auditd.service
ls -la /var/log/audit/
```

## Make `less` behave like `tail -f`
```bash
less +F somelogfile
```

## trash a open logfile
```bash
cat /dev/null > logfile
echo -n > logfile
> logfile #bash
```

## View Recent Log Files
```bash
find /var/log -follow  -type f -mmin -1
tail -f /storage/log/vmware/applmgmt/monsvc.log | egrep --color=always -i '$|error|crit|warn'
lsof | egrep 'log$|out$' | awk '{print $10}' | sort -u | xargs tail -f | egrep --color=always -i '$|error|crit|warn'
lsof /var/log /storage/log | awk '{print $9}' | sort -u  | xargs tail -f | tee /tmp/all.log
journalctl -af
```

## Trash rsyslog Message Pattern

**/etc/rsyslog.d/mydomain.conf**
```bash
#auth,authpriv.* @syslog.mydomain.ch:1516

:msg, contains, "pam_unix(cron:session)" ~
:msg, contains, ": uid: missing" ~
*.* @syslog.mydomain.ch:1516
```

## Log Current Shell Session into File

```bash
script -a -f $HOME/console.log
```
