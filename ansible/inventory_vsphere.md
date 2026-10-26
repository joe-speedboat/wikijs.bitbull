---
title: vSphere Inventory
description: Ansible vSphere Inventory concept
published: true
date: 2026-10-26T14:12:57.102Z
tags: ansible, vsphere, inventory
editor: markdown
dateCreated: 2026-03-02T10:52:20.050Z
---

# Ansible Inventory with vSphere
* Inventory reference config
  https://github.com/joe-speedboat/linux.scripts/blob/master/ansible/inventory.vmware.yml

## Rundeck
The goal of this document is to provide an understanding of the possibilities and functionality of Rundeck and how Ansible got integrated.  
A RH294 (Ansible + RHCE) and practical experience with Rundeck are assumed as the basis for administration.

[Rundeck Website](https://www.rundeck.com/)  
[RH294 (Ansible + RHCE)](https://www.redhat.com/en/services/training/rh294-red-hat-linux-automation-with-ansible)

Rundeck is used to automate recurring tasks.  
This brings the following advantages:
-   Centralized management
-   WebUI with Active Directory authorization rules
-   Centralized scheduling for a better overview
-   Centralized error handling -\> eMail to Helpdesk -\> Zammad ticket
-   Centralized password management (Ansible Vault + Rundeck Vault)
-   Traceability of executed tasks (who, when, what, where)
-   Creating an autonomous and secure environment for the management of systems.

Honestly, creating jobs with Rundeck is very easy and pleasant.
However, administering Rundeck is not; it is complex and has many dependencies.
Rundeck should only be configured and maintained by someone who has experience and expertise.

### vCenter Inventory
* Inventory Script Config File: `rundeck@rundeck1:/etc/ansible/inventory/svvcenter1.vmware.yml`
  * Goals
    * Newly created VMs are discovered automatically
    * Without further definition, the VMs receive base configuration and updates
    * vSphere tags should make simple administration clear and efficient.
    * Excluded VMs are visible in the <code>ignore_tag</code> group
    * Systems temporarily in maintenance are visible in the <code>maintenance_tag</code> group
    * Groups can be composed from any vSphere objects

  * General
  <details>
  <summary><b>Powered-off</b> VMs and VMs with the names <b>*_lab</b>, <b>*-lab</b>, <b>lab_*</b>, <b>lab_*</b> are not displayed.</summary>
  <pre>
  filters:
  - runtime.powerState == "poweredOn"
  - not (
    config.name.lower().startswith('lab_') or
    config.name.lower().startswith('lab-') or
    config.name.lower().endswith('-lab') or
    config.name.lower().endswith('_lab')
  )
  </pre>
  </details>
    * Group definitions
    
  <details>
  <summary>The <b>name of the vCenter</b> in which the VM is located is additionally defined as a group</summary>
  <pre>
  svvcenter_NN: |
    not config.guestId.startswith('DoMatchAllOs')
  </pre></details>

  <details>
  <summary><b>Linux</b> systems are assigned based on the operating system detected by vSphere</summary>
  <pre>
  linux: |
    config.guestId.lower().startswith('alma') or
    config.guestId.lower().startswith('rocky') or
    config.guestId.lower().startswith('ubuntu') or
    config.guestId.lower().startswith('rhel')
    </pre></details>

  <details>
  <summary><b>Windows</b> systems are assigned based on the operating system detected by vSphere</summary>
  <pre>
  windows: |
    'windows' in config.guestId.lower()
  </pre></details>

  <details>
  <summary><b>no_update_tag</b> is a vSphere VM tag in the Ansible group<br>
  and is used to mark systems that are ignored by automatic patching.</summary>
  <pre>
  no_update_tag: |
    'no_update' in tag_category.Ansible
  </pre></details>

  <details>
  <summary><b>maintenance_tag</b> is a vSphere VM tag in the Ansible group<br>
  and is used to mark systems that are temporarily in maintenance.<br>
  This group is a member of the <code>ignore</code> group and is not used directly.
  </summary>
  <pre>
  maintenance_tag: |
    'maintenance' in tag_category.Ansible
  </pre></details>

  <details>
  <summary><b>ignore_tag</b> is a vSphere VM tag in the Ansible group<br>
  and is used to mark systems that should be permanently ignored.<br>
  This group is a member of the <code>ignore</code> group and is not used directly.
  </summary>
  <pre>
  ignore_tag: |
    'ignore' in tag_category.Ansible
  </pre></details>

  <details>
  <summary><b>ignore</b> is a meta group and is used to mark systems 
  that should be ignored by automation.
  </summary>
  <ul>
    <li>VMs which are <b>NOT</b> in the <b>Linux</b> or <b>Windows</b> group<li>
    <li>VMs which have the <b>ignore_tag</b> from vSphere<li>
    <li>VMs which have the <b>maintenance_tag</b> from vSphere<li>
    <li>VMs which have the name <b>svvprx-</b> (Veeam Proxies)<li>
  </ul>
  <pre>
  ignore: |              
    not ( config.guestId.lower().startswith('alma') or
    config.guestId.lower().startswith('rocky') or 
    config.guestId.lower().startswith('ubuntu') or
    config.guestId.lower().startswith('rhel') or
    'windows' in config.guestId.lower()) or
    config.name.lower().startswith('svvprx-') or
    'ignore' in tag_category.Ansible or
    'maintenance' in tag_category.Ansible
  </pre></details>

  <details>
  <summary><b>netscaler</b> VMs are assigned based on their name</summary>
  <pre>
  netscaler: |
    config.name.lower().startswith('svcns-')
  </pre></details>

  <details>
  <summary><b>ntp_server</b> VMs are assigned based on their name and are required to roll out the configuration of the NTP servers.</summary>
  <pre>
  ntp_server: |
    config.name.lower().startswith('svtime-')
  </pre></details>

  <details>
  <summary><b>probe</b> VMs are assigned based on their name and are required to roll out the configuration of the network probe servers.</summary>
  <pre>
  probe: |
    config.name.lower().startswith('svnprobe-')
  </pre></details>

  <details>
  <summary><b>prod</b> VMs are assigned based on their name, specifically when they do NOT match the pattern of test systems</summary>
  prod: |
    not ( config.name.lower().startswith('svt') or
         'test' in config.name.lower() )
  </pre></details>

  <details>
  <summary><b>test</b> VMs are assigned based on their name</summary>
  test: |
    config.name.lower().startswith('svt') or
    'test' in config.name.lower()
  </pre></details>

# Passwords

This section describes where passwords are stored and how they are
protected.

## Rundeck

Rundeck has a password vault. The passwords cannot be read by users,
but they can be referenced in jobs.

## Ansible Vault

Ansible Vault is a mechanism in which sensitive data can be stored in
encrypted files.  
When these encrypted files are used by Ansible, a password hidden at
runtime is used. This prevents the passwords from being exposed in a
backup.  
Therefore, this "Vault-Unlock Password" must be entered after every
startup.  
This is described in the Operations section.  
What Ansible Vault is and how it works is described [here
described](https://docs.ansible.com/ansible/latest/vault_guide/index.html),
the protected data is mainly stored here:  
`/etc/ansible/inventory/group_vars/`

# Operations

## Reboot

If the server is restarted, the Vault password must be entered via SSH:
```bash
ssh -l admin_XXXX svrundeck1.domain.tld
    sudo su -
        init-rundeck-and-ansible.sh
```
* More information about how this work is here
  https://github.com/joe-speedboat/linux.scripts/blob/master/ansible/vault-unlock.sh
  It is basically an unlock and a start of rundeck,nginx service
* `vim /usr/local/sbin/init-rundeck-and-ansible.sh`
```bash
#!/bin/bash
echo
echo Feed the ssh private key passphrase for rundeck
echo "Bitwarden > vault@rundeck1"
echo "Link to Secret"
echo "https://v.domain.tld/#/vault?itemId=blub"

sudo -u rundeck --login echo
echo
echo INFO: re/starting rundeck + nginx service
systemctl restart rundeckd nginx
echo
echo
echo All done
echo Now login to rundeck webUI:
echo .Test the inventory
echo .Test AdHoc command
```

After that, the "Ansible Vault" is unlocked and the Rundeck service is
started.  

After Unlocking, it is recomended to verify access to target nodes once
* cli as rundeck user
  `ansible -m ping all`