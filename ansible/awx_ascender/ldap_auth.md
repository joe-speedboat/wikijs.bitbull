---
title: Ascender LDAP Auth
description: awx & ascender ldap authentication wit FreeIPA
published: true
date: 2026-10-26T14:12:17.499Z
tags: ansible, freeipa, awx, ascender, ldap
editor: markdown
dateCreated: 2026-02-15T08:14:27.031Z
---

Just to not forget :-)

# AWX LDAP Auth with FreeIPA

## My Settings

* LDAP Server IP: `192.168.11.202`
* Bind User DN: `uid=ldap-bind,cn=users,cn=accounts,dc=domain,dc=tld`
* Admin Group DN: `cn=ansibleadmin,cn=groups,cn=accounts,dc=domain,dc=tld`

## HowTo Configure

* LDAP Server URI: `ldap://192.168.11.202:389`
* LDAP Bind DN: `uid=ldap-bind,cn=users,cn=accounts,dc=domain,dc=tld`
* LDAP Bind Password: `***`
* LDAP User DN Template: `uid=%(user)s,cn=users,cn=accounts,dc=domain,dc=tld`
* LDAP Group Type: `MemberDNGroupType`
* LDAP Require Group: `cn=ansibleadmin,cn=groups,cn=accounts,dc=domain,dc=tld`
* LDAP Deny Group: `Not configured`
* LDAP Start TLS: `Off`
Note, you can enable SSL, but then you must allow every cert or inject ca, which is not easy going
* https://docs.ansible.com/projects/awx/en/24.6.1/administration/ldap_auth.html
* https://stackoverflow.com/questions/53828320/awx-ansible-tower-ldap-authentication
* https://github.com/ansible/awx/issues/4267

* hint
```
-------------- LDAP AUTH HACKS ---------------------
https://ascener.fqdn.tld/api/v2/settings/ldap/
    "AUTH_LDAP_CONNECTION_OPTIONS": {
        "OPT_REFERRALS": 0,    
        "OPT_X_TLS_NEWCTX": 0, 
        "OPT_NETWORK_TIMEOUT": 30,
        "OPT_X_TLS_REQUIRE_CERT": 0
    },               
```


### LDAP Group Search

```
"dc=domain,dc=tld",
"SCOPE_SUBTREE",
"(objectClass=groupOfNames)"
```

### LDAP User Attribute Map

```
"first_name": "givenName",
"last_name": "sn",
"email": "mail"
```

### LDAP Group Type Parameters

```
{
  "name_attr": "cn",
  "member_attr": "member"
}
```

### LDAP User Flags By Group

```
{
  "is_superuser": [
    "cn=ansibleadmin,cn=groups,cn=accounts,dc=domain,dc=tld"
  ]
}
```
