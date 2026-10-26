---
title: guacamole
description: HTML remote gateway for RDP, VNC and SSH
published: true
date: 2026-10-26T14:11:39.734Z
tags: product, guacamole
editor: markdown
dateCreated: 2026-02-13T09:07:16.448Z
---

## Compile guacamole auth radius
* this are just some notes how i compiled the extension
```bash
VERS=1.5.1
git clone https://github.com/joe-speedboat/docker.guacamole-auth-radius-build.git
cd guacamole-auth-radius
sed -i "s/ARG VERSION=.*/ARG VERSION=$VERS/" Dockerfile
docker build --tag guacamole-auth-radius .
docker run -d --name=guacamole-auth-radius guacamole-auth-radius
docker cp guacamole-auth-radius:/guacamole-auth-radius-$VERS.jar .
docker container prune -f
docker image prune -a -f

scp guacamole-auth-* root@test01:

vi /etc/guacamole/guacamole.properties
------------
radius-hostname 192.168.111.222
radius-auth-port 1812
radius-auth-protocol pap
radius-shared-secret xxx...xxx
------------
systemctl restart nginx guacd tomcat

cp -v guacamole-auth-radius-$VERS.jar /usr/share/tomcat/.guacamole/extensions/aaa-guacamole-auth-radius-$VERS.jar

TEST
------------
- existing freeipa user without totp -> ok
- existing freeipa user with totp -> ok
- freeipa user created with totp enforced
  - password changed
  - totp created
  - guacamole login via radius (password+token) -> ok

- freeipa user created with totp enforced
  - password changed
  - totp NOT created *****ACHTUNG*****
  - guacamole login via radius (password) -> ok, but allowed by freeipa design
```