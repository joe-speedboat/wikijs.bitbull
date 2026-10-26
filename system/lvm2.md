---
title: LVM2 Refcard
description: LVM2 Reference Card
published: true
date: 2026-10-26T14:12:45.277Z
tags: helpers, lvm
editor: markdown
dateCreated: 2026-02-21T20:09:40.680Z
---

# Install LVM Afterwards (RHEL 10)

```bash
# install
dnf install lvm2

# scan for existing volume groups
vgscan

# create partition (use modern device names like /dev/sdX or /dev/nvmeXn1)
fdisk /dev/sdX

# create physical volumes
pvcreate /dev/sdX3 /dev/sdY1

# create volume group
vgcreate -s 16M vg0 /dev/sdX3 /dev/sdY1

# create logical volume
lvcreate -L 4G -n lv_var vg0

# create filesystem (RHEL 10 default is XFS)
mkfs.xfs /dev/vg0/lv_var
```

---

# Extend Logical EXT Volumes (Online)

```bash
# extend logical volume by 800MB
lvextend -L +800M /dev/vg0/lv_var

# resize ext filesystem
resize2fs /dev/vg0/lv_var
```

---

# Extend Logical XFS Volumes (Online)

```bash
# extend logical volume by 800MB
lvextend -L +800M /dev/vg0/lv_var

# grow xfs filesystem (must be mounted)
xfs_growfs /mountpoint
```

---

# Shrink Logical EXT Volumes (Offline Only)

```bash
# shrinking only works unmounted
umount /dev/vg0/lv_var

# check filesystem
e2fsck -f /dev/vg0/lv_var

# shrink filesystem first
resize2fs /dev/vg0/lv_var 600M

# then shrink logical volume
lvreduce -L 600M /dev/vg0/lv_var
```

---

# Shrink Logical XFS Volumes

```bash
Not possible (XFS cannot be shrunk)
```

---

# Add Physical Volume to a Volume Group
```bash
# create partition type Linux LVM (8e) using fdisk
fdisk /dev/sdZ

# create physical volume
pvcreate /dev/sdZ1

# extend volume group
vgextend vg0 /dev/sdZ1

# check volume group
vgck vg0
```

---

# Remove Physical Volume from a Volume Group

```bash
# move data away from the physical volume
pvmove /dev/sdY1

# remove physical volume from volume group
vgreduce vg0 /dev/sdY1
```

---

# Create LVM Snapshots, Backup & Cleanup
```bash
# create snapshot
lvcreate -L 500M --snapshot -n snap_var /dev/vg0/lv_var

# mount snapshot
mkdir -p /mnt/snap_var
mount /dev/vg0/snap_var /mnt/snap_var

# backup data
tar vcfz /mnt/usbdisk/snap_var.tar.gz /mnt/snap_var/

# unmount snapshot
umount /mnt/snap_var

# remove snapshot
lvremove /dev/vg0/snap_var
```

Note: The snapshot only stores changed blocks since its creation.  
If more data changes than the snapshot size allows, the snapshot becomes invalid immediately.

---

# Extend LVM Physical Volume (Disk Extended in Virtualization)
```bash
disk=sda
part=3
vg=myvg
lv=tmp

# rescan SCSI bus
echo 1 > /sys/class/block/$disk/device/rescan

# reread partition table
partprobe -s

# show disk partitions
fdisk -l /dev/$disk

# list block devices
lsblk

# backup MBR (only for MBR partition tables)
dd if=/dev/$disk of=/root/$disk.mbr bs=512 count=1

LV=/dev/$vg/$lv

# resize partition to full disk
parted /dev/$disk resizepart $part 100%

# resize physical volume
pvresize /dev/${disk}${part}

# extend logical volume to all free space
lvextend -l +100%FREE /dev/$vg/$lv

# grow filesystem (choose the correct one)
xfs_growfs /$lv || resize2fs /dev/$vg/$lv

# verify
pvs
lvs
df -hP

# example: secure /tmp with noexec
sed -i "/$lv/s/defaults/defaults,noexec/" /etc/fstab

mount -o remount /var/tmp
mount -o remount /tmp
mount | grep tmp | grep exec

# test persistence
reboot
```

---

# Relevant Files and Commands

```bash
/etc/fstab
vgscan
pvcreate
vgcreate
lvcreate
mkfs.xfs
mkfs.ext4
lvextend
lvreduce
resize2fs
xfs_growfs
vgextend
vgreduce
pvmove
pvdisplay
vgdisplay
lvdisplay
pvs
vgs
lvs
```