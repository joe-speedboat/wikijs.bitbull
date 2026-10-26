---
title: Win Lin mixed inv
description: Rundeck mixed inventory for Linux and Windows hosts within same project
published: true
date: 2026-10-26T14:12:20.515Z
tags: ansible, rundeck, linux, windows
editor: markdown
dateCreated: 2026-02-15T08:20:35.432Z
---

# DESCRIPTION

Ansible integration in Rundeck is not that great, so there is still a need to run native bash and PowerShell jobs.

# PRE_REQ

* rundeck user must have working winrm setup:
  https://docs.ansible.com/projects/ansible/latest/os_guide/windows_winrm.html

* Linux and Windows hosts are joined to same AD
* Ansible installed and working as rundeck user
* Linux Inventory is working

```
ansible -m ping linux_all
```

* Windows Inventory is working
```
ansible -m win_ping windows_all
```

```
[rundeck@rundeck-02 ~]$ ansible-inventory --host gitea-01
{
    "ansible_become_password": "{{ ansible_password }}",
    "ansible_password": "xxxxxx",
    "ansible_port": 222,
    "ansible_user": "adm_ansible"
}

[rundeck@rundeck-02 ~]$ ansible-inventory --host xapp-01
{
    "ansible_become": false,
    "ansible_become_password": "{{ ansible_password }}",
    "ansible_connection": "winrm",
    "ansible_password": "xxxxxx",
    "ansible_port": 5985,
    "ansible_shell_type": "powershell",
    "ansible_user": "adm_ansible",
    "ansible_winrm_server_cert_validation": "ignore",
    "ansible_winrm_transport": "ntlm"
}
```

# RUNDECK CONFIG NOTES

```
PROJECT: Support
  Default Node Executor: ssh
    SSH Password Storage Path: keys/project/Support/AD/adm_ansible
    SSH Authentication: password
  Default File Copier: SCP
    SSH Password Storage Path: keys/project/Support/AD/adm_ansible
    SSH Authentication: password

  Nodes:
    1. Ansible Resource Model Source
      Ansible config file path: /etc/ansible/ansible.cfg
      Gather Facts: yes
      Ignore Host Discovery Errors: yes
      Limit Targets: linux*
      Additional host tag: ansible
      Import host vars: yes
      SSH Authentication: password
      SSH Timeout: 10
      Use become privilege escalation: yes

    2. Ansible Resource Model Source
      Ansible config file path: /etc/ansible/ansible.cfg
      Gather Facts: yes
      Ignore Host Discovery Errors: yes
      Limit Targets: windows*

    3. Local

    4. File
      Format: resourcexml
      File Path: /var/lib/rundeck/manual_nodes.xml
      Writeable: yes

      <?xml version="1.0" encoding="UTF-8"?>
      <project>
        <node name="srv-pgitea-01" hostname="gitea-01:222" username="adm_ansible"/>
      </project>

  Enhancers:
    1. Attribute Match
      Attribute: tags=~windows.*
      Attributes:
        winrm-authtype=ntlm
        winrm-user=adm_ansible
        winrm-password-storage-path=keys/project/Support/AD/adm_ansible
        winrm-port=5985
        winrm-protocol=http
        winrm-domain=domain.local
        node-executor=WinRMPython
        file-copier=WinRMcpPython
```

# TEST

Commands -> select all, run:

```
hostname
```
