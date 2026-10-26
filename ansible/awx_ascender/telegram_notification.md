---
title: AWX Telegram notification
description: AWX Ascender Telegram notification howto
published: true
date: 2026-10-26T14:12:18.983Z
tags: awx, ascender, telegram, notification
editor: markdown
dateCreated: 2026-02-15T08:16:19.229Z
---

# AWX Telegram Notification

With notification plugins, you can get information about what your AWX/Ansible Tower is up to.

# Setup

* AWX > Notification > Add
  * Name: Telegram
  * Notification Type: Webhook
  * Target URL:

```
https://api.telegram.org/bot<INSERT_AUTH_TOKEN_HERE>/sendMessage
```

  * HTTP Method:

```
POST
```

  * HTTP Headers:

```
{"Content-Type":"application/json"}
```

  * Start/Success/Error message body

```
{
    "chat_id": "<INSERT_CHAT_ID_HERE>",
    "text": "BITBULL AWX Job Notification\nName: {{ job.name }}\nstarted: {{ job.started }}\nstatus: {{ job.status }}\nurl: {{ url }}\n"
}
```

  * Workflow approved message body

```
{
    "chat_id": "<INSERT_CHAT_ID_HERE>",
    "text": "BITBULL AWX Notification\nThe approval node \"{{ approval_node_name }}\" was approved. {{ workflow_url }}"
}
```

  * Workflow denied message body

```
{
    "chat_id": "<INSERT_CHAT_ID_HERE>",
    "text": "BITBULL AWX Notification\nThe approval node \"{{ approval_node_name }}\" was denied. {{ workflow_url }}"
}
```

  * Workflow pending message body

```
{
    "chat_id": "<INSERT_CHAT_ID_HERE>",
    "text": "BITBULL AWX Notification\nThe approval node \"{{ approval_node_name }}\" needs review. This node can be viewed at: {{ workflow_url }}"
}
```

  * Workflow timed out message body

```
{
    "chat_id": "<INSERT_CHAT_ID_HERE>",
    "text": "BITBULL AWX Notification\nName: \"The approval node \\\"{{ approval_node_name }}\\\" has timed out. {{ workflow_url }}"
}
```
