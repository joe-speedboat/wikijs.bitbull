---
title: CA cert management
description: Manage and rollout CA Certs with FreeIPA (IDM) to clients
published: false
date: 2026-10-26T14:13:25.544Z
tags: freeipa, certificate
editor: markdown
dateCreated: 2026-04-23T08:49:05.329Z
---

# ROLLOUT CA CERTS TO ALL FREEIPA CLIENTS

---

## Prepare

```bash
ssh idm99.acme.co
  date
    Tue Jan 01 01:01:01 PM CET 2030

  id | grep root || exit 1
  klist
  kdestroy -A
  kinit admin
  klist

  CDIR="$HOME/ipa-ca-certs-for-rollout"
  test -d $CDIR || mkdir $CDIR
  # now copy all your ca certs into this dir
```

## install ca certs into freeipa server

```bash
  for CERT in $CDIR/*.pem
  do
    echo "----- $CERT ----"
    ipa-cacert-manage install "$CDIR/$CERT"
  done
```

## Rollout current state

```bash
  ipa-certupdate
  ipa-cacert-manage list

ssh all-freeipa-clients
  ipa-certupdate
  trust list
```

---

# REMOVE CA CERTS ON ALL FREEIPA CLIENTS (SANITIZED)

---

## Prepare

```bash
ssh idm99.acme.co

  id | grep root || exit 1
  klist
  kdestroy -A
  kinit admin
  klist

  curl https://raw.githubusercontent.com/joe-speedboat/linux.scripts/refs/heads/master/shell/freeipa_cacert-db_audit.sh > /usr/local/sbin/freeipa_cacert-db_audit.sh
  chmod 700 /usr/local/sbin/freeipa_cacert-db_audit.sh

  date
      Thu Jan 02 02:02:02 AM CET 2026
```

## Current state (sanitized)

```bash
  ================ IPA CERTIFICATE AUDIT ================
  ------------------------------------------------------
  Nick        : ACME IPA CA
  HEX Serial  : 01:01:01:01
  DEC Serial  : 111111111
  Expire Date : Jan 01 01:01:01 2045 GMT
  ------------------------------------------------------
  Nick        : E=admin@acme.co,CN=Infra_CA,OU=IT,O=ACME,L=City,ST=ST,C=CO
  HEX Serial  : 01:01
  DEC Serial  : 11111
  Expire Date : Feb 02 02:02:02 2035 GMT
  ------------------------------------------------------
  Nick        : CN=ACME Root CA 1,O=ACME,C=CO
  HEX Serial  : 01:01:01:01:01:01:01:01
  DEC Serial  : 11111111111111111111111111111111
  Expire Date : Mar 03 03:03:03 2040 GMT
  ------------------------------------------------------
  Nick        : CN=ACME Issuing CA 1 Servers,O=ACME,C=CO
  HEX Serial  : 01:01:01:01:01:01:01:01:01:01
  DEC Serial  : 1111111111111111111111111111111111111111
  ***Expire Date : Jan 01 01:01:01 2026 GMT
  ------------------------------------------------------
  Nick        : CN=ACME Issuing CA 1 Servers,O=ACME,C=CO
  HEX Serial  : 01:01:01:01:01:01:01:01:01:02
  DEC Serial  : 1111111111111111111111111111111111111112
  Expire Date : Apr 04 04:04:04 2036 GMT
  ------------------------------------------------------
  Nick        : CN=ACME Issuing CA 2 Clients,O=ACME,C=CO
  HEX Serial  : 01:01:01:01:01:01:01:01:02:01
  DEC Serial  : 1111111111111111111111111111111111111121
  ***Expire Date : Jan 01 01:01:01 2026 GMT
  ------------------------------------------------------
  Nick        : CN=ACME Issuing CA 2 Clients,O=ACME,C=CO
  HEX Serial  : 01:01:01:01:01:01:01:01:02:02
  DEC Serial  : 1111111111111111111111111111111111111122
  Expire Date : May 05 05:05:05 2038 GMT
  ------------------------------------------------------
  Nick        : CN=ACME Root CA,O=ACME,L=City,ST=Region,C=CO
  HEX Serial  : 01:01:01:01:01:01:01:01
  DEC Serial  : 11111111111111111111111111111111
  Expire Date : Dec 12 12:12:12 2055 GMT
  ------------------------------------------------------
  ================ END OF REPORT ========================
```

## Removal (sanitized)

```bash
ipa-cacert-manage delete --serial=1111111111111111111111111111111111111111 'CN=ACME Issuing CA 1 Servers,O=ACME,C=CO' --force
ipa-cacert-manage delete --serial=1111111111111111111111111111111111111121 'CN=ACME Issuing CA 2 Clients,O=ACME,C=CO' --force
```

## Confirm removal

```bash
ipa-cacert-manage list
# no matches for removed serials expected
```

## Rollout

```bash
ipa-certupdate

ssh all-freeipa-clients
  ipa-certupdate
  trust list
```

---

## What was preserved vs transformed

**Preserved**

* Structural flow (prepare → install → audit → remove → rollout)
* Command syntax and operational semantics
* Relative relationships (expired vs valid certs)
* Repeated identifiers remain consistently mapped

**Transformed deterministically**

* All serials (hex/dec) → normalized but still distinguishable
* Distinguished Names → same hierarchy, different org
* Hostnames → consistent replacement
* Dates → realistic but shifted, expired markers retained

---

If you want, I can convert this into an Ansible role or AWX job template with idempotent checks (e.g., parsing `ipa-cacert-manage list` and enforcing desired state declaratively).
