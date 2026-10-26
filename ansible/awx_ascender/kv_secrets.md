---
title: AWX Key-Value secrets
description: AWX/Ascender key-value secret howto
published: true
date: 2026-10-26T14:12:15.902Z
tags: ansible, awx, ascender, secrets
editor: markdown
dateCreated: 2026-02-15T08:01:27.851Z
---

* Version: awx 20.0.1  
HowTo store key-value secrets in awx and pass them to the playbooks
* **The current code/development of AWX is kept back by IBM/RedHat in order to get the "Ansible Automation Platform" selled.
  This is a shame for whole Open Source Comunit that is working on ansible in free time. Shame on you! Chris**

# AWX Configuration

## Credential Type

* AWX > Administration > Credential Types > Add
  * Name: kv
  * Input configuration: YAML

```
fields:
  - id: username
    type: string
    label: Username
  - id: password
    type: string
    label: Password
    secret: true
required:
  - username
  - password
```

  * Injector configuration: YAML

```
extra_vars:
  KV_PASSWORD: '{{ password }}'
  KV_USERNAME: '{{ username }}'
```

## Create Test Credential

* AWX > Resources > Credentials > Add
  * Name: test-kv
  * Type: kv
  * Username: myuser
  * Password: mypass

## Create Demo Playbook

Create Project with Github Repo and load it into AWX

* AWX > Resources > Projects > Add
* Name: Bitbull Ops
* var_secret.yml

```
---
- hosts: linux.domain.local
  tasks:
  - name: debug vars
    debug:
      msg: "key1: {{ key1 }} --- value1: {{ value1 }}"
...
```

## Create Template Job

* AWX > Resources > Templates > Add > Job Template
  * Name: DEBUG Variables
  * Project: Bitbull Ops
  * Playbook: var_secret.yml
  * Credentials: "YOUR SSH CREDS" + "test-kv"
  * Variables: YAML

```
---
key1: "{{ KV_USERNAME }}"
value1: "{{ KV_PASSWORD }}"
```

### Run Playbook

Output example:

```
Enter passphrase for /runner/artifacts/228/ssh_key_data: 
Identity added: /runner/artifacts/228/ssh_key_data (xxxxx)

PLAY [linux.domain.local] **************************************************

TASK [Gathering Facts] *********************************************************
ok: [linux.domain.local]

TASK [debug vars] **************************************************************
ok: [linux.domain.local] => {
    "msg": "key1: myuser -- value1: mypass"
}

PLAY RECAP *********************************************************************
linux.domain.local     : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
