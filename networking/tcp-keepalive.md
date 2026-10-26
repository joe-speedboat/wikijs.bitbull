---
title: TCP keepalive by kernel
description: How to configure linux to keep tcp connections
published: true
date: 2026-10-26T14:12:06.080Z
tags: networking, linux, keepalive
editor: markdown
dateCreated: 2026-02-15T07:21:31.146Z
---

Anyone who occasionally works via VPN has probably noticed that SSH connections drop as soon as you don’t do anything for 2 minutes.

By chance, I found these funny kernel parameters. They periodically check whether a TCP connection is still valid, and if not, it gets discarded. This traffic generation is perfectly suited to prevent connection timeouts of any kind.

`/etc/sysctl.conf`
```
net.ipv4.tcp_keepalive_time = 30
net.ipv4.tcp_keepalive_intvl = 25
```

```
sysctl -p
```

This loads the parameters into the kernel.  
At boot time, this is automatically executed.
For the curious (`man 7 tcp`)

```
tcp_keepalive_intvl
       The number of seconds between TCP keep-alive probes. The default value is 75 seconds.

tcp_keepalive_probes
       The maximum number of TCP keep-alive probes to send before giving up and killing the connection if
       no response is obtained from the other end. The default value is 9.

tcp_keepalive_time
       The number of seconds a connection needs to be idle before TCP begins sending out keep-alive
       probes. Keep-alives are only sent when the SO_KEEPALIVE socket option is enabled. The default
       value is 7200 seconds (2 hours). An idle connection is terminated after approximately an addi-
       tional 11 minutes (9 probes an interval of 75 seconds apart) when keep-alive is enabled.

       Note that underlying connection tracking mechanisms and application timeouts may be much shorter.
```
