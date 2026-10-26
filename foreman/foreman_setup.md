---
title: foreman setup
description: Setup Foreman on Rocky Linux 9
published: true
date: 2026-10-26T14:12:32.521Z
tags: foreman
editor: markdown
dateCreated: 2026-02-20T14:35:31.130Z
---

# VM SETUP
* CPU: 4
* MEM: 20G
* DISK: 200G
* Host IP: eg: 1.2.3.4

## DNS requirements
I use this, because i also stand behind a firewall with loadbalancer and want to use letsencrypt cert for public
* A-Record: eg: foreman01.domain.tld
* CNAME: eg: satellite.domain.tld 
* Cert Location: /etc/pki/letsencrypt #keep this place restricted: root.root 0640
```bash
wget https://raw.githubusercontent.com/joe-speedboat/linux.scripts/master/shell/openssl_check_cert_chain.sh
bash openssl_check_cert_chain.sh /etc/pki/letsencrypt/fullchain.pem 
 0: subject=CN = foreman.domain.tld
issuer=C = US, O = Let's Encrypt, CN = R10
 1: subject=C = US, O = Let's Encrypt, CN = R10
issuer=C = US, O = Internet Security Research Group, CN = ISRG Root X1
 2: subject=C = US, O = Internet Security Research Group, CN = ISRG Root X1
issuer=C = US, O = Internet Security Research Group, CN = ISRG Root X1
/etc/pki/letsencrypt/fullchain.pem: OK
```

# LINKS
* https://docs.theforeman.org/3.11/Quickstart/index-katello.html

# OUTSIDE CONNECTIVITY NEEDS
* https://cdn.redhat.com
* https://yum.theforeman.org
* http://yum.puppetlabs.com

# Install
```bash
dnf clean all
dnf -y install https://yum.theforeman.org/releases/3.11/el9/x86_64/foreman-release.rpm
dnf -y install https://yum.theforeman.org/katello/4.13/katello/el9/x86_64/katello-repos-latest.rpm
dnf -y install https://yum.puppet.com/puppet7-release-el-9.noarch.rpm
dnf repolist enabled


dnf -y upgrade
dnf -y install foreman-installer-katello


dnf -y install firewalld

systemctl enable firewalld --now

firewall-cmd \
--add-port="80/tcp" --add-port="443/tcp" \
--add-port="5647/tcp" \
--add-port="8000/tcp" --add-port="9090/tcp" \
--add-port="8140/tcp" \
#--add-port="53/udp" --add-port="53/tcp" \
#--add-port="67/udp" \
#--add-port="69/udp"

firewall-cmd --runtime-to-permanent

firewall-cmd --list-all
   public (active)
     services: cockpit dhcpv6-client ssh
     ports: 80/tcp 443/tcp 5647/tcp 8000/tcp 9090/tcp 8140/tcp

ping -c1 localhost
ping -c1 `hostname -f`

echo "1.2.3.4 foreman01.domain.tld" >> /etc/hosts
echo "1.2.3.4 satellite.domain.tld" >> /etc/hosts

hostnamectl set-hostname `hostname -f`

dnf clean all
dnf makecache
dnf -y upgrade

yum -y install chrony
systemctl start chronyd
systemctl enable chronyd

echo sources | chronyc

reboot
```

```bash
foreman-installer --scenario katello \
 --foreman-servername satellite.domain.tld \
 --foreman-foreman-url https://satellite.domain.tld \
 --foreman-unattended-url https://satellite.domain.tld \
 --foreman-proxy-foreman-base-url https://satellite.domain.tld \
 --foreman-proxy-registered-name satellite.domain.tld \
 --foreman-proxy-registered-proxy-url https://satellite.domain.tld:9090 \
 --foreman-proxy-puppet-url https://satellite.domain.tld:8140 \
 --puppet-server-foreman-url https://satellite.domain.tld \
 --foreman-proxy-template-url http://satellite.domain.tld:8000 \
 --foreman-proxy-trusted-hosts satellite.domain.tld \
 --foreman-proxy-trusted-hosts foreman01.domain.tld \
 --foreman-proxy-trusted-hosts "127.0.0.1/8" \
 --foreman-proxy-trusted-hosts "::1" \
 --foreman-proxy-trusted-hosts "$(hostname -i)" \
 --foreman-trusted-proxies "127.0.0.1/8" \
 --foreman-trusted-proxies "::1" \
 --foreman-trusted-proxies "$(hostname -i)" \
 --foreman-initial-organization "BITBULL" \
 --foreman-initial-location "Core" \
 --foreman-initial-admin-username admin \
 --foreman-initial-admin-password change-me. \
 --enable-foreman-cli \
 --enable-foreman-cli-katello \
 --enable-foreman-plugin-statistics \
 --enable-foreman-plugin-tasks \
 --certs-server-cert "/etc/pki/letsencrypt/cert.pem" \
 --certs-server-key "/etc/pki/letsencrypt/key.pem" \
 --certs-server-ca-cert "/etc/pki/letsencrypt/fullchain.pem" 

hammer settings list | grep foreman01
hammer settings set --id foreman_url --value https://satellite.domain.tld

hammer settings list | grep trusted_ho
# trusted_hosts                                          | Trusted hosts                                                | []                                                                               | List of hostnames, IPv4, IPv6 addresses or subnets to be trusted in addition ...

hammer settings set --id trusted_hosts --value '[foreman01.domain.tld, satellite.domain.tld, 1.2.3.4]'
# Setting [trusted_hosts] updated to [["foreman01.domain.tld", "satellite.domain.tld", "1.2.3.4"]].


foreman-installer \
 --enable-foreman-plugin-remote-execution \
 --enable-foreman-proxy-plugin-remote-execution-script
```


