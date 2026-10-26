---
title: kvm
description: Kernel-based Virtual Machine Infos
published: true
date: 2026-10-26T14:11:41.474Z
tags: howto, ksm, kvm, setup
editor: markdown
dateCreated: 2026-02-13T09:07:18.132Z
---

## enable nested virtualization
### For AMD CPUs
```bash
[root@clue2 ~]# cat /sys/module/kvm_amd/parameters/nested
0

[root@clue2 ~]# echo "options kvm-amd nested=1" >> /etc/modprobe.d/dist.conf

[root@clue2 ~]# rmmod kvm-amd

[root@clue2 ~]# modprobe kvm-amd

[root@clue2 ~]# modinfo kvm_amd | grep -i nested
parm:           nested:int

[root@clue2 ~]# cat /sys/module/kvm_amd/parameters/nested
1
```

```bash
[root@clue2 ~]# virsh edit ov-compute1
---modify---
<cpu mode='host-passthrough'/>
---------
[root@clue2 ~]# virsh start ov-compute1
```

### For Intel CPUs
```bash
clue1# cat /sys/module/kvm_intel/parameters/nested
N

clue1# rmmod kvm-intel
clue1# echo 'options kvm-intel nested=y' >> /etc/modprobe.d/dist.conf
clue1# modprobe kvm-intel

clue1# cat /sys/module/kvm_intel/parameters/nested
Y

clue1# modinfo kvm_intel | grep nested
parm:           nested:bool
```

```bash
clue1# virsh edit ov-compute1
---modify---
<cpu mode='host-passthrough'/>
---------
clue1# virsh start ov-compute1
```

## tuning
It is easy to enable kvm. However, the defaults are fairly conservative.

### howto enable
* `vi /etc/rc.local`

```bash
# ksm page merging, default 0
echo 1 > /sys/kernel/mm/ksm/run
# pages to scan on each run, default: 100
echo 1000 > /sys/kernel/mm/ksm/pages_to_scan
# time to sleep after each scan, default: 200
echo 20 > /sys/kernel/mm/ksm/sleep_millisecs
```
```bash
chmod +x /etc/rc.d/rc.local
```

### load tuning
```bash
free -t | grep ^Mem: | awk '{print $7/1024 " MB"}'
top # sort for cpu with "P" and look for ksmd
```

## enable vm serial console
How to configure serial console for KVM vm. So virsh will have access:
```bash
virsh console <vm-name>
```

### Red Hat
* https://access.redhat.com/articles/7212
#### RHEL9
```bash
grubby --update-kernel=ALL --args="console=tty0 console=ttyS0,115200"
```
#### RHEL8
```bash
grub2-editenv - set "$(grub2-editenv - list | grep kernelopts) console=tty0 console=ttyS0,115200"
```


### ubuntu
```bash
systemctl enable serial-getty@ttyS0.service
systemctl start serial-getty@ttyS0.service
```

### alpine
* Enabling a login console
This is done in `/etc/inittab`. There is commented entry for `ttyS0`. Just enable it.
```bash
# Put a getty on the serial port
ttyS0::respawn:/sbin/getty -L ttyS0 115200 vt100
```

* To start the getty, restart init:
```bash
kill -HUP 1
```

* Enabling two consoles during boot

It's possible to output to both the serial and vga console during the system boot.

```bash
append "quiet console=ttyS0,9600 console=tty0"
```

Not known how to do the same thing in the extlinux menu. 
You might find a starting point in this thread: http://patchwork.openembedded.org/patch/45175/

* Add your serial console to the trusted local terminal list
If you face the problem that the login prompt always refuses your password when you use serial console, you missed this entry.

Add this to the `/etc/securetty` file:   
```bash
ttyS0
```

## expand qcow2 disk online
Recently I needed to expand my nfs servers disk system while file operations where ongoing.   
So the easy and save way with `qemu-img resize` and final reboot of the VM was not possible.
Finally I found a way to resize the qcow2 disk of the vm online.

### Collect Information
#### Free Space
##### File Server VM
* CentOS8 Core
```bash
[root@nfs ~]# df -hP /srv/
Filesystem      Size  Used Avail Use% Mounted on
/dev/vdb        985G  707G  278G  72% /srv
```bash


