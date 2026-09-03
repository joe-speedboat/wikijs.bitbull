---
title: backup and disk
description: backup, disk, san
published: true
date: 2026-02-15T08:03:49.253Z
tags: cmd, helpers, backup, blockdevice
editor: markdown
dateCreated: 2026-02-13T09:07:01.425Z
---

## rescan scsi disk
This you need after vm disk expansion in runtime
rebooting is recommended at end of work for testing
```bash
for d in /sys/block/sd*/device/rescan ; do echo "scanning $d" ; echo 1 > $d ; done
```

## expand last partition in disk
```bash
lsblk
DISK=sdb
PART=1
parted /dev/$DISK resizepart $PART 100%
lsblk
```

## backup and restore mbr of a disk
* Backing up MBR stored on /dev/sdX
```bash
dd if=/dev/sdX of=/tmp/sda-mbr.bin bs=512 count=1
```

* Restore partition table to disk
```bash
dd if= sda-mbr.bin of=/dev/sdX bs=1 count=64 skip=446 seek=446
```

Restore partition table and boot loader
```bash
dd if= sda-mbr.bin of=/dev/sdX bs=512 count=1
```

## backup helper script
```bash
 echo '#!/bin/sh
 cp -av "$1" "$1.$(date +%Y%m%d%H%M%S)"
 ' > /usr/local/bin/backup
 chmod 755 /usr/local/bin/backup
```

## create sparse image files with dd
```bash
 dd if=/dev/zero of=guest.raw bs=1 count=0 seek=8G
```

## create random data fast
  50Gig of data with 5 threads
```bash
for i in {1..5} ; do ( openssl enc -aes-256-ctr -pass pass:"$(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64)" -nosalt < /dev/zero 2>&1 | dd of=/tmp/file_10G.$i bs=1M count=10k iflag=fullblock ) & done
```

## create 5 data generating threads which create infinite data files
```bash
for i in {1..5} ; do ( openssl enc -aes-256-ctr -pass pass:"$(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64)" -nosalt < /dev/zero 2>&1 | dd of=/tmp/file.$i) & done
 # stop data generation, started with command above
 pkill -9 -f dd
```

## ultra fast file copy of large file volumes
```bash
tar --ignore-failed-read -C $SRC_DATA/ -cf - . | mbuffer -L -s 256k -m 1G -P 85 | tar --ignore-failed-read -C $DST_DATA/ -xf -
```

## read HD smart status
```bash
smartctl -a /dev/sda
smartctl -H /dev/sda
```

## read udev disk attributes
read disk serial
```bash
udevadm info --query=all --name=/dev/sda | grep ID_SERIAL_SHORT | cut -d= -f2
```

## save and restore acl attributes
be careful, restore deleted my suid permissions :)
```bash
getfacl -R . >acl.txt
setfacl --restore acl.txt
getfacl -R $(ls -d /* | egrep -v 'dev|proc|selinux|sys|lost+') > /etc/acl.txt
```

## turn off auto hard disc boot scanning for extN and reduce root preserved space
```bash
tune2fs -c 0 -i 0 -m 0 /dev/VG0/data
```

## format Fat32 usb stick
```bash
DEV=/dev/sdX
umount ${DEV}* $DEV
dd if=/dev/zero of=$DEV bs=1M count=64
partprobe $DEV
parted $DEV --script -- mklabel msdos
parted $DEV --script -- mkpart primary fat32 1MiB 100%
mkfs.vfat -F32 ${DEV}1
```

## show extended superblock information of extN partition
```bash
debugfs -R stats /dev/VG0/root
```

## mark bad blocks on degrading hard disk with extN
```bash
umount /dev/sda1
e2fsck -cc /dev/sda1
```

