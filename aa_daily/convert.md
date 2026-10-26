---
title: convert
description: About converting
published: true
date: 2026-10-26T14:11:21.525Z
tags: cmd, convert, helpers
editor: markdown
dateCreated: 2026-02-13T09:06:59.737Z
---

## rename files with special characters in it
```bash
convmv --notest -f latin1 -t utf8 *.pdf
```

## remove umlauts from file/folders
```bash
find . -type d | while read dir; do rename 's/ö/oe/g;s/Ö/Oe/g;s/ü/ue/g;s/Ü/Ue/g;s/ä/ae/g;s/Ä/Ae/g' "$dir"; done
find . -type f | while read file; do rename 's/ö/oe/g;s/Ö/Oe/g;s/ü/ue/g;s/Ü/Ue/g;s/ä/ae/g;s/Ä/Ae/g' "$file"; done
```

## remove commented lines from file
```bash
sed 's/#.*$//' -e '/^$/d' -e '/^\s*#.*$/d' /etc/file.cfg
```

## unix2dos with sed
```bash
sed -i 's/$/\r/' file.txt
```

## dos2unix with sed
```bash
sed -i 's/\r//' file.txt
```

## search and replace onliner
```bash
sed -i 's/search/replace/g;' *.txt
```

## replace multiline pattern
```bash
perl -i -pe 'BEGIN{undef $/;} s/START_PATTERN.*END_PATTERN/REPLACE_STRING/smg' file1.txt
```

## display a block of text with AWK
```bash
awk '/start_pattern/,/stop_pattern/' file.txt
```

## delete Block of Text with sed
```bash
cat MYFILE |sed '/START_PATTERN/,/END_PATTERN/d'
```

## prettify an XML file
```bash
tidy -xml -i -m [file]
xmllint --format [file]
```

## prettify an JSON file
```bash
cat file.json | python -m json.tool
```

## list installed packages and repo
```bash
repoquery -a --installed --qf "%{ui_from_repo} %{name}"
yum list installed | egrep -i 'epel|ovirt'
```

## convert txt to pdf
```bash
cal > cal.txt
enscript -o cal.ps cal.txt 
ps2pdf cal.ps 
```

## remove color from bash output (escape sequences)
```bash
color-script.sh  | col -b | sed 's/0;[0-9]*m//g'
color-script.sh  | sed 's/\x1b\[[0-9;]*m//g' 
```
## convert bash color output into html file
```bash
yes | ansible-playbook csv-runner-baseEvpn.yml  | tee >(aha > ansible_example_output.html)
```
## quick access to the ascii table
```bash
dnf -y install man-pages || apt-get -y install manpages
man ascii
```
