---
title: proxy.pac example
description: Useful example rules of proxy.pac configuration file
published: true
date: 2026-10-26T14:12:00.985Z
tags: networking, proxy
editor: markdown
dateCreated: 2026-02-15T06:17:04.081Z
---

This is a simple and fast way to configure webbrowsers
for difficult settings of internet acces per domain or ip

```
function FindProxyForURL(url, host)
{
var proxy_priv = "PROXY 127.0.0.1:8080";
var proxy_work = "PROXY 127.0.0.1:3128";
var proxy_no = "DIRECT";
if (shExpMatch(url, "https://key.work.com*")) { return proxy_work; }
if (shExpMatch(url, "https://*mon.work.com*")) { return proxy_work; }
if (shExpMatch(url, "http://*intranet.work.com*")) { return proxy_work; }
if (shExpMatch(url, "http://192.168.103.73*")) { return proxy_work; }
if (shExpMatch(url, "http://*mydomain.ch*")) { return proxy_priv; }
if (shExpMatch(url, "https://*mydomain.ch*")) { return proxy_priv; }
// Proxy anything else
return proxy_no;
}
```

you don't need a running webserver to provide this file,
simply use something like this in your browser settings:
 `file:///home/frog/doc/proxy.pac`