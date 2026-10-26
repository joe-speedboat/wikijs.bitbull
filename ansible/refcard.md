---
title: Ansible Refcard
description: Ansible knowledge collection
published: true
date: 2026-10-26T14:12:14.361Z
tags: ansible
editor: markdown
dateCreated: 2026-02-15T07:55:43.917Z
---

# Ansible Navigator

| Ansible Command | Ansible Navigator Equivalent |
|-----------------|-----------------------------|
| **Inventory Commands** | |
| ansible-inventory -i inventory --list | ansible-navigator inventory -i inventory --list -m stdout |
| ansible-inventory -i inventory --graph | ansible-navigator inventory -i inventory --graph -m stdout |
| **Vault Commands (Mostly Local, Remain the Same)** | |
| ansible-vault create secret.yml | ansible-vault create secret.yml *(Remains the same)* |
| ansible-vault encrypt secret.yml | ansible-vault encrypt secret.yml *(Remains the same)* |
| ansible-vault decrypt secret.yml | ansible-vault decrypt secret.yml *(Remains the same)* |
| ansible-vault view secret.yml | ansible-vault view secret.yml *(Remains the same)* |
| **Playbook Commands** | |
| ansible-playbook playbook.yml | ansible-navigator run playbook.yml -m stdout |
| ansible-playbook -i inventory playbook.yml | ansible-navigator run -i inventory playbook.yml -m stdout |
| ansible-playbook -b playbook.yml | ansible-navigator run -b playbook.yml -m stdout |
| ansible-playbook -e "var=value" playbook.yml | ansible-navigator run -e "var=value" playbook.yml -m stdout |
| **Ad-Hoc Commands** | |
| ansible all -m ping | ansible-navigator exec "ansible all -m ping" -m stdout |
| ansible localhost -m setup | ansible-navigator exec "ansible localhost -m setup" -m stdout<br>ansible-navigator exec "ansible localhost -m setup -a filter=*ipv4* webserver" |
| ansible localhost -m setup | ansible-navigator exec "ansible localhost -m setup" -m stdout<br>ansible-navigator exec "ansible localhost -m setup -a filter=*ipv4* webserver" |
| ansible webservers -a "df -h" | ansible-navigator exec "ansible webservers -a 'df -h'" -m stdout |
| **Console Commands** | |
| ansible-console -b linux_servers | ansible-navigator exec "ansible-console -b linux_servers" -m stdout |
| **Configuration and Documentation** | |
| ansible-config dump | ansible-navigator config -m stdout |
| ansible-doc -l | ansible-navigator doc -l -m stdout |
| ansible-doc -s module_name | ansible-navigator doc module_name -m stdout |

## Aliases for ansible-playbook
```
alias nansible-playbook="ansible-navigator run -m stdout"

# Alias for ansible (Ad-Hoc Commands)
alias nansible="function _nansible() { ansible-navigator exec -m stdout \"ansible \$@\"; }; _nansible"

# Alias for ansible-inventory
alias nansible-inventory="ansible-navigator inventory -m stdout"

# Alias for ansible-config
alias nansible-config="ansible-navigator config -m stdout"

# Alias for ansible-doc
alias nansible-doc="ansible-navigator doc -m stdout"

# Alias for ansible-vault (Remains the same)
alias nansible-vault="ansible-vault"

# Alias for ansible-galaxy
alias nansible-galaxy="ansible-navigator galaxy -m stdout"

# Alias for ansible-test (if applicable)
alias nansible-test="ansible-navigator test -m stdout"
```

## Inventory

## Examples

* `vim /etc/ansible/inventory/hosts`

```
[apache]
web[01:05] ansible_user=devops

[nginx]
web[10:12]
web13 ansible_port=222 has_java = False
10.0.1.[250:253]

[nginx:vars]
http_port=8080

[webservers:children]
nginx
apache
```

### Dynamic Inventory Example

* `vim inventory/dynamic-inventory.sh`
```
#!/bin/bash
echo '{
   "web": ["www1", "www2", "www3"],
   "db": ["db1", "db2", "oracle1"]
}'
```
`chmod 700 inventory/dynamic-inventory.sh`

* `ls -l inventory/`
```
-rwxr-xr-x. 1 root root 94 Dec 14 15:01 dynamic-inventory.sh
-rw-r--r--. 1 root root 34 Dec 14 15:03 hosts
```

```
[root@ansible lab]# ansible -i inventory/ --list-hosts web
  hosts (3):
    www1
    www2
    www3
[root@ansible lab]# ansible -i inventory/ --list-hosts sudo
  hosts (1):
    vm20
```

### Commands

* query inventory for specific hosts  
  `ansible web01 --list-hosts`
  `ansible 'all:!kvm' -i /etc/ansible/hosts --list-hosts`
* show host involved by playbook  
  `ansible-playbook --list-hosts tests/qa.yml`
* run module on specific host  
  `ansible vm06 -m setup`

### cmd export/import
```bash
ansible-inventory --list --export --yaml > i.yaml  
ansible --list-hosts all -i i.yaml  
ansible -i i.yaml -m ping all
```

# Setup Ansible
## Container
Use the ansible-navigator as mentioned above
## Local setup
Install Ansible with latest LTS release into venv under `/opt`
This way, you can test new releases without touching current env.
But be aware, its not for newbies, its for Ansible Pros
```bash
curl -L ansible.bitbull.ch | bash
```