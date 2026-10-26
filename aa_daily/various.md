---
title: various
description: This and that
published: true
date: 2026-10-26T14:11:34.911Z
tags: cmd, helpers
editor: markdown
dateCreated: 2026-02-13T09:07:11.509Z
---

## Create/Convert TOTP Token
Here is a **RAG/LLM-friendly, semantically explicit version** of your wiki entry. It adds intent, context, and normalization cues while staying compact and technical:

---

## Create / Convert TOTP Token

**Purpose:**
Generate and transform secrets for Time-based One-Time Password (TOTP) systems (e.g. RFC 6238 / Google Authenticator compatible).
TOTP secrets are typically shared in **Base32 encoding**, while some tools and APIs require **hexadecimal format**.

---

### Generate new secret

* **Base32-encoded secret (recommended for QR / authenticator apps):**

  ```bash
  openssl rand -base64 20 | base32 | tr -d '=' | head -c 32
  ```

  * Generates ~160-bit random secret
  * Encoded in Base32 (no padding) → compatible with most TOTP apps

* **Hex-encoded secret (raw binary representation):**

  ```bash
  openssl rand -hex 20
  ```

  * Same entropy, different encoding
  * Often used in configs, APIs, or lower-level tooling

---

### Convert between formats

* **Hex → Base32 (for use in authenticator apps):**

  ```bash
  echo "1e1e1e1e1e1e8e6fee8d7f3c1a2a4d9b0f5c6a3e" \
    | xxd -r -p \
    | base32 \
    | tr -d '='
  ```

  * Converts raw hex secret into TOTP-compatible Base32

* **Base32 → Hex (for storage / debugging / APIs):**

  ```bash
  echo SPKYT4JLGTOLATSHJHIX2F74YS35GUIL \
    | base32 --decode \
    | xxd -p \
    | tr -d '\n'
  ```

  * Decodes Base32 into raw bytes, then prints as hex

---

### context information

* Base32 is the **canonical representation for TOTP provisioning**
* Hex is a **transport/debug format**, not used directly by authenticator apps
* Padding (`=`) is commonly removed in TOTP secrets
* All transformations are **lossless encoding changes**, not cryptographic operations
* Ensure sufficient entropy (≥160 bits recommended)


## Crypt with GPG Symmetric Passphrase
```bash
gpg -c --pinentry-mode=loopback --no-symkey-cache some_file.tar.gz
gpg -d --pinentry-mode=loopback --no-symkey-cache -o some_file.tar.gz some_file.tar.gz.gpg
```

## Redirect Script Output Within the Script
```bash
#!/bin/bash
logfile=$$.log
exec > $logfile 2>&1
echo main script starts here
```

## Reduce PDF File Size
```bash
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4  -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf
```

## X11-Forwarding with sudo
In the meanwhile it's a given styandard to do your daily work rootless.
But sometimes you need to start an application as root.
This is how it works, tested with Rocky Linux 9
```bash
[chris@ws ~]$ ssh kvm.domain.tld -X -Y -C
[chris@kvm ~]$ sudo su -
[root@arjuna ~]# virt-manager 
(virt-manager:13408): Gtk-WARNING **: 06:49:10.610: cannot open display: 
# see, it cant find valid way to forward application window
[root@kvm ~]# export XAUTHORITY=/home/chris/.Xauthority # This does the trick
[root@kvm ~]# virt-manager 
# now it works
```

## Change Keyboard Layout on the Fly
- **For console:**
    ```bash
    loadkeys sg-latin1
    ```
- **For X11:**
    ```bash
    setxkbmap -layout ch
    ```

## CLI Clipboard Handling with X11
This is for use with pipes and stdout:
```bash
alias copyc='xclip -sel clip'
alias pastec='xclip -o -sel clip'
```

**Example:**
```bash
cat /etc/hosts | copyc
pastec > myhosts
```
It works with mouse as well :-)

## Paste Clipboard with Keyboard
This may be super useful for console connections into VMs:
```bash
sh -c 'sleep 0.5; xdotool type "$(xclip -o -selection clipboard)"'
```

## Set Terminal Tab Label Within Console to user@host
```bash
PROMPT_COMMAND='echo -ne "\033]0;$USER@$HOSTNAME\007"'
```

## Reassign Pipe Key from AltGr-1 to AltGr-7
```bash
xmodmap -e 'keycode 10 = 1 plus brokenbar exclamdown brokenbar exclamdown'
xmodmap -e 'keycode 16 = 7 slash bar seveneighths bar seveneighths'
```

## Change Screen Resolution to Work with Beamer
```bash
xrandr -s 1024x768 -r 60
```
or this:
```bash
# startup 2 head (Beamer + Laptop)
xrandr --output LVDS1 --mode 1024x768 --primary
# force use 1024x768 mode of the projector
xrandr --output VGA1 --mode 1024x768 --right-of LVDS1 || (xrandr --addmode VGA1 1024x768 && xrandr --output VGA1 --mode 1024x768 --right-of LVDS1)

# shutdown
xrandr --output VGA1 --off
xrandr --output LVDS1 --auto
```

## Bash Session Recording

- **Record the session:**
    ```bash
    script -t 2> demo.timing -a demo.session
    # Script started, file is demo.session
    echo do something
    exit
    # Script done, file is demo.session
    ```
- **Replay the session:**
    ```bash
    scriptreplay demo.timing demo.session
    ```
## MySQL Hints

- **Repair and optimize MySQL DB:**
    ```bash
    mysqlcheck -uroot -p@secret! -A -a -o -e -c -r --auto-repair
    ```
- **Copy MySQL DB to other host in one ssh command:**
    ```bash
    mysqldump --add-drop-table --extended-insert --force --log-error=error.log -uUSER -pPASS OLD_DB_NAME | ssh -C user@newhost "mysql -uUSER -pPASS NEW_DB_NAME"
    ```

## Delay Cron Job by Random Minutes to Spread Load

```bash
1 12 * * * /bin/sleep ${RANDOM:0:2}m ; /usr/local/sbin/update.sh
```

## Generate Monthly Calendar from Command Line
```bash
pcal -E -P a4 -B -F 1 -d /8 -t /18 -n /10 -a de -o cal.ps 2012
```