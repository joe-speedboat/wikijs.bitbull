---
title: pack files into shell script
description: Howto pack files into shell script
published: true
date: 2026-10-26T14:12:11.005Z
tags: linux, shell, script
editor: markdown
dateCreated: 2026-02-15T07:40:18.509Z
---

From time to time the necessity arises to also include the setup files, e.g.: rpm, tar.gz ... inside a shell script.

base64 has always been a useful helper for me here. below is a small example ...

first we pack the desired data together with tar, pipe it through base64 and write it into my future install script:

```
tar cz /opt/vpnclient/ /etc/CiscoSystemsVPNClient/ /etc/opt/cisco-vpnclient/ | base64 > install_vpnclient.sh
```

now I can edit my script, in the end it could perhaps look like this:

```
#!/bin/bash
rm -rf /tmp/root
mkdir /tmp/root
cd /tmp/root
echo welcome to my setup, first of all i have to extract my suspect base64 archive ... please wait ...
echo 'H4sIABo1iEcAA+xbCXRb1Zm+90mypbwryZZlP0e2YjmyE2dzHMd2QsgKCQTCHmCCSavIkpwIW36q
lsRQaAMNLUtgGAaYHAhMCikznaEQMqW0QAtMgCGFA7RNmXRJy5JOaco27Nuk83/3XjlKujqnnTM9
...
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' | base64 -i -d | tar xz >/dev/null
echo files extracted, going to do setup ...
cd /opt/vpnclient
./install.sh
echo setup is now finished ... bye
```

