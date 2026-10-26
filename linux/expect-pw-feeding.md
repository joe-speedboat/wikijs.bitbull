---
title: Expect examples
description: Feed passwords and commands with Expect
published: true
date: 2026-10-26T14:11:56.222Z
tags: linux, expect
editor: markdown
dateCreated: 2026-02-15T05:52:13.129Z
---

It's a bad thing, but sometimes you can't avoid passing passwords with a script.

Here are two scripts to start a command of another user using expect:
The password is hardcoded here (that's really really bad :)
```bash
#!/usr/bin/expect
set password "geheimgeheim"
spawn /bin/su - test-user -c "cat testfile"
expect "Password:"
send "$password\r"
expect eof
```
The password is passed as a parameter ($1) to the script (this is also bad :)
```bash
#!/usr/bin/expect
set password [lindex $argv 1]
spawn /bin/su - test-user -c "cat testfile"
expect "Password:"
send "$password\r"
expect eof
```

If the expect script is part of a bash script, you can wrap the whole thing in a bash script like this:
```bash
#!/bin/bash
date
echo ' #!/usr/bin/expect
set password [lindex $argv 1]
spawn /bin/su - test-user -c "cat testfile"
expect "Password:"
send "$password\r"
expect eof ' | /usr/bin/expect
date
```

Here is a small script for telnet:
```bash
#!/usr/bin/expect
set user "admin"
set password "geheim"
spawn telnet router-ip
expect "login:"
send "$user\r"
expect "Password:"
send "$password\r"
expect "Last"
spawn reboot
expect eof
```

With sudo, password prompt, and all in nice... this is how you do it:
```bash
#!/usr/bin/expect -f
set timeout 30
set env(TERM)
set server [lindex $argv 0]
set user [lindex $argv 1]
set cmd [lindex $argv 2]
set sudo [lindex $argv 3]
set prompt "\[.*\@.* .*\]\$"

spawn ssh $user@$server
expect {
   "(yes/no)? " {
      send "yes\r"
      expect {
         "assword: " {
            interact -nobuffer -re "(.*)\r" return
            }
         "$prompt" {}
         }
      }
   "assword: " {
      interact -nobuffer -re "(.*)\r" return
      }
   "$prompt" { }
   }

if { $sudo == "1" } {
   send "sudo su -\r"
   expect "$prompt"
   send "$cmd\r"
   }
if { $sudo == "" || $sudo == "0" } {
   send "$cmd\r"
   }
sleep 0.2
expect "$prompt" { send "exit\r" }
```

Configuration of a Cisco router for reading, e.g., for backup:
```bash
#!/usr/bin/expect
set user "admin"
set password "secret!"
spawn telnet 10.0.0.20
expect "name:"
send "$user\r"
expect "word:"
send "$password\r"
expect "*#"
send "ter len 0\r"
expect "*#"
send "show run\r"
expect "*#"
send "exit\r"
```
