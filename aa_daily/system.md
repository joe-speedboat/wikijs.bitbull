---
title: system
description: System-related commands
published: true
date: 2026-10-26T14:11:33.311Z
tags: cmd, helpers
editor: markdown
dateCreated: 2026-02-13T09:07:09.829Z
---

## Force RHEL9 to Boot into Specific Kernel Version

If you do not have remote console access, you can set the next kernel version to boot with this:

```bash
VERS=5.14.0-362.13.1.el9_3.x86_64

grubby --info=ALL | grep -e $VERS -e ^
index=0
kernel="/boot/vmlinuz-5.14.0-362.18.1.el9_3.x86_64"
args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M rd.md.uuid=000:aaa:bbb:ccc"
root="UUID=567zerts-xxxx-eeee-5555-terhge676z3r"
initrd="/boot/initramfs-5.14.0-362.18.1.el9_3.x86_64.img"
title="Rocky Linux (5.14.0-362.18.1.el9_3.x86_64) 9.3 (Blue Onyx)"
id="dsfgsdfgsdgdfsdfgsdfgsdfgsdfgsdf-5.14.0-362.18.1.el9_3.x86_64"

index=1
kernel="/boot/vmlinuz-5.14.0-362.13.1.el9_3.x86_64"
args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M rd.md.uuid=000:aaa:bbb:ccc"
root="UUID=567zerts-xxxx-eeee-5555-terhge676z3r"
initrd="/boot/initramfs-5.14.0-362.13.1.el9_3.x86_64.img"
title="Rocky Linux (5.14.0-362.13.1.el9_3.x86_64) 9.3 (Blue Onyx)"
id="dsfgsdfgsdgdfsdfgsdfgsdfgsdfgsdf-5.14.0-362.13.1.el9_3.x86_64"

index=2
kernel="/boot/vmlinuz-5.14.0-70.13.1.el9_0.x86_64"
args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M rd.md.uuid=000:aaa:bbb:ccc"
root="UUID=567zerts-xxxx-eeee-5555-terhge676z3r"
initrd="/boot/initramfs-5.14.0-70.13.1.el9_0.x86_64.img"
title="Rocky Linux (5.14.0-70.13.1.el9_0.x86_64) 9.0 (Blue Onyx)"
id="dsfgsdfgsdgdfsdfgsdfgsdfgsdfgsdf-5.14.0-70.13.1.el9_0.x86_64"
```

```bash
grubby --set-default=/boot/vmlinuz-$VERS
# The default is /boot/loader/entries/aaabbbcccdddeeefgffsdfhfsghsfdgs-5.14.0-362.13.1.el9_3.x86_64.conf with index 1 and kernel /boot/vmlinuz-5.14.0-362.13.1.el9_3.x86_64
```

```bash
grub2-mkconfig -o /boot/grub2/grub.cfg
# Generating grub configuration file ...
# lsblk: /dev/mapper/test-vpool0: not a block device
# Adding boot menu entry for UEFI Firmware Settings ...
# done
```

## Get Hypervisor Information from Within VM

```bash
cat /sys/class/dmi/id/sys_vendor
```

## Show File System Hierarchy

```bash
man hier
```

## Execute a Command Without Saving It in the History

```bash
<space>command
```

## Show Date in Bash History

```bash
echo 'export HISTTIMEFORMAT="%d/%m/%y %T "' >> ~/.bash_profile
. ~/.bash_profile
history
```

## Execute Command at Given Time

```bash
echo "ls -l" | at 22:00 30.12.13
```

## Insert Newline into Cronjob

```bash
30 1 * * *  /usr/bin/ssh admin@10.0.0.1 'execute reboot ^My' >/dev/null 2>&1
# CTRL-v, CTRL-m
```

## Salvage a Borked Terminal

```bash
reset
```

## Rapidly Invoke an Editor to Write a Long Command

```bash
EDITOR=vim
ctrl-x e
# hold ctrl, then hit x, then hit e, release ctrl
```

## Run Last Command as Root

```bash
sudo !!
# forgot to login as root, take it easy
```

## Change into Shell of a Disabled System User

```bash
getent passwd nginx # check if shell is disabled
  # nginx:x:995:993:Nginx web server:/var/lib/nginx:/sbin/nologin

su - nginx # which will not work
  # This account is currently not available.

su -s /bin/bash nginx # which will work
  # bash-4.2$ id
  # uid=995(nginx) gid=993(nginx) groups=993(nginx) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
```

## Runs Previous Command but Replacing

```bash
^foo^bar
# example(replace once):
vi 7etc/hosts
^7^/

!!:gs/foo/bar
# example(replace many):
vi 7etc7hosts
!!:gs#7#/
```

## Configure Date and Time

Get system time from ntp-server:
```bash
ntpdate pool.ntp.org
```
Manually set system time:
```bash
date MMDDhhmmYYYY
date MMDDhhmm
# example 27.12.1975 08:00
date 122708001975
```
Write system time into bios (hw clock):
```bash
hwclock -w
```
Set timezone:
```bash
cd /etc
ln -sf /usr/share/zoneinfo/EST localtime
```

## Find System Installation Date

```bash
tune2fs -l $(df -P / | tail -n1 | cut -d' ' -f1 ) | grep 'Filesystem created:'
ls -lact --full-time /etc | tail -1 | awk '{print $6,$7}'
rpm -qi basesystem | grep Install
```

## Create Nice Overview of System Hardware

```bash
lshw -html > hardware.html
```

## Processor / Memory Bandwidth in GB/s

```bash
dd if=/dev/zero of=/dev/null bs=1M count=32768
```

## Ultimate System Monitoring Command

```bash
dstat -f -M time,cpu,net,disk,sys,swap,page,load,proc,topcpu --output $(date '+%Y.%m.%d-%H.%M')-dstat.csv
dstat -cdngymsp --lock --tcp --output $(date '+%Y.%m.%d-%H.%M')-dstat.csv
```

## strace Examples

```bash
strace -ff -e trace=write -e write=1,2 -p SOME_PID
strace -e open ls
strace -e trace=open,read ls /home
strace -o output.txt ls 
strace -f -p 1725 -o firefox_trace.txt # f: follow process
strace -t -e open ls /home #timestamp
strace -c ls /home # statistics
strace -f -t -e trace=file systemctl restart nginx 2>&1 | grep open | cut -d'"' -f2
```

## Useful Alias to View System Processes

```bash
alias px='ps -eo ruser,pid,rss,vsz,pcpu,tty,args | grep -v grep | grep -e COMMAND -e'
```

## Show BIOS and Hardware Information

```bash
dmidecode
```

## Show Free Memory in Percent

```bash
MEM=($(free -t| grep ^Mem)) ;echo FreeMemPct: $(((${MEM[1]} - ${MEM[2]}) * 100 / ${MEM[1]} ))
free -t | awk '/Mem/{print ($2-$3) * 100.0 / $2}'
```

## Free Up Cache Memory

To free pagecache:
```bash
echo 1 > /proc/sys/vm/drop_caches
```
To free dentries and inodes:
```bash
echo 2 > /proc/sys/vm/drop_caches
```
To free pagecache, dentries and inodes:
```bash
echo 3 > /proc/sys/vm/drop_caches
```

## Manually Create Out of Memory Event (OOM)

```bash
swapoff -a
# 1.1 is the amount of memory to use
stress --vm-bytes $(awk '/MemAvailable/{printf "%d\n", $2 * 1.1;}' < /proc/meminfo)k --vm-keep -m 1
```

## Search Memory for Given Readable Strings

```bash
dd if=/dev/mem | cat | strings | grep xyz
```

## Mounting a Disk Image Containing Several Partitions

List partition table of image file:
```bash
fdisk -l disk.img
kpartx -l disk.img
```
Create devices:
```bash
kpartx -a -v disk.img
ls -all /dev/mapper/
```
Do what you need to do:
```bash
mount /dev/mapper/loopXXX /mnt/tmp -o loop
sleep 600
umount /mnt/tmp
```
Delete devices when work is done:
```bash
kpartx -d -v disk.img
ls -l /dev/mapper/
```

## Mount a Temporary RAM Partition

```bash
mount -t tmpfs tmpfs /mnt -o size=1024m
```

## cat top Output into a Text File

```bash
top -b -n1 > /tmp/top.txt
```

## sudo and ulimit

```bash
sudo bash -c 'ulimit -n 8192; sudo -u username ./startup-script'
# now its possible to use it with /etc/sudoers :)
```

## Disable requiretty on sudo for One User/Group

This is the cronjob which has to be run as monitoring user:
```bash
crontab -e -u monitoring
# */15 * * * * /usr/bin/sudo /bin/su -l oracle -c "/usr/local/mon/bin/oracle-check.sh oratbs DB01 APP" > /usr/local/mon/data/oracle-check.oratbs.DB01.APP.tmp
```
These are the sudo settings you need:
```bash
visudo
# Defaults:mon   !requiretty
# mon ALL=(ALL) NOPASSWD:/bin/su -l oracle -c /usr/local/mon/bin/oracle-check.sh DB01 APP
```

## sudo: Allow Single Command with Arg

```bash
mon ALL=(ALL) NOPASSWD:/usr/bin/sudo /usr/bin/nmap -O
```

## Detach Running Process So That You Can Logout

```bash
sleep 600
# <CTRL>+<Z>
# [1]+  Stopped                 sleep 600
bg
# [1]+ sleep 600 &
jobs
# [1]+  Running                 sleep 600 &
disown -r
# jobs
ps -ef | grep sleep
# root     29081 28991  0 13:23 pts/0    00:00:00 sleep 600
```

## Give Important System Message to TTY and Switch Display

```bash
clear >/dev/tty9
echo '
      ***************************************************
      *        SYSTEM WILL SHUT DOWN AT 19.30           *
      *                                                 *
      *        SAVE YOUR WORK AND EXIT NOW !!!          *
      ***************************************************' >/dev/tty9
chvt 9
sleep 5
chvt 7
```

## Bash Prompt Examples

For documentation:
```bash
export PS1='#\u;\h;\D{%Y.%m.%d %H:%M.%S};\w\n '
```
To mark important hosts:
```bash
export PS1='\e[0;45m \e[0;30m[\u@\h \w]\$ '
# or
export PS1="\[$(tput setaf 1)\]$PS1\[$(tput sgr0)\]"
```

## Find Procs Having Too Many Open Files

```bash
lsof +c15 > lsof.tmp
for i in $(cat lsof.tmp | cut -d' ' -f1 | sort -u ); do echo $i : $(cat lsof.tmp | grep "^$i " | wc -l); done | sort -n -t: -k2 | column -t | tail
rm -f lsof.tmp
```

## Get Memory Usage for Many Procs

```bash
ps -ylC php-fpm --sort:rss | awk '{sum+=$8; ++n} END {print "Tot="sum"("n")";print "Avg="sum"/"n"="sum/n/1024"MB"}'
```

## Generate Passwords

```bash
genpasswd() {
    local l=$1
    [ "$l" == "" ] && l=20
    tr -dc A-Za-z0-9_ < /dev/urandom | head -c ${l} | xargs
}
```

```bash
tr -dc 'A-NP-Za-np-z1-9.,;:+/()=?[]{}_-' < /dev/urandom | head -c16 | xargs
openssl rand -base64 24
```

## SELinux Handling

```bash
setenforce 0 # set permissive
semanage fcontext -l | grep /var/www
semanage fcontext -d -t httpd_sys_content_t "/data"
semanage fcontext -a -t httpd_sys_content_t "/data"
semanage fcontext -a -t httpd_sys_content_t "/data/www/([^/]*/)?www(/.*)?"
semanage fcontext -a -t httpd_config_t "/data/www/([^/]*/)?conf(/.*)?"
semanage fcontext -a -t httpd_log_t "/data/www/([^/]*/)?logs(/.*)?"
restorecon -Fr /data
ls -lZ /data
for i in $(rpm -ql policycoreutils | grep bin/ ); do man -k $(basename $i); done
semanage user -l httpd
systemctl restart httpd
sealert -a /var/log/secure
# fix if error
setenforce 1
sed -i 's/^SELINUX=.*/SELINUX=Enforcing/' /etc/selinux/config
grep ^SELINUX= /etc/selinux/config
getenforce
```

## SELinux Alerting

```bash
dnf -y install setroubleshoot-server setroubleshoot-plugins setroubleshoot-doc
```

**/etc/setroubleshoot/setroubleshoot.conf**
```ini
[email]
recipients_filepath = /var/lib/setroubleshoot/email_alert_recipients
smtp_port = 25
smtp_host = mail.domain.local
from_address = selinux@domain.local
subject = [DOMAIN] SELinux AVC Alert
```

**/var/lib/setroubleshoot/email_alert_recipients**
```
support@ict4u.li
```

```bash
service messagebus restart
```

## Bash Notes

Don't log duplicate entries in `.bash_history`:
```bash
echo 'HISTCONTROL=ignoreboth' >> $HOME/.bashrc
```

Set variables in variables:
```bash
X=horse
eval $X=23
echo $X : ${!X}
# horse : 23
```

Variables in functions:
```bash
var=hello 
foo () { echo "${!1}"; } 
foo var 
# hello
```

Work with arrays:
```bash
HOSTS=($(egrep -v '^#|^$' /etc/hosts | awk '{print $2}'))
for HOST in ${HOSTS[*]} ; do
   NR=$(($NR + 1))
   echo "   $NR)   $HOST"
done

echo -n "choose a host: " ; read DEST
echo "ssh ${HOSTS[$(($DEST -1))]}"
```

## Perform a Branching Conditional

```bash
true && { echo success;} || { echo failed; }
```

## Password Handling

Lock the account:
```bash
usermod -L <username>
```
Change the password expiration date to 0 to ensure the user changes the password during the next login:
```bash
chage -d 0 <username>
```
Unlock the account:
```bash
usermod -U <username>
```
Set password from within a script:
```bash
echo my-secret-password | passwd --stdin <username>
```
Create and update hashed password:
```bash
openssl passwd -6 -salt $(openssl rand -base64 12 | tr -d '=+/')
usermod --password '$6$X4ZzE06F0...134zFM0' myuser
```

## Backup/Restore Packages of Debian System

Nice command to clone and reset debian based systems.

### Backup

```bash
dpkg --get-selections > /etc/dpkg-list.txt
```

### Restore

```bash
/usr/bin/dpkg --clear-selections
/usr/bin/dpkg --set-selections < /etc/dpkg-list.txt
/usr/bin/dpkg --get-selections | sed -e 's/deinstall/purge/' > /tmp/dpkg-list.txt
/usr/bin/dpkg --set-selections < /tmp/dpkg-list.txt
rm -f /etc/dpkg-list.txt
/usr/bin/apt-get dselect-upgrade
```


## systemctl
* list all services
```bash
systemctl list-units --type service
```

* List failed services on boot 	
```bash
systemctl --failed
```

* show all running services
```bash
systemctl --all --state=running
```

* show detailed service status
```bash
systemctl status <svc-name>
```

* most common service handling
```bash
systemctl [start|stop|restart|status|enable|disable|mask] <svc-name>
```

* check if service is enabled to autostart after reboot
```bash
systemctl is-enabled <svc-name>
```