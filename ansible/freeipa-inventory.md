---
title: Ansible FreeIPA inventory
description: Ansible FreeIPA inventory setup
published: true
date: 2026-10-26T14:11:52.903Z
tags: ansible, rundeck, freeipa
editor: markdown
dateCreated: 2026-02-14T14:02:17.360Z
---

## FreeIPA Inventory
```bash
cd /etc/ansible
test -d inventory || exit #inventory must be dir

curl https://raw.githubusercontent.com/joe-speedboat/linux.scripts/master/ansible/ansible_dynamic_inventory_freeipa_with_vars.py > inventory/freeipa.py

chmod 700 inventory/freeipa.py
pip install python_freeipa

echo '# FreeIPA Ansible Inventory Auth
# FreeIPA Ansible Inventory Auth
export freeipaserver=freeipa01.domain.local
export freeipauser='svc_bind_rundeck_prod'
export freeipapassword='******'
' >> $HOME/.bashrc
```

