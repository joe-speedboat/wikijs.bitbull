---
title: OpenLDAP proxy
description: setup openldap proxy on Rocky 9
published: true
date: 2026-10-26T14:12:37.507Z
tags: proxy, ldap, openldap
editor: markdown
dateCreated: 2026-02-20T14:52:11.530Z
---

# General
OpenLDAP Proxy to present read only view to AD

* [https://www.zytrax.com/books/ldap/](https://www.zytrax.com/books/ldap/)

## Prerequisites
* Install AD Server
* Install Rocky9 minimal for LDAP Proxy

## Install OpenLDAP Proxy
```bash
dnf -y install epel-release 
dnf -y install openldap-servers openldap-clients ldapvi
```

## base configuration

## Configure Proxy
* /etc/sysconfig/slapd
```bash
# OpenLDAP server configuration
# see 'man slapd' for additional information

# Where the server will run (-h option)
# - ldapi:/// is required for on-the-fly configuration using client tools
#   (use SASL with EXTERNAL mechanism for authentication)
# - default: ldapi:/// ldap:///
# - example: ldapi:/// ldap://127.0.0.1/ ldap://10.0.0.1:1389/ ldaps:///
SLAPD_URLS="ldapi:/// ldap:/// ldaps:///"

# Any custom options
SLAPD_OPTIONS="-f/etc/openldap/slapd.conf"
```

```bash
cp -av /lib/systemd/system/slapd.service /etc/systemd/system/slapd.service
```

* /etc/systemd/system/slapd.service
```bash
[Unit]
Description=OpenLDAP Server Daemon
After=syslog.target network-online.target
Documentation=man:slapd
Documentation=man:slapd-config
Documentation=man:slapd-mdb
Documentation=file:///usr/share/doc/openldap-servers/guide.html

[Service]
Type=forking
ExecStartPre=/usr/libexec/openldap/check-config.sh
Environment="SLAPD_URLS=ldap:/// ldapi:///" "SLAPD_OPTIONS="
EnvironmentFile=/etc/sysconfig/slapd
ExecStart=/usr/sbin/slapd -u ldap -h ${SLAPD_URLS} ${SLAPD_OPTIONS}
LimitMEMLOCK=infinity
LimitNOFILE=20480

Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
Alias=openldap.service
```

* /etc/openldap/slapd.conf
```bash
### Schema includes ###########################################################
include                 /etc/openldap/schema/core.schema
include                 /etc/openldap/schema/cosine.schema
include                 /etc/openldap/schema/inetorgperson.schema
include                 /etc/openldap/schema/misc.schema
include                 /etc/openldap/schema/nis.schema

## Module paths ##############################################################
modulepath              /usr/lib64/openldap/
moduleload              back_ldap
moduleload              rwm

# Main settings ###############################################################
pidfile                 /var/run/openldap/slapd.pid
argsfile                /var/run/openldap/slapd.args

### Database definition (Proxy to AD) #########################################
disallow                bind_anon
database                ldap
readonly                yes
protocol-version        3
rebind-as-user

# Prod
uri                     "ldap://10.1.2.2:389"
uri                     "ldap://10.1.2.1:389"

TLSCertificateKeyFile   /etc/ssl/certs/domain.local/star.key
TLSCertificateFile      /etc/ssl/certs/domain.local/star.crt
TLSCACertificateFile    /etc/ssl/certs/domain.local/star-ca.crt


lastmod off
chase-referrals no
suffix                  "DC=DOMAIN,DC=LOCAL"

### Logging ###################################################################
# loglevel  trace
# loglevel  -1

### Access Rules ##############################################################
### "AD Proxy" can Read all, others can only auth (bind)
access to dn.subtree="DC=DOMAIN,DC=LOCAL"
       by dn.exact="CN=AD Proxy,CN=Users,DC=DOMAIN,DC=LOCAL" read
       by *          none

### Authenticated users can read in AD (rebind) but not write
# access                  to *
#                         by * read
```

```bash
restorecon -FRv /etc
firewall-cmd --add-port=636/tcp --permanent
systemctl restart firewalld
systemctl enable slapd
systemctl restart slapd
systemctl status slapd 
lsof -i -P -n
```

## Test Access
```bash
ldapvi -h localhost -b 'OU="DC=DOMAIN,DC=LOCAL' -D 'CN=AD Proxy,CN=Users,DC=DOMAIN,DC=LOCAL' -w xxxxxx '(&(cn=homer*))'
```