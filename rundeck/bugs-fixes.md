---
title: Bugs & Fixes
description: Known issues and solutions for Rundeck
published: true
date: 2026-10-26T14:11:51.170Z
tags: rundeck, bugfix
editor: markdown
dateCreated: 2026-02-14T13:58:24.019Z
---

# BUGS & FIXES

## Error Msg: `/bin/sh: /tmp/0-1-localhost-dispatch-script.tmp.sh: Permission denied`
```bash
echo '
# ----------------------------------------------------------------
# CUSTOM VALUES
# ----------------------------------------------------------------
framework.file-copy-destination-dir = ~/
' >> /etc/rundeck/framework.properties

systemctl restart rundeckd
```

## service.log not rotated
* Problem: /var/log/rundeck/service.log grows and get not rotated
```bash
cat << EOF > /etc/logrotate.d/rundeck_service
/var/log/rundeck/service.log {
 su root root
 copytruncate
 daily
 missingok
 rotate 7
 compress
 delaycompress
 notifempty
 create 640 root adm
}
EOF

logrotate -fv /etc/logrotate.d/rundeck_service
```

## pass on environment vars into playbook (rundeck & twilio issue)
```yaml
  - name: Load proxy variables from /etc/environment
    shell: |
      set -a
      source /etc/environment
      env | grep -i proxy
    register: proxy_env
    changed_when: false

  - name: Send user password via Twilio SMS
    environment: "{{ dict(proxy_env.stdout_lines | map('split','=',1) | list) }}"
    community.general.twilio:
      account_sid: "{{ twilio_account_sid }}"
      auth_token: "{{ twilio_auth_token }}"
      from_number: "{{ twilio_from_number }}"
      to_numbers:
        - "{{ ipa_user_phone | regex_replace('^00', '+') }}"
      msg: |
        ACME Access Infos
        
        Name: {{ ipa_user }}
        Givenname: {{ ipa_user_gn }}
        Surname: {{ ipa_user_sn }}
        E-Mail: {{ ipa_user_mail }}
        Password: {{ ipa_pass }}
        Expire: {{ ipa_user_expire_in_days }} Tage
        
        Self Service Portal: https://idm99.acme.com
      register: ipa_reset_password_cmd
```

## After reboot, WebUI hangs with message: "Authentication required"
This is an old issue, I never traced down and never red a lean explanation why it's happening
* https://github.com/rundeck/rundeck/issues/8785
```bash
$ mysql rundeck
MariaDB [rundeck]> update DATABASECHANGELOGLOCK set LOCKED = false where ID = 1;
Query OK, 1 row affected (0.002 sec)
Rows matched: 1  Changed: 1  Warnings: 0
```
