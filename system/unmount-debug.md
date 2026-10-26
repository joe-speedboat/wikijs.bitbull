---
title: Unmount blocked FS
description: Resolving "Device is busy" When Unmounting
published: true
date: 2026-10-26T14:12:02.726Z
tags: linux, mount
editor: markdown
dateCreated: 2026-02-15T06:20:13.617Z
---

## Resolving "Device is busy" When Unmounting

```bash
$ umount /cdrom
/dev/sr1: Device is busy
```

This indicates that some process is still accessing the CD-ROM. Either a user has files open on it, or a program is using it as its current working directory.

To identify the process:

```bash
$ fuser -u /cdrom
/cdrom:   348c(bill)
```

The output shows that process ID **348**, owned by user **bill**, is accessing `/cdrom`.

If you need to terminate all processes using the mount point:

```bash
$ fuser -k /cdrom
/cdrom:   348c
No automatic removal. Please use umount /cdrom
```

Now try unmounting again:

```bash
$ umount /cdrom
```

The unmount should now succeed.

---

### If It Still Does Not Work

As `root`, you can forcefully terminate all processes accessing files within the mount point:

```bash
$ fuser -k /cdrom/*.*
```

---

### Other Mounted Directories or Partitions

If local directories or mounted partitions are affected (for example `/win/d`):

```bash
$ fuser -k /win/d/*.*
```

This will terminate all processes currently accessing files within that path.
