---
title: systemd service clone
description: clone ssh service into independent clone
published: true
date: 2026-10-26T14:12:04.377Z
tags: ssh, systemd
editor: markdown
dateCreated: 2026-02-15T07:10:38.445Z
---

HowTo build a second sshd service for restricted sftp file transfer, independing of existing sshd service

## Create Files

```
# service overview
rpm -ql openssh-server

# copy config files
cp -va /usr/lib/systemd/system/sshd.service /etc/systemd/system/sftpd.service
cp -av /etc/sysconfig/sshd /etc/sysconfig/sftpd
cp -av /etc/ssh/sshd_config /etc/ssh/sftpd_config
```

## Modify configs for your needs

* `vi /etc/systemd/system/sftpd.service`
```
[Unit]
Description=OpenSSH SFTP server daemon
After=network.target sshd-keygen.target
Wants=sshd-keygen.target

[Service]
Type=notify
EnvironmentFile=-/etc/crypto-policies/back-ends/opensshserver.config
EnvironmentFile=-/etc/sysconfig/sftpd
ExecStart=/usr/sbin/sshd -D $OPTIONS $CRYPTO_POLICY
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
RestartSec=42s

[Install]
WantedBy=multi-user.target
```

*  `vim /etc/sysconfig/sftpd`
```
# Configuration file for the sftpd service.
SSH_USE_STRONG_RNG=0
OPTIONS="-f /etc/ssh/sftpd_config"
```

* `vim /etc/ssh/sftpd_config`
```
Port 222
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
SyslogFacility AUTHPRIV
LoginGraceTime 30m
PermitRootLogin no
MaxAuthTries 3
AuthorizedKeysFile	/dev/null
PermitEmptyPasswords no
PasswordAuthentication yes
ChallengeResponseAuthentication no
GSSAPIAuthentication yes
GSSAPICleanupCredentials no
UsePAM yes
AllowAgentForwarding no
AllowTcpForwarding no
GatewayPorts no
X11Forwarding no
PermitTTY no
PrintMotd no
PrintLastLog no
TCPKeepAlive yes
UseDNS no
AcceptEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES
AcceptEnv LC_IDENTIFICATION LC_ALL LANGUAGE
Subsystem	sftp	/usr/libexec/openssh/sftp-server
AllowUsers ftp1 ftp2
```

## Start and test

```bash
systemctl daemon-reload
systemctl restart sftpd
systemctl status sftpd

lsof -i -P -n

[xxx]# ssh -p222 localhost
root@localhost's password: 
```