# Foreman Content Management - Menu Overview
![foreman_35_menu.png](/foreman_35_menu.png)

# Manage Repos with Foreman
* https://opensource.com/article/21/9/centos-stream-foreman
* https://www.youtube.com/watch?v=XsCi9Jy2lGs&t=3s

# Create Content
## Sync Plan
* Content > Sync Plans
  * Create Sync Plan > Daily

## Products/Repos
### Rocky 9
* Content > Products > Repo Discovery
  * Type: Yum Repositories
  * URL to Discover: https://pkg.adfinis.com/rockylinux/9/
  * Filter: /9/AppStream/x86_64/os/
  * Filter: /9/BaseOS/x86_64/os/
  * Filter: /9/extras/x86_64/os/
  * Filter: /9/plus/x86_64/os/
  * Filter: /9/BaseOS/x86_64/kickstart/ 
  * Name: Rocky Linux
  * Add "Rocky Linux 9" in front of suggested Repository Name
  * Run Repository Creation

* Products > Rocky Linux
  * Sync Plan: Daily

* Products > Rocky Linux > Repositories: ALL
* Restrict to architecture: x86_64

### EPEL 9
* Content > Products > Create
  * Name: EPEL
  * Sync Plan: Daily

  * Repositories > New Repositoriy
    * Type: yum
    * Name: epel-el9
    * Restrict to Architecture: x86_64
    * Upstream url: https://pkg.adfinis.com/epel/9/Everything/x86_64/
    * Save





## Lifecycle Environment
* Content > Lifecycle Environment > Create
  TestLcEnv > ProdLcEnv

## Content View
Remind to sync all Repos before proceeding with this steps
* Content > Content views > Create
  * Name: cv_rocky9
  * Solve dependencies: TRUE
  * CV: cv_rocky9 > TAB:Repositories
  * Add: all except Kickstart (think)

* Content > Content views > cv_rocky9 > Publish new version
  * Promote: TRUE
  * Version: 1.0
  * Env: TestLcEnv + ProdLcEnv





## Activation Keys
* Content > Activation Keys > Create
  * Name: ak_rocky9_test
  * Environment: TestLcEnv
  * Content View: cv_rocky9
  * Repository Sets: Disable all but needed

* Content > Activation Keys > Create
  * Name: ak_rocky9_prod
  * Environment: ProdLcEnv
  * Content View: cv_rocky9
  * Repository Sets: Disable all but needed

# Register System
* Hosts > Register Host > select needed settings
* Copy-Paste Register info to root on target system

## Disable Default Repos
```bash
curl https://raw.githubusercontent.com/joe-speedboat/linux.scripts/master/shell/foreman_host_disable_default_repos.sh | bash
```




# Patch Cycle Ideas Brainstorming
## Prerequisites
* Daily Sync of all Foreman Libraries (Product upstream Repos)
* Working Repos as mentioned above
* Systems are grouped and registered in Lifecycle Environments
  * TEST
  * TEST-LATE
  * PROD
  * PROD-LATE
The meaning of "LATE" is to patch this systems later to avoid production issues (eg: half of the systems of a Cluster (DNS, Web, ...)

## Patch Cycle
* All systems get patched at least every 4 weeks
* A Rundeck Job does update the Content Views on a regular base.
```bash
EXAMPLE:
----------------------------------
KW01 -> "Library" (daily sync) into "TEST" Content View as Version "KW01"
KW02 -> Version "KW01" into "TEST-LATE" Content View
KW03 -> Version "KW01" into "PROD" Content View
KW04 -> Version "KW01" into "PROD-LATE" Content View
KW05 -> "Library" (daily sync) into "TEST" Content View as Version "KW05"
KW06 -> Version "KW05" into "TEST-LATE" Content View
KW07 -> Version "KW05" into "PROD" Content View
KW08 -> Version "KW05" into "PROD-LATE" Content View
...
```

# TIPPS AND TRICKS
* Push Host Package State to Foreman
```bash
subscription-manager repos --list
```