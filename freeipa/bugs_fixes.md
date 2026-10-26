---
title: Bugs & Fixes
description: FreeIPA/IDM Bugs and Solutions
published: true
date: 2026-10-26T14:12:53.786Z
tags: bugfix, freeipa
editor: markdown
dateCreated: 2026-02-24T07:19:28.650Z
---

# Fresh Install
## Replica Issues
### IPADNARangeCheck.no_dna_range_defined
* Error: `ipa-healthcheck --all --output-type human 2>&1 | grep -v -e SUCCESS:`
  >ipahealthcheck.ipa.dna.IPADNARangeCheck.no_dna_range_defined: No DNA range defined.
* Solution: create/delete user on new replica
```bash
[root@freeipa02 ~]# /usr/local/bin/ipa-health-check.sh
WARNING: ipahealthcheck.ipa.dna.IPADNARangeCheck.no_dna_range_defined: No DNA range defined. If no masters define a range then users and groups cannot be created.
RC=1

[root@freeipa02 ~]# kinit admin
Password for admin@DOMAIN.TLD:

[root@freeipa02 ~]# ipa user-add
First name: delete
Last name: me
User login [dme]:
----------------
Added user "dme"
----------------
  User login: dme
  First name: delete
  Last name: me
  Full name: delete me
  [...]
  
[root@freeipa02 ~]# /usr/local/bin/ipa-health-check.sh
RC=0

[root@freeipa02 ~]# cat /usr/local/bin/ipa-health-check.sh
#!/bin/bash
# Used by zabbix-agent2 to cover FreeIPA application status
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin
EXCLUDE_SOURCES='DSCERTLE0001: The certificate .Server-Cert. will expire in less than 30 days|WARNING: ipahealthcheck.ipa.certs.IPACertmongerExpirationCheck.* expires in 2[0-9] days|NSS DB /etc/pki/pki-tomcat/alias does not match entry in LDAP|WARNING: ipahealthcheck.ipa.idns.IPADNSSystemRecordsCheck.'
# fail if dnf or other ipa-healthcheck is currently running, which should not cause any long term status errors.
# reason is that ipa health checks can han when rpms get updated
for proc_name in rpm sos ipactl ipa-healthcheck
do
  pgrep -f $proc_name >/dev/null 2>&1
  if [ $? -eq 0 ]
  then
     echo "WARNING: $proc_name is running, check skipped"
     exit 1
  fi
done
STDOUT="$(ipa-healthcheck --all --output-type human 2>&1 | grep -v -e SUCCESS: | egrep -v "$EXCLUDE_SOURCES" | egrep '[a-zA-Z]')"
RC=$(echo "$STDOUT" | egrep '[a-zA-Z]' | wc -l)
echo "$STDOUT"
echo RC=$RC
exit $RC
```
