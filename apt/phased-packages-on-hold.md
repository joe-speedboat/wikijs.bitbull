---
title: packages hold by phasing
description: Ubuntu/Debian phased packages hold back due unmet depencies
published: true
date: 2026-10-26T14:12:09.375Z
tags: linux, apt, ubuntu, debian
editor: markdown
dateCreated: 2026-02-15T07:31:22.462Z
---

## Ubuntu packages held back due to unmet dependencies

* **Problem:** Not all packages on a system upgrade and are mentioned as held back

```
root@srvtestl12p:~# apt-get dist-upgrade
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
Calculating upgrade... Done
The following packages have been kept back:
  base-files cloud-init coreutils cryptsetup cryptsetup-bin cryptsetup-initramfs distro-info dpkg ethtool firmware-sof-signed iptables kpartx landscape-common ldap-utils libcryptsetup12 libcups2
  libip4tc2 libip6tc2 libldap-2.5-0 libldap-common libmm-glib0 libnss-systemd libpam-systemd libsystemd0 libudev1 libxtables12 modemmanager motd-news-config multipath-tools python-apt-common
  python3-apt python3-distro-info python3-distupgrade python3-gssapi python3-software-properties python3-update-manager snapd software-properties-common systemd systemd-hwe-hwdb systemd-sysv
  ubuntu-advantage-tools ubuntu-pro-client-l10n ubuntu-release-upgrader-core udev update-manager-core update-notifier-common vim vim-common vim-runtime vim-tiny xxd
0 upgraded, 0 newly installed, 0 to remove and 52 not upgraded.

root@srvtestl12p:~# apt-cache policy vim-tiny
vim-tiny:
  Installed: 2:8.2.3995-1ubuntu2.13
  Candidate: 2:8.2.3995-1ubuntu2.17
  Version table:
     2:8.2.3995-1ubuntu2.17 500 (phased 20%)
        500 katello://foreman.domain.tld/pulp/deb/ORG/lc_env_prod/ubuntu22-04/custom/Ubuntu_22_04/jammy-updates default/all amd64 Packages
     2:8.2.3995-1ubuntu2.16 500
        500 katello://foreman.domain.tld/pulp/deb/ORG/lc_env_prod/ubuntu22-04/custom/Ubuntu_22_04/jammy-security default/all amd64 Packages
 *** 2:8.2.3995-1ubuntu2.13 100
        100 /var/lib/dpkg/status
     2:8.2.3995-1ubuntu2 500
        500 katello://foreman.domain.tld/pulp/deb/ORG/lc_env_prod/ubuntu22-04/custom/Ubuntu_22_04/jammy default/all amd64 Packages
```

## WHY

Updates are rolled out only to a subset of client machines (grouped by machine-id) to minimize impact in case of broken packages.

Example: If a broken package is rolled out with "phase for ex: 20%" and in the first week several clients report errors, the other 80% are not affected and the phased rollout gets stopped.

* There is a fix, see link (3) for Ubuntu 24.04 and later  
* https://ubuntu.com/server/docs/about-apt-upgrade-and-phased-updates  
* https://ubuntu-archive-team.ubuntu.com/phased-updates.html  
* https://bugs.launchpad.net/ubuntu/+source/apt/+bug/1988819  

## HOW TO GET RID OF

* `vim /etc/apt/apt.conf.d/99no-phased-updates`

```
APT::Get::Always-Include-Phased-Updates "true";
```

The problem is that if you enable that, you always get "critical/buggy" updates first.  
Maybe that is not what you want.

---

## OUR SOLUTION / WAY TO GO

* We probably get affected by this issue when:
  * Moving repos from "public" to "Satellite/Foreman/local mirror"
  * Updating systems which have big gaps in software versions (not updated for a long period)

So we decided to:

```
echo 'APT::Get::Always-Include-Phased-Updates "true";' > /etc/apt/apt.conf.d/99no-phased-updates
apt-get clean all
apt-get update
apt-get dist-upgrade # must show held packages as upgradable
apt-get clean all
rm -fv /etc/apt/apt.conf.d/99no-phased-updates
apt-get update
apt-get dist-upgrade # must show no packages
```

* To get informed about systems affected by this issue, we create a Rundeck job pointing to these systems.

---

## Down the rabbit hole

This phased update information is carried in the `Packages` files in the repository metadata.  
See example here:

```
curl -s http://archive.ubuntu.com/ubuntu/dists/jammy-updates/main/binary-amd64/Packages.gz | gunzip - | grep -e ^Phased -e Package: | grep -B1 ^Phased
Package: python3-update-manager
Phased-Update-Percentage: 0
--
Package: update-manager
Phased-Update-Percentage: 0
Package: update-manager-core
Phased-Update-Percentage: 0
```

* https://git.launchpad.net/ubuntu-archive-tools/tree/phased-updater  

This script, running on package distribution systems, looks for bugs/heat-level and decreases the `Phased-Update-Percentage` if the heat-level rises. Otherwise, it increments the `Phased-Update-Percentage` step by step over time.