### KVM Hypervisor
* CentOS7
```bash
[root@clue1 ~]# vmh -l nfs #my personal script, look at github if you like it
   ===---------- VM: nfs ----------===
           State: running
       Autostart: enable
          Memory: 1024 MB
             CPU: 2
      ---------- Network Interfaces:
      Interface  Type    Source  Model   MAC
      vnet6      bridge  br0     virtio  52:54:00:5d:c7:87
      ---------- Block Devices:
      Target  Source                        Size
      vda     /srv/vm/images/nfs.qcow2      7.0G  40G
      vdb     /srv/vm/images/nfs_srv.qcow2  973G  1.0T


[root@clue1 ~]# df -hP /srv
Filesystem           Size  Used Avail Use% Mounted on
/dev/mapper/raid-vm  2.8T  1.2T  1.5T  45% /srv

[root@clue1 ~]# qemu-img info -U /srv/vm/images/nfs_srv.qcow2
image: /srv/vm/images/nfs_srv.qcow2
file format: qcow2
virtual size: 1.0T (1073741824000 bytes)
disk size: 972G
cluster_size: 65536
Format specific information:
    compat: 1.1
    lazy refcounts: false
    refcount bits: 16
    corrupt: false
```

### Resize the qcow2 disk online
```bash
[root@clue1 ~]# virsh 
Welcome to virsh, the virtualization interactive terminal.

Type:  'help' for help with commands
       'quit' to quit

virsh # qemu-monitor-command nfs info block --hmp
drive-virtio-disk0 (#block185): /srv/vm/images/nfs.qcow2 (qcow2)
    Attached to:      /machine/peripheral/virtio-disk0/virtio-backend
    Cache mode:       writeback

drive-virtio-disk1 (#block360): /srv/vm/images/nfs_srv.qcow2 (qcow2)
    Attached to:      /machine/peripheral/virtio-disk1/virtio-backend
    Cache mode:       writeback

virsh # qemu-monitor-command nfs block_resize drive-virtio-disk1 1.5T --hmp

[root@clue1 ~]# qemu-img info -U /srv/vm/images/nfs_srv.qcow2
image: /srv/vm/images/nfs_srv.qcow2
file format: qcow2
virtual size: 1.5T (1649267441664 bytes)
disk size: 972G
cluster_size: 65536
Format specific information:
    compat: 1.1
    lazy refcounts: false
    refcount bits: 16
    corrupt: false
```

### Align the VM Disk size
```bash
[root@nfs ~]# df -hPT /srv/
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/vdb       ext4  985G  719G  266G  74% /srv

[root@nfs ~]# resize2fs /dev/vdb
resize2fs 1.45.4 (23-Sep-2019)
Filesystem at /dev/vdb is mounted on /srv; on-line resizing required
old_desc_blocks = 125, new_desc_blocks = 192
The filesystem on /dev/vdb is now 402653184 (4k) blocks long.

[root@nfs ~]# df -hPT /srv/
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/vdb       ext4  1.5T  720G  793G  48% /srv
```

### Links
* https://bugzilla.redhat.com/show_bug.cgi?id=648594
* https://serverfault.com/questions/324281/how-do-you-increase-a-kvm-guests-disk-space

## useful cmd
### fact
* get disks 
```bash
virsh domblklist $VM
```
* disk info
```bash
qemu-img info $VM_IDISK
```

* get ip adress of vm
```bash
virsh qemu-agent-command $VM '{"execute":"guest-network-get-interfaces"}' | python3 -mjson.tool | grep ip-address
```

### resize disk
* resize image
 qemu-img resize $VM_IDISK 100G

### convert disk
* Error: Cannot store dirty bitmaps in qcow2 v2 files
```bash
qemu-img convert -O qcow2 -o compat=1.1 old-image.qcow2 new-image.qcow2
```

### snapshot
* list snapshots with virsh
```bash
virsh snapshot-list $VM
```
* commit snapshot from online vm
```bash
virsh blockcommit $VM $VM_IDISK --active --pivot --verbose
```
* commit snapshot from powered-off vm
```bash
qemu-img commit $VM_DISK_DELTA_FILE
```
* delete snapshot meta data
```bash
virsh snapshot-delete $VM snap_name --metadata
```
* delete snapshot within qcow2 file
```bash
qemu-img snapshot -d $SNAP_NAME $VM_DISK
```