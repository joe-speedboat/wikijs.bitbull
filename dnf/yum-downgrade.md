---
title: yum downgrade
description: Downgrade Example with yum
published: true
date: 2026-10-26T14:12:29.269Z
tags: yum, downgrade
editor: markdown
dateCreated: 2026-02-20T14:12:21.488Z
---

Sometimes things go wrong and you have to downgrade packages to an earlier state.<br>
Here I write down my notes how I have done it, so I can reuse it later again.<br>
Probably it helps you too.

# What and When
* Analysis
  * Can you reproduce the problem in QA?
  * Do you have a test plan?
  * Can you verify the desired state?
* Maintenance window?
  * Prevent user access
* Fallback plan?
  * DR Backup
  * Snapshot

# Verify the bug
* https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb/bffc70f9-b16a-453b-939a-0b6d3c9263af
* https://docs.gluster.org/en/latest/release-notes/6.0/
* https://bugs.centos.org/

```bash
[root@vglclu144 ~]# gluster snapshot list | tail
autosnap_GMT-2021.01.16-17.58.01
autosnap_GMT-2021.01.17-10.58.01
autosnap_GMT-2021.01.17-17.58.01
autosnap_GMT-2021.01.18-10.58.01
autosnap_GMT-2021.01.18-17.58.01
autosnap_GMT-2021.01.19-10.58.01
autosnap_GMT-2021.01.19-17.58.01
autosnap_GMT-2021.01.20-10.58.01
autosnap_GMT-2021.01.20-15.17.11
autosnap_GMT-2021.01.20-17.58.01

[root@vglclu144 ~]# df -hTP | grep -e glusterfs -e cifs
localhost:/ctdb                                        fuse.glusterfs  2.0G   89M  2.0G   5% /mnt/ctdb
localhost:/data                                        fuse.glusterfs  2.0T  659G  1.4T  33% /mnt/data
//localhost/CIFS-SHARE                                 cifs            2.0T  659G  1.4T  33% /mnt/samba1

[root@vglclu144 ~]# ls -l /mnt/samba1/.snaps/autosnap_GMT-2021.01.20-17.58.01/ /mnt/data/.snaps/autosnap_GMT-2021.01.20-17.58.01/
/mnt/data/.snaps/autosnap_GMT-2021.01.20-17.58.01/:
total 8
drwxrws---+ 15 root Sec1 4096 Jan 18 09:41 Sec1
drwxrws---+ 18 root SBIB 4096 Oct  7 08:00 Sec1_ProjContr

/mnt/samba1/.snaps/autosnap_GMT-2021.01.20-17.58.01/:
ls: reading directory /mnt/samba1/.snaps/autosnap_GMT-2021.01.20-17.58.01/: Is a directory
total 0
```

