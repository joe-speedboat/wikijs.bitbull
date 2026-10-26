---
title: network
description: network related
published: true
date: 2026-10-26T14:11:28.918Z
tags: cmd, helpers, networking
editor: markdown
dateCreated: 2026-02-13T09:07:06.470Z
---

# settings

## Remember SSH Private Key Passphrase on Console
```bash
alias skey='ssh-agent > /tmp/.k ; . /tmp/.k ; rm -f /tmp/.k ; ssh-add'
```

## Private Key with Keychain in `.bashrc`
```bash
# SSH
keychain -Q -q ~/.ssh/id_dsa < /dev/null
[ -f $HOME/.keychain/$HOSTNAME-sh ] && source $HOME/.keychain/$HOSTNAME-sh

# GPG Keys
# gpg --list-keys
keychain --agents gpg 297E196D
[ -f $HOME/.keychain/$(uname -n)-sh-gpg ] && source $HOME/.keychain/$(uname -n)-sh-gpg
```

## Avoid Bash Auto Logout
### TMOUT Variable
* Logout message: timed out waiting for input: auto-logout
```bash
echo $TMOUT
man bash
# rpm -qf /etc/profile.d/tmout.sh
#   file /etc/profile.d/tmout.sh is not owned by any package
# cat /etc/profile.d/tmout.sh
#   # Set TMOUT to 900 per security requirements
#   TMOUT=900
```

### SSH Config
```bash
grep -B1 Alive /etc/ssh/ssh*_config
# /etc/ssh/ssh_config:Host *
# /etc/ssh/ssh_config:   ServerAliveInterval 60
# --
# /etc/ssh/sshd_config:ClientAliveInterval 60

fgrep -r Alive /etc/ssh/
```

## change description of SSH Private Key
- [StackOverflow: Rename SSH key agent that was already added](https://stackoverflow.com/questions/73676798/rename-ssh-key-agent-that-was-already-added)

```bash
ssh-keygen -c -C 'migration:rundeck@host' -f ssh/id_rsa_migration
# Enter passphrase:
# Old comment: rundeck@host
# Comment 'migration:rundeck@host' applied
```

## Change and verify SSH Private Key Passphrase
Its best practice to change passphrase of keys on a regular base.
This is how you can change and verify the passphrase.
```bash
[chris@xxx ~]$ ssh-keygen -p -f ~/.ssh/id_ed25519
Enter old passphrase: 
Key has comment 'chris@control.sun.bitbull.ch'
Enter new passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved with the new passphrase.

[chris@xxx ~]$ ssh-add -D
All identities removed.

[chris@xxx ~]$ ssh-add ~/.ssh/id_ed25519
Enter passphrase for /home/chris/.ssh/id_ed25519: 
Identity added: /home/chris/.ssh/id_ed25519 (chris@xxx.domain.tld)
```

## Keychain / Ansible SSH Private Keys
**Install keychain:**
```bash
dnf -y install keychain
```

**Add to `.bashrc`:**
```bash
keychain -Q -q ~/.ssh/id_rsa < /dev/null
[ -f $HOME/.keychain/$HOSTNAME-sh ] && source $HOME/.keychain/$HOSTNAME-sh
```

**Protect your SSH key:**
```bash
ssh-keygen -p -f .ssh/id_rsa
# Key has comment '.ssh/id_rsa'
# Enter new passphrase (empty for no passphrase): 
# Enter same passphrase again: 
# Your identification has been saved with the new passphrase.
```

**Log out and log in, it will ask for passphrase:**
```bash
exit
# ...login again...
# Enter passphrase for /home/ansible-adm/.ssh/id_rsa: 
```

**Add cronjobs that run ansible commands (login once after every reboot):**
```bash
crontab -e
# SHELL="/bin/bash"
# PATH=/usr/local/bin:/bin:/usr/bin:$HOME/bin
# * * * * * . $HOME/.bashrc; cd dep-adhoc ; ansible all -m ping >> cron.out 2>&1
```

**Check results:**
```bash
cat cron.out
# server1.example.com | SUCCESS => { "changed": false, "ping": "pong" }
# localhost | SUCCESS => { "changed": false, "ping": "pong" }
```

## Add CA Cert to Java Keystore
```bash
TMPF=/tmp/myca.crt
EP="directory01.sun.bitbull.ch:636"
echo -n | openssl s_client -connect $EP | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > $TMPF
openssl x509 -in $TMPF
keytool -import -alias idm -file $TMPF -keystore /etc/pki/ca-trust/extracted/java/cacerts -storepass changeit
```

## Set IP Address on the Fly
```bash
ip link set eth0 up
ip addr add 192.168.111.1/24 dev eth0
ip route add 192.168.33.1/32 dev eth0
ip route add default via 192.168.0.254 dev eth0
```

## Random MAC Address gen
```bash
printf 'DE:AD:BE:EF:%02X:%02X\n' $((RANDOM%256)) $((RANDOM%256))
date +%s | md5sum | sed 's/^\(..\)\(..\)\(..\)\(..\)\(..\).*$/02:\1:\2:\3:\4:\5/'
```

## Proxy Environment
- [GitLab: We need to talk: NO_PROXY](https://about.gitlab.com/blog/2021/01/27/we-need-to-talk-no-proxy/)

**In `$HOME/.bashrc`:**
```bash
export http_proxy=http://proxy.example.com:8080
export no_proxy=whole-domain-direct.com,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

**In `/etc/environment`:**
```bash
http_proxy=http://proxy.example.com:8080
no_proxy=whole-domain-direct.com,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

|                       | curl      | wget           | Ruby      | Python    | Go        |
| --------------------- | --------- | -------------- | --------- | --------- | --------- |
| no_proxy              | Yes       | Yes            | Yes       | Yes       | Yes       |
| NO_PROXY              | Yes       | No             | Yes       | Yes       | Yes       |
| Case precedence       | lowercase | lowercase only | lowercase | lowercase | Uppercase |
| Matches suffixes?     | Yes       | Yes            | Yes       | Yes       | Yes       |
| Strips leading .?     | Yes       | No             | Yes       | Yes       | No        |
| * matches all hosts?  | Yes       | No             | No        | Yes       | Yes       |
| Supports regexes?     | No        | No             | No        | No        | No        |
| Supports CIDR blocks? | No        | No             | Yes       | No        | Yes       |
| Detects loopback IPs? | No        | No             | No        | No        | Yes       |

# tasks
## mirror website
```bash
wget --random-wait -r -U Mozilla -e robots=off --span-hosts --domains miyuru.lk --convert-links https://www.miyuru.lk/geoiplegacy/
httrack "https://lab9.lab.domain.info/" -s0 -O "./" "+*.lab.domain.info/*" -v
```

**Verify added keys:**
```bash
ssh-add -l
```

## Server Current Directory by HTTP
```bash
python3 -m http.server
```


## Pipe tar via SSH
**Put data:**
```bash
cd /usr/local/stuff
tar cfz - . | ssh remote "cd /backup && tar xfz -"
```

**Get data:**
```bash
ssh remote "cd /usr/local/stuff && tar cf - ." | tar xfz -
```

## Pipe Disk Image via SSH
**Get data:**
```bash
ssh root@get-disk-from dd bs=8192 if=/dev/sda | dd bs=8192 of=/dev/vg01/backup_sda
```

**Put data:**
```bash
dd bs=8192 if=/dev/sda | ssh root@put-disc-to dd bs=8192 of=/dev/vg01/backup_sda
dd if=/dev/sda1 | buffer -s 64k -S 10m | ssh root@put-disk-to "cat > /dev/image"
dd if=/dev/sda1 bs=4M | lzop -c | ssh root@put-disk-to "lzop -dc | dd of=/dev/sda1 bs=4M"
```

## Escape Remote Console
**By telnet / Xen VM Console:**
```
Escape character is '^]'.
```
That means: `<CTRL> + <AltGr> + ]`

**Access iLO by SSH:**
```bash
ssh user@ilo-host
</>hpiLO-> remcons
# Starting remote console
# Press 'ESC (' to return to the CLI Session
```

**From Cyclades:**
```
~.
```

## Install Public Key to Remote
```bash
ssh-copy-id username@hostname
```

## Resume rsync of a Big File
```bash
rsync --partial --progress --rsh=ssh $file_source $user@$host:$destination_file
```

## Github PubKeys to `authorized_keys`
```bash
curl -s https://github.com/joe-speedboat.keys | while read key ; do 
   grep -q "$key" ~/.ssh/authorized_keys && echo "Key did exist: $key" || (echo "$key" >> ~/.ssh/authorized_keys ; echo "Key added: $key" )
done
```

## SSH Port Forwarding
### SSH Reverse Tunnel
**Build the SSH reverse tunnel:**
```bash
ssh -R 2222:localhost:22 middleuser@middle
ssh -N -f -R 2222:localhost:22 middleuser@middle
```

**Connect to the SSH reverse tunnel and jump to destination:**
```bash
ssh destinationuser@localhost -p2222
ssh destinationuser@middle -p 2222
```

### SSH Port Forwarding
```bash
ssh -g -L 80:127.0.0.1:3128 jump@zen.bitbull.ch -p23
ssh -g -L local_port:remote_host:remote_port user@dst_host -p23
# -g  Allows remote hosts to connect to local forwarded ports
# -L  [bind_address:]port:host:hostport
# -p  use different port for ssh connection
```

# diag
## Find Routing Decision
```bash
ip route show match 1.2.3.4
ip route get 1.2.3.4
```

## Get Host IP
```bash
hostname -i
```

## Validate Date of SSL Certificate
```bash
echo | openssl s_client -connect www.google.com:443 2>/dev/null | openssl x509 -dates -noout
```

**Quick SSL test function:**
```bash
ssl-test() { curl -kvv --max-time 2 https://$1 2>&1 | egrep 'issuer:|expire date:|start date:|subject:' ;}
ssl-test www.google.ch
# *  subject: C=US; ST=California; L=Mountain View; O=Google LLC; CN=*.google.ch
# *  start date: Jan  5 12:14:12 2021 GMT
# *  expire date: Mar 30 12:14:11 2021 GMT
# *  issuer: C=US; O=Google Trust Services; CN=GTS CA 1O1
```

## SSL/TLS Debugging
**Get all LISTEN ports and test for certificate details by web request:**
```bash
IF=$(ip r | grep default | awk '{print $5}')
IP=$(ip addr show $IF | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
lsof -i -P -n 2>/dev/null | grep LISTEN | grep -v 127.0.0.1 | awk '{print $9}' | cut -d: -f2 | sort -u | while read port 
do 
   echo "---------- https://$IP:$port "
   lsof -i -P -n 2>/dev/null | grep LISTEN | grep :$port 
   curl -m3 -k -vv https://$IP:$port 2>&1 | grep -A4 'Server certificate:'
done
```

## tcpdump
```bash
# Max. 100MB / full length and host x.x.x.x   
tcpdump -C 100 -w dump.dat -i eth0 -s 0 -XX udp port 514
tcpdump host client.example.com and port 80
tcpdump ip host bevo and bevo master
tcpdump ip and not net 127.0.0.0

# Print the start and end packets (the SYN and FIN packets) of each TCP conversation that involves a non-local host
tcpdump '(tcp[13] & 3 !=0 and not src and dst net localnet)'

# Print all ICMP packets that are not echo requests or replies (not ping packets)
tcpdump '(icmp[0] !=8 and icmp[0] !=0)'

# Dump traffic for later view in Wireshark
tcpdump -p -s0 -w tcpdump.cap

# Trace plain LDAP traffic
tcpdump -nvvvXAttt port 389 2>&1 | grep -B1 -A1 dc=
```

## Count Network Connections for Each Host
```bash
ss -ant state established | awk '{print $4}' | grep -v Address | awk -F: '{print $1}' | sort | uniq -c | sort
```

## List the Number and Type of Active Network Connections
```bash
ss -antH | awk '{print $1}' | sort | uniq -c
```

## nmap Network Discovery
**Find web servers on subnet:**
```bash
nmap -sS -T5 -P0 -p80 -oG - 192.168.1.1-254 | grep open
```

## Monitor Network Activity of Applications
```bash
while true; do
    date
    diff <(lsof -i) <(sleep 5; lsof -i)
done
```

## Show Your WAN IP
```bash
curl ifconfig.me
```

## Scan Open Outgoing Ports
```bash
for i in {1..1024}; do wget -qO- -T0.5 -t1 portquiz.net:$i >/dev/null 2>&1 && echo $i open ; done
```

## curl WebDAV Examples
- **Reading Files/Folders on WebDAV Server:**
  ```bash
  curl 'https://example.com/webdav'
  ```
- **Deleting Files/Folders on WebDAV Server:**
  ```bash
  curl -X DELETE 'https://example.com/webdav/test'
  curl -X DELETE 'https://example.com/webdav/test.txt'
  ```
- **Renaming File on WebDAV Server:**
  ```bash
  curl -X MOVE --header 'Destination:http://example.org/new.txt' 'https://example.com/old.txt'
  ```
- **Creating New Folder on WebDAV Server:**
  ```bash
  curl -X MKCOL 'https://example.com/new_folder'
  ```
- **Uploading File on WebDAV Server:**
  ```bash
  curl -T '/path/to/local/file.txt' 'https://example.com/test/'
  ```
- **CURL Options:**
  - Username/Password:
    ```bash
    curl --user 'user:pass' 'https://example.com'
    ```
  - HTTP Authentication:
    ```bash
    curl --user 'user:pass' 'https://example.com' --basic
    curl --user 'user:pass' 'https://example.com' --digest
    ```
  - Let curl decide the authentication:
    ```bash
    curl --user 'user:pass' 'https://example.com' --anyauth
    ```
  - Get Response Code:
    ```bash
    curl --user 'user:pass' -X DELETE 'https://example.com/test' -sw '%{http_code}'
    ```

## Curl SOAP
soap.txt is a local text file with the soap request in it
```bash
curl -H "Content-Type: text/xml; charset=utf-8" \
     -H "SOAPAction:" \
     -d @soap.txt \
     -X POST http://localhost:18181/httpWSDLService/httpWSDLPort
```

## Use netcat (nc) for Port Check
```bash
nc -vvn -z 10.202.3.40 80 # old syntax
nc -w3 -i3 --recv-only $DSL_IP $DSL_PORT 2>/dev/null | grep -q Login: # new syntax
```

## Port Checker Function
```bash
check_port() {
  if [[ $# -ne 2 ]]; then
    echo "Usage: check_port <HOST> <PORT>"
    echo "Example: check_port 127.0.0.1 22"
    return 1
  else
    local host=$1
    local port=$2
    (echo > "/dev/tcp/$host/$port") >/dev/null 2>&1 && echo "$host,$port,open" || echo "$host,$port,closed"
  fi
}
```
## Blink NIC LED
```bash
NIC=$(ip route show default 0.0.0.0/0 | awk '{print $5; exit}')
END=$((SECONDS+300))
while [ $SECONDS -lt $END ]; do
    ip link set $NIC down
    sleep 2
    ip link set $NIC up
    sleep 2
done
```


