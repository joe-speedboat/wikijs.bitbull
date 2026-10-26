---
title: refcard
description: Foreman and Satellite Reference Card
published: true
date: 2026-10-26T14:11:44.662Z
tags: product, foreman, satellite
editor: markdown
dateCreated: 2026-02-13T09:07:21.403Z
---

# CLI
## Hammer
* Hammer Password location
```bash
vim $HOME/.hammer/cli.modules.d/foreman.yml
```

* Set all Repos to use "Download Policy" Immediate
```bash
for ID in $(hammer --csv repository list --per-page=1000 --fields Id | tail -n +2 | cut -d',' -f1)
do
  echo ID=$ID
  hammer repository update --id "$ID" --download-policy immediate
done
```

# Content
## Content Views
### Content View Filters
* Content > Lifecycle > Content Views > cv_rhel9 (your cv) > Tab: Filters > Create Filter
  * Name: EPEL_Zabbix_Exclude
  * Content type: RPM 
  * Type: Exclude Filter
  * Description: Never use Zabbix packages from epel repo: https://support.zabbix.com/si/jira.issueviews:issue-html/ZBX-21363/ZBX-21363.html
  * Create
* Add RPM Rule
  * RPM Name: zabbix*
  * keep other options as they are
* Apply to a Subset of Repositories (right top corner)
  * Add EPEL9 Repos
* Finally "Publish new Version" of your Content View
* Then verify on target systems