#Verify the previous working version and downgrade
In my case, I did just know that it was working before they upgraded.<br>
Samba 4.10 seems to have a bug that prevents the VSS Folder restore with Gluster 6.<br>
But I can not find anything about it in Community, it may be to early, I will create a bug report later on.
* https://access.redhat.com/solutions/3205571
* https://access.redhat.com/solutions/29617
```bash
yum history list --all | head

Loaded plugins: changelog, fastestmirror
ID     | Login user               | Date and time    | Action(s)      | Altered
-------------------------------------------------------------------------------
    38 | root <root>              | 2020-12-23 23:49 | I, O, U        |  271 EE
    37 | root <root>              | 2020-12-15 15:10 | Install        |    2   
    36 | root <root>              | 2020-12-15 14:35 | Install        |    1   
    35 | root <root>              | 2020-11-10 10:36 | Install        |    1   
    34 | root <root>              | 2020-09-22 20:02 | Install        |    1   


sed -i 's/enabled=0/enabled=1/' /etc/yum.repos.d/CentOS-Vault.repo
yum makecache

yum list samba --show-duplicates 

Installed Packages
samba.x86_64                4.9.1-10.el7_7                   @C7.7.1908-updates 
Available Packages
samba.x86_64                4.1.1-31.el7                     C7.0.1406-base     
samba.x86_64                4.1.1-33.el7_0                   C7.0.1406-updates  
samba.x86_64                4.1.1-35.el7_0                   C7.0.1406-updates  
samba.x86_64                4.1.1-37.el7_0                   C7.0.1406-updates  
samba.x86_64                4.1.1-38.el7_0                   C7.0.1406-updates  
samba.x86_64                4.1.12-21.el7_1                  C7.1.1503-base     
samba.x86_64                4.1.12-23.el7_1                  C7.1.1503-updates  
samba.x86_64                4.1.12-24.el7_1                  C7.1.1503-updates  
samba.x86_64                4.2.3-10.el7                     C7.2.1511-base     
samba.x86_64                4.2.3-11.el7_2                   C7.2.1511-updates  
samba.x86_64                4.2.3-12.el7_2                   C7.2.1511-updates  
samba.x86_64                4.2.10-6.el7_2                   C7.2.1511-updates  
samba.x86_64                4.2.10-6.2.el7_2                 C7.2.1511-updates  
samba.x86_64                4.2.10-7.el7_2                   C7.2.1511-updates  
samba.x86_64                4.4.4-9.el7                      C7.3.1611-base     
samba.x86_64                4.4.4-12.el7_3                   C7.3.1611-updates  
samba.x86_64                4.4.4-13.el7_3                   C7.3.1611-updates  
samba.x86_64                4.4.4-14.el7_3                   C7.3.1611-updates  
samba.x86_64                4.6.2-8.el7                      C7.4.1708-base     
samba.x86_64                4.6.2-10.el7_4                   C7.4.1708-updates  
samba.x86_64                4.6.2-11.el7_4                   C7.4.1708-updates  
samba.x86_64                4.6.2-12.el7_4                   C7.4.1708-updates  
samba.x86_64                4.7.1-6.el7                      C7.5.1804-base     
samba.x86_64                4.7.1-9.el7_5                    C7.5.1804-updates  
samba.x86_64                4.8.3-4.el7                      C7.6.1810-base     
samba.x86_64                4.8.3-4.el7.0.1                  C7.6.1810-fasttrack
samba.x86_64                4.8.3-6.el7_6                    C7.6.1810-updates  
samba.x86_64                4.9.1-6.el7                      C7.7.1908-base     
samba.x86_64                4.9.1-10.el7_7                   C7.7.1908-updates  
samba.x86_64                4.10.4-10.el7                    C7.8.2003-base     
samba.x86_64                4.10.4-11.el7_8                  C7.8.2003-updates  
samba.x86_64                4.10.16-5.el7                    base               
samba.x86_64                4.10.16-7.el7_9                  updates            
samba.x86_64                4.10.16-9.el7_9                  updates            

yum history info 38 | grep -e samba -e libwbclient -e 4.9.1-10.el7_7  | awk '{print $2}' | xargs echo yum downgrade

yum downgrade ctdb-4.9.1-10.el7_7.x86_64 libsmbclient-4.9.1-10.el7_7.x86_64 libwbclient-4.9.1-10.el7_7.x86_64 samba-4.9.1-10.el7_7.x86_64 samba-client-4.9.1-10.el7_7.x86_64 samba-client-libs-4.9.1-10.el7_7.x86_64 samba-common-4.9.1-10.el7_7.noarch samba-common-libs-4.9.1-10.el7_7.x86_64 samba-common-tools-4.9.1-10.el7_7.x86_64 samba-libs-4.9.1-10.el7_7.x86_64 samba-vfs-glusterfs-4.9.1-10.el7_7.x86_64

yum remove pyldb

sed -i 's/enabled=1/enabled=0/' /etc/yum.repos.d/CentOS-Vault.repo
yum makecache
```

# Lock the current state
An Upgrade would destroy all your work, so lets lock it down
* https://access.redhat.com/solutions/98873
```bash
yum install yum-plugin-versionlock

yum versionlock ctdb-4.9.1-10.el7_7.x86_64 libsmbclient-4.9.1-10.el7_7.x86_64 libwbclient-4.9.1-10.el7_7.x86_64 samba-4.9.1-10.el7_7.x86_64 samba-client-4.9.1-10.el7_7.x86_64 samba-client-libs-4.9.1-10.el7_7.x86_64 samba-common-4.9.1-10.el7_7.noarch samba-common-libs-4.9.1-10.el7_7.x86_64 samba-common-tools-4.9.1-10.el7_7.x86_64 samba-libs-4.9.1-10.el7_7.x86_64 samba-vfs-glusterfs-4.9.1-10.el7_7.x86_64

Loaded plugins: changelog, fastestmirror, versionlock
Adding versionlock on: 0:samba-common-tools-4.9.1-10.el7_7
Adding versionlock on: 0:samba-common-4.9.1-10.el7_7
Adding versionlock on: 0:samba-libs-4.9.1-10.el7_7
Adding versionlock on: 0:libwbclient-4.9.1-10.el7_7
Adding versionlock on: 0:samba-client-libs-4.9.1-10.el7_7
Adding versionlock on: 0:ctdb-4.9.1-10.el7_7
Adding versionlock on: 0:samba-client-4.9.1-10.el7_7
Adding versionlock on: 0:samba-4.9.1-10.el7_7
Adding versionlock on: 0:samba-vfs-glusterfs-4.9.1-10.el7_7
Adding versionlock on: 0:samba-common-libs-4.9.1-10.el7_7
Adding versionlock on: 0:libsmbclient-4.9.1-10.el7_7


yum versionlock list

Loaded plugins: changelog, fastestmirror, versionlock
0:samba-common-tools-4.9.1-10.el7_7.*
0:samba-common-4.9.1-10.el7_7.*
0:samba-libs-4.9.1-10.el7_7.*
0:libwbclient-4.9.1-10.el7_7.*
0:samba-client-libs-4.9.1-10.el7_7.*
0:ctdb-4.9.1-10.el7_7.*
0:samba-client-4.9.1-10.el7_7.*
0:samba-4.9.1-10.el7_7.*
0:samba-vfs-glusterfs-4.9.1-10.el7_7.*
0:samba-common-libs-4.9.1-10.el7_7.*
0:libsmbclient-4.9.1-10.el7_7.*
versionlock list done


# yum versionlock clear # this can be used to release locks
```