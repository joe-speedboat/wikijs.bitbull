---
title: firewalld Refcard
description: Firewalld Reference Card for RHEL10/Rocky10
published: true
date: 2026-10-26T14:12:46.949Z
tags: firewalld
editor: markdown
dateCreated: 2026-02-21T20:25:11.829Z
---

# firewalld Reference Card (RHEL 10)

Complete quick reference for daily and advanced administration.

## Install & Service Management

* Install:
```bash
dnf install firewalld
```

* Enable and start:
```bash
systemctl enable --now firewalld
```

* Check status:
```bash
systemctl status firewalld
```

* Check firewall state:
```bash
firewall-cmd --state
```

* Reload (keeps connections):
```bash
firewall-cmd --reload
```

* Restart (drops connections):
```bash
systemctl restart firewalld
```

## Runtime vs Permanent

* Temporary rule:
```bash
firewall-cmd --add-service=http
```

* Permanent rule:
```bash
firewall-cmd --add-service=http --permanent
```

* Apply permanent changes:
```bash
firewall-cmd --reload
```

## Zones

* List zones:
```bash
firewall-cmd --get-zones
```

* Get default zone:
```bash
firewall-cmd --get-default-zone
```

* Set default zone:
```bash
firewall-cmd --set-default-zone=public
```

* Show active zones:
```bash
firewall-cmd --get-active-zones
```

* Assign interface:
```bash
firewall-cmd --zone=internal --change-interface=eth1 --permanent
```

* Assign source network:
```bash
firewall-cmd --zone=trusted --add-source=192.168.10.0/24 --permanent
```

## Services
* List available services:
```bash
firewall-cmd --get-services
```

* List services in zone:
```bash
firewall-cmd --zone=public --list-services
```

* Add service:
```bash
firewall-cmd --zone=public --add-service=http --permanent
```

* Remove service:
```bash
firewall-cmd --zone=public --remove-service=http --permanent
```

## Ports

* Open TCP port:
```bash
firewall-cmd --zone=public --add-port=8080/tcp --permanent
```

* Open UDP port:
```bash
firewall-cmd --zone=public --add-port=53/udp --permanent
```

* Remove port:
```bash
firewall-cmd --zone=public --remove-port=8080/tcp --permanent
```

## Rich Rules

* Allow SSH from single IP:
```bash
firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source address="10.0.0.5" service name="ssh" accept'
```

* Block IP:
```bash
firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source address="1.2.3.4" drop'
```

* Log and drop:
```
firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source address="5.6.7.8" log prefix="FW-DROP " level="info" drop'
```

## Port Forwarding
* Forward port 80 → 8080:
```bash
firewall-cmd --permanent --zone=public --add-forward-port=port=80:proto=tcp:toport=8080:toaddr=192.168.1.10
```

## Masquerading (NAT)

* Enable masquerade:
```bash
firewall-cmd --zone=external --add-masquerade --permanent
```

* Enable IP forwarding:
```bash
sysctl -w net.ipv4.ip_forward=1
```

## IP Sets (Group IP Management)

* Create ipset:
```bash
firewall-cmd --permanent --new-ipset=blacklist --type=hash:ip
```

* Add IP to ipset:
```bash
firewall-cmd --permanent --ipset=blacklist --add-entry=1.2.3.4
```

* Use ipset in rule:
```bash
firewall-cmd --permanent --zone=public --add-rich-rule='rule source ipset="blacklist" drop'
```

* List ipsets:
```bash
firewall-cmd --get-ipsets
```

## Direct Rules (nftables level)

* Add direct drop rule:
```bash
firewall-cmd --permanent --direct --add-rule ipv4 filter INPUT 0 -s 10.10.10.10 -j DROP
```

* List direct rules:
```bash
firewall-cmd --direct --get-all-rules
```

## Lockdown Mode

* Enable lockdown:
```bash
firewall-cmd --lockdown-on
```
* Whitelist command:
```bash
firewall-cmd --permanent --add-lockdown-whitelist-command=/usr/bin/firewall-cmd
```

## ICMP Control

* List ICMP types:
```bash
firewall-cmd --get-icmptypes
```

* Block ping:
```bash
firewall-cmd --permanent --add-icmp-block=echo-request
```


## Custom Service File
* Create file:
```bash
vi /etc/firewalld/services/myapp.xml
```

* Example content:
```bash
<service>
  <short>MyApp</short>
  <description>Custom App</description>
  <port protocol="tcp" port="9000"/>
</service>
```

* Reload:
```bash
firewall-cmd --reload
```


## Offline Configuration

* Add service offline:
```bash
firewall-offline-cmd --add-service=http
```

* Add port offline:
```bash
firewall-offline-cmd --add-port=8443/tcp
```

## Debugging
* Log denied packets:
```bash
firewall-cmd --set-log-denied=all
```
* Show nft rules:
```bash
nft list ruleset
```
* View logs:
```bash
journalctl -xeu firewalld
```

## Reset Configuration
* Backup:
```bash
cp -r /etc/firewalld /root/firewalld.backup
```
* Reset:
```bash
rm -rf /etc/firewalld
```
* Restart:
```bash
systemctl restart firewalld
```

# Best Practices
- Use `--permanent` in production.
- Reload after changes.
- Prefer services over raw ports.
- Use ipsets for large IP groups.
- Use rich rules before direct rules.
- Backup `/etc/firewalld` before major changes.
