---
title: find
description: finding things
published: true
date: 2026-02-15T08:04:24.983Z
tags: cmd, helpers, find
editor: markdown
dateCreated: 2026-02-13T09:07:03.121Z
---

## Find suid bits
```bash
 find / -xdev -perm -4000 -exec ls -l {} \;
```

## Find world-writable files
```bash
find / -xdev -perm -o+w -and -not \( -type l -or -type s -or -perm -o+t \) -exec ls -ld {} \;
```

## Find Duplicate Files (based on size first, then MD5 hash)
```bash
find -not -empty -type f -printf "%s\n" | sort -rn | uniq -d | xargs -I{} -n1 find -type f -size {}c -print0 | xargs -0 md5sum | sort | uniq -w32 --all-repeated=separate
```

## remove files older than 60 days
```bash
find /var/log/ -type f -name '*.log' -ctime +60 -exec rm -f {} \;
```

## show what have been modified last 60 minutes
```bash
find / -mmin +60 -type f
```

## find files with lines longer than
```bash
find . -type f -exec grep -l '.\{80\}' {} \;
```

## find core dumps
```bash
/bin/nice -19  /usr/bin/find / -type f -print 2>/dev/null | egrep  -r '/core\.[0-9]{2,}' | /usr/bin/xargs ls -l
```
## get file modification age in days
```bash
echo $((($(date +%s) - $(stat -c %Y -- /etc/hosts)) / 86400)) days
```


## find differences between two files
classical side-by-side comparison
```bash
diff -y file1 file2
```

## enhanced comparison with highlighting (package: vim-enhanced)
```bash
vimdiff file1 file2
```

## compare a remote file with a local file
```bash
ssh user@host cat /path/to/remotefile | diff -y /path/to/localfile -
```


