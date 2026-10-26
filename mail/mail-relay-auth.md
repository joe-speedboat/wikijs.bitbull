---
title: Postfix mail relay with authentication
description: this is a sample config to enable mail sending for system mails or forward mails from mailserver by smtp-auth.
published: true
date: 2026-10-26T14:11:59.321Z
tags: postfix, smtp
editor: markdown
dateCreated: 2026-02-15T06:11:34.983Z
---

## SMTP AUTH
* `vi /etc/postfix/password`
```
#smtp.isp.com       username:password
smt`p.mydomain.com  send-user@mydomain.com:mySecretePassword
```
```bash
chown root:root /etc/postfix/password
chmod 0600 /etc/postfix/password
postmap hash:/etc/postfix/password
```

* `vi /etc/postfix/main.cf`
```
relayhost = smtp.mydomain.com:587
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/password
smtp_sasl_security_options =
```

```bash
systemctl restart postfix
```

## WITH TLS
```bash
dnf install cyrus-sasl cyrus-sasl-lib cyrus-sasl-plain
```

* `vi /etc/postfix/main.cf`
```
smtp_enforce_tls = yes
smtp_tls_security_level = encrypt
```
```bash
systemctl restart postfix
```

## CHANGE SYSTEM SENDER
* `vi /etc/postfix/main.cf`
```
sender_canonical_maps = regexp:/etc/postfix/canonical
```

* `vi /etc/postfix/canonical`
```
/^.*localhost.*/      send@mydomain.com
/^.*localdomain.*/    send@mydomain.com
```
