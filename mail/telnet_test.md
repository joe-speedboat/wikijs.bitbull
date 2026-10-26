---
title: SMTP + IMAP via telnet
description: Useful commands for mail testing
published: true
date: 2026-10-26T14:11:57.751Z
tags: mail
editor: markdown
dateCreated: 2026-02-15T06:00:50.911Z
---

## SMTP
```
[jump@zen ~]$ telnet mail.bitbull.ch 25
  Trying 82.220.2.26...
  Connected to mail.bitbull.ch.
  Escape character is '^]'.
  220 never eat yellow snow...
ehlo domain.com
  250-prometueus.bitbull.ch
  250-PIPELINING
  250-SIZE 10240000
  250-ETRN
  250-AUTH CRAM-MD5 LOGIN DIGEST-MD5 PLAIN
  250-AUTH=CRAM-MD5 LOGIN DIGEST-MD5 PLAIN
  250 8BITMIME
mail from:admin@domain.com
  250 Ok
rcpt to: chris@bitbull.ch
  250 Ok
data
  354 End data with <CR><LF>.<CR><LF>
Subject: test title
here is the body of the mail
.
  250 Ok: queued as 6B9054C0CE
quit
  221 Bye
  Connection closed by foreign host.
```
| Your Input                  | Meaning |
|------------------------------|---------|
| HELO Test                    | You identify yourself to the mail server using HELO. The server will respond with `250 OK` or a similar status message. |
| MAIL FROM:user@company.tld   | You specify the envelope sender address (MAIL FROM). This address can technically be spoofed. For testing, you may use your own email address. The receiving server must acknowledge with a 2xx status code. |
| RCPT TO:recipient@example.tld| You specify the valid recipient address where the message should be delivered. The mail server uses this information for routing. The server must confirm with a 2xx status code. |
| DATA                         | You indicate that the SMTP envelope is complete and that you will now send the message content (headers and body). The server responds with a 2xx or `354 Start mail input` status. |
| To: Testuser1                | Message header: logical recipient shown in the email client. |
| From: Testuser2              | Message header: logical sender shown in the email client (independent from MAIL FROM). |
| Subject: Testmail            | Message header: defines the email subject. |
| (empty line)                 | A blank line separates the message headers from the message body. |
| Test                         | Message body content. |
| .                            | A single dot on a new line terminates the DATA section and signals the end of the message content. The server should acknowledge acceptance with a 2xx status code. |
| QUIT                         | Terminates the SMTP session politely. |


## POP3
```
telnet pop.domain.com pop3
  +OK Hello there.
user user@domain.net
  +OK Password required.
pass secret
  +OK
list
  1 1586
  2 13304
  3 795
.
dele 2
  +OK
quit
  Connection closed by foreign host
```

## IMAP
```
telnet imap.example.com imap
  Escape character is ']'.
  OK Courier-IMAP ready. Copyright 1998-2002 Double Precision, Inc. See COPYING for distribution information.
login user@example.com secret
  OK LOGIN Ok.
  A0001 CAPABILITY
  CAPABILITY IMAP4rev1 CHILDREN NAMESPACE THREAD=ORDEREDSUBJECT THREAD=REFERENCES SORT QUOTA
logout
  BYE Courier-IMAP server shutting down
  OK LOGOUT completed
``