---
title: MISP Setup
description: Install MISP
published: true
date: 2026-02-20T14:48:08.610Z
tags: misp, podman
editor: markdown
dateCreated: 2026-02-20T14:48:08.610Z
---

# Setup Notes v2.4.195
* This is my working note to setup docker-based misp setup.   
* Please feel free to add a wiki on this page.   
* Consider that compiling any docker images in production is not allowed and not in focus of this document.
* CAP_AUDIT_WRITE and TAG_vars may get integrated natively later on.
* Ability to get ALL docker volumes persistent and located on one specific point is desirable, my approach is probably not best, but clean.

Cheers, Chris

## Prepare / Proceed
* Setup Rocky 9 minimal.
* Prepare Settings as needed in vars below.
* Carefully place commands: understand, apply, verify.
* Test.

## Outcome
* Docker-based misp setup.
* SELinux enabled.
* Independent .env and docker-compose.yml, comparable with git repo: /srv/misp-containers.
  * Please note that docker images may change once released; if you want to persist, stick to commit tags in .env.
* All Docker data is located under: /srv/misp-volumes.
* Test approach for cert replacement.

## Open items
* Document upgrade path.

## Enforce SELinux
```bash
dnf -y install setroubleshoot-server
sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config
grep ^SELINUX= /etc/selinux/config
   SELINUX=enforcing
setenforce 1
getenforce
```

## Firewall Setup
```bash
dnf -y install firewalld
systemctl is-enabled firewalld
systemctl restart firewalld
firewall-cmd --add-service https --permanent
systemctl restart firewalld
```

## Podman Setup
```bash
dnf -y install epel-release
dnf -y install podman-compose podman skopeo

sed -i.bak 's/^unqualified-search-registries .*/unqualified-search-registries = ["docker.io"]/' /etc/containers/registries.conf
systemctl enable podman
systemctl restart podman
```

### Podman default network configuration
```bash
# create custom config
echo '# custom podman default networking
[network]
default_network = "podman"
default_subnet = "192.168.223.0/24"
default_subnet_pools = [{"base" = "192.168.224.0/20", "size" = 24}]
' >> /etc/containers/containers.conf
restorecon -FRv /etc/containers/containers.conf

systemctl restart podman
systemctl status podman
```

#### Podman default network configuration testing (optional)
```bash
mkdir /srv/compose-test
echo '
version: "3.8"

services:
  busybox:
    image: busybox
    command: sleep 3600
' > /srv/compose-test/docker-compose.yml

cd /srv/compose-test
podman-compose up

podman network ls
podman network inspect podman
podman network inspect compose-test_default
```

## Start the fresh misp configuration
```bash
cd /srv

genpasswd() {
        local l=$1
        [ "$l" == "" ] && l=40
        tr -dc A-Za-z0-9_ < /dev/urandom | head -c ${l} | xargs
}

mkdir /srv/git /srv/misp-containers /srv/misp-volumes
cd /srv/git
git clone https://github.com/MISP/misp-docker.git
cd /srv/git/misp-docker

# check latest version
grep _TAG=  template.env
        CORE_TAG=v2.4.195
        MODULES_TAG=v2.4.195

cp -av docker-compose.yml /srv/misp-containers
cp -av template.env /srv/misp-containers/.env
cd /srv/misp-containers

# replace latest with tags, due we dont want to compile "this is a bug in compose file"
sed -i 's/misp-core:latest/misp-core:${CORE_TAG}/' docker-compose.yml
sed -i 's/misp-modules:latest/misp-modules:${MODULES_TAG}/' docker-compose.yml

# Corporate specific config
ADMIN_ORG="MyOrg"
SMARTHOST_ADDRESS="mailgw.domain.tld"
SMARTHOST_PORT=25
MISP_EMAIL="sender@domain.tld"
MISP_CONTACT="contact@domain.tld"
DISABLE_IPV6=true
BASE_URL="https://misp-test.domain.tld"

sed -i "s|^ADMIN_ORG=.*|ADMIN_ORG=\"$ADMIN_ORG\"|" .env
sed -i "s|^SMARTHOST_ADDRESS=.*|SMARTHOST_ADDRESS=\"$SMARTHOST_ADDRESS\"|" .env
sed -i "s|^SMARTHOST_PORT=.*|SMARTHOST_PORT=$SMARTHOST_PORT|" .env
sed -i "s|^# MISP_EMAIL=.*|MISP_EMAIL=\"$MISP_EMAIL\"|" .env
sed -i "s|^# MISP_CONTACT=.*|MISP_CONTACT=\"$MISP_CONTACT\"|" .env
sed -i "s|^# DISABLE_IPV6=.*|DISABLE_IPV6=$DISABLE_IPV6|" .env
sed -i "s|^BASE_URL=.*|BASE_URL=\"$BASE_URL\"|" .env

# random passwords
MYSQL_ROOT_PASSWORD=$(genpasswd)
MYSQL_PASSWORD=$(genpasswd)
REDIS_PASSWORD=$(genpasswd)
ENCRYPTION_KEY=$(genpasswd)

sed -i "s/# MYSQL_ROOT_PASSWORD=.*/MYSQL_ROOT_PASSWORD=\"$MYSQL_ROOT_PASSWORD\"/" .env
sed -i "s/# MYSQL_PASSWORD=.*/MYSQL_PASSWORD=\"$MYSQL_PASSWORD\"/" .env
sed -i "s/# REDIS_PASSWORD=.*/REDIS_PASSWORD=\"$REDIS_PASSWORD\"/" .env
sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=\"$ENCRYPTION_KEY\"/" .env
```

### Pull Docker images
```bash
cd /srv/misp-containers
podman-compose pull
```

### Insert CAP_AUDIT_WRITE to misp-core pod in docker compose file
```bash
# insert cap_add-CAP_AUDIT_WRITE
cd /srv/misp-containers
awk '
/misp-core:/ {print; in_misp_core=1; next}
/^[[:space:]]*[^[:space:]]/ && in_misp_core {in_misp_core=0; if (!cap_found) {print "    cap_add:"; print "      - CAP_AUDIT_WRITE"}}
{print}
' docker-compose.yml > temp.yml && mv -fv temp.yml docker-compose.yml
```

### Update volumes in docker compose file and remove port 80
```bash
cd /srv/misp-containers

# change misp-core volume settings
sed -i 's|.*\/var/www/MISP/app/Config.*|      - configs:/var/www/MISP/app/Config|' docker-compose.yml
sed -i 's|.*\/var/www/MISP/app/tmp/logs.*|      - logs:/var/www/MISP/app/tmp/logs|' docker-compose.yml
sed -i 's|.*\/var/www/MISP/app/files.*|      - files:/var/www/MISP/app/files|' docker-compose.yml
sed -i 's|.*\/etc/nginx/certs.*|      - ssl:/etc/nginx/certs|' docker-compose.yml
sed -i 's|.*\/var/www/MISP/.gnupg.*|      - gnupg:/var/www/MISP/.gnupg|' docker-compose.yml

# inject redis volume
awk '
/^  redis:/ {print; in_redis=1; next}  # Match exactly "  redis:"
/^[[:space:]]*[^[:space:]]/ && in_redis {in_redis=0; if (!volumes_found) {print "    volumes:"; print "      - redis_data:/data"}}
{print}
' docker-compose.yml > temp.yml && mv -fv temp.yml docker-compose.yml

# add missing volumes at the end
echo '    configs:
    files:
    gnupg:
    logs:
    ssl:
    redis_data:
' >> docker-compose.yml

# remove port 80
sed -i '/80:80/d' docker-compose.yml

# add selinux volume tags
sed -i '/^[[:space:]]*#/!s|\(^[[:space:]]*-[[:space:]]*[^[:space:]]*:/[^[:space:]]*\)$|\1:Z|' docker-compose.yml

# verify changes
vimdiff docker-compose.yml ../git/misp-docker/docker-compose.yml
```

### Create volumes for pods
```bash
cd /srv/misp-volumes

for vol in misp-containers_mysql_data misp-containers_configs misp-containers_files misp-containers_gnupg misp-containers_logs misp-containers_ssl misp-containers_redis_data
do
echo "------ $vol"
mkdir $vol
podman volume create --opt type=none --opt o=bind --opt device=/srv/misp-volumes/$vol $vol
done
```

## Start compose and wait for finishing message
```bash
cd /srv/misp-containers/

# first start and follow logs
podman-compose up -d
podman logs -f misp-containers_misp-core_1
podman-compose down

podman network inspect misp-containers_default
```

## Now make a service out of it
```bash
echo '[Unit]
Description=Docker Compose: MISP

[Service]
Type=oneshot
WorkingDirectory=/srv/misp-containers
ExecStart=/usr/bin/podman-compose up -d
ExecStop=/usr/bin/podman-compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target' > /etc/systemd/system/docker-misp.service

restorecon -FRv /etc/systemd/system

systemctl daemon-reload

systemctl start docker-misp
systemctl enable docker-misp
systemctl status docker-misp

podman logs -f misp-containers_misp-core_1
```

## TEST
* https://test-misp.domain.tld/servers/serverSettings/diagnostics
  * admin@admin.test / admin

## Custom Server Cert (just for Testing)
```bash
# Read Documentation in Readme first, there you find all
cd /usr/local/sbin
curl https://raw.githubusercontent.com/joe-speedboat/linux.scripts/master/shell/cert-create-ca.sh > cert-create-ca.sh
chmod 700 cert-create-ca.sh
cert-create-ca.sh $(hostname -f) # replace with your test fqdn

systemctl stop docker-misp

# [root@test-misp01 sbin]# ll /srv/misp-volumes/misp-containers_ssl/
# total 12
#-rw-r--r--. 1 root root 1805 Jun 26 13:51 cert.pem
#-rw-r--r--. 1 root root  424 Jun 26 13:52 dhparams.pem
#-rw-------. 1 root root 3272 Jun 26 13:51 key.pem

#[root@test-misp01 sbin]# find /root/MySsl
#/root/MySsl
#/root/MySsl/test-misp01.domain.tld
#/root/MySsl/test-misp01.domain.tld/servers
#/root/MySsl/test-misp01.domain.tld/servers/test-misp01.domain.tld_cert.pem
#/root/MySsl/test-misp01.domain.tld/servers/test-misp01.domain.tld_privkey.pem
#/root/MySsl/test-misp01.domain.tld/servers/test-misp01.domain.tld_ca_chain.pem
#/root/MySsl/test-misp01.domain.tld/tmp
#/root/MySsl/test-misp01.domain.tld/tmp/test-misp01.domain.tld.csr.pem
#/root/MySsl/ca
#/root/MySsl/ca/root.crt.pem
#/root/MySsl/ca/root.key.pem
#/root/MySsl/ca/root.crt.srl

cat /root/MySsl/test-misp01.domain.tld/servers/test-misp01.domain.tld_cert.pem > /srv/misp-volumes/misp-containers_ssl/cert.pem
cat /root/MySsl/test-misp01.domain.tld/servers/test-misp01.domain.tld_privkey.pem > /srv/misp-volumes/misp-containers_ssl/key.pem
cat /root/MySsl/ca/root.crt.pem > /srv/misp-volumes/misp-containers_ssl/ca.pem

systemctl start docker-misp
```