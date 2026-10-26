---
title: Welcome
description: Welcome
published: true
date: 2026-10-26T11:00:59.077Z
tags: 
editor: markdown
dateCreated: 2026-02-13T09:06:58.094Z
---

<img src="/pics/che.png"
     style="float:right;width:512px;margin:0 0 0px 0px;" />
     <br><br><br><br><br><br><br><br>
# Bucket List
* [https://wiki.app.tuxmint.com/en/Overleaf-LaTeX](https://wiki.app.tuxmint.com/en/Overleaf-LaTeX)
* [OpenTelemetry - Getting Started](https://opentelemetry.io/docs/getting-started/ops/)
* ✅ [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install/linux-install)
* [Event Foto Sharing](https://github.com/Memtly)
* ✅ [Paperless Document Management](https://docs.paperless-ngx.com/)
* [OPA & Gatekeeper](https://open-policy-agent.github.io/gatekeeper/website/docs/)
* [Istio & Kiali](https://istio.io/latest/docs/ops/integrations/kiali/)
* [ArgoCD best practice and hands on](https://argo-cd.readthedocs.io/en/stable/)
* [OWASP Kubernetes Top 10](https://kubernetes-top10.owasp.org/)

# Quick and Dirty
```bash
# install ansible
curl -L ansible.bitbull.ch | bash

# cleanup rhel and ubuntu templates
curl -L sysprep.bitbull.ch | bash
```
     
     
# Welcome
Welcome to my Open Source Wiki, it's a place for knowledge, hacking and sharing useful information.
Content is focused on business and lean usage of Linux and Open Source applications.

The archive of old Mediawiki pages can be found here: [https://github.com/joe-speedboat/archive.mediawiki](https://github.com/joe-speedboat/archive.mediawiki)

# My Resources
* [Script Archive](https://github.com/joe-speedboat/scripts)
* [GitHub](https://github.com/joe-speedboat)
* [Kubernetes Apps and hints](https://github.com/joe-speedboat?tab=repositories&q=kube)
* [Ansible Galaxy](https://galaxy.ansible.com/ui/standalone/namespaces/3440/)

# Interesting stuff
* [Radxa Dragon Q6A - Single board computer based on Qualcom QCS6490](https://radxa.com/products/dragon/q6a/)
  * Fedora Install to NVMe (boot into SDCard with t4 image)
    ```bash
    smartctl --all /dev/nvme0n1
    nvme format --ses=1 /dev/nvme0n1
    curl -L https://mirror.iscas.ac.cn/fedora-riscv/releases/42/Spins/aarch64/images/QCS6490/Radxa-Dragon-Q6A/Fedora-GNOME-42-20251017000000.QCS6490.Radxa-Dragon-Q6A.raw.gz | gzip -d | sudo dd of=/dev/nvme0n1 bs=4M status=progress conv=fsync oflag=sync
    fstrim -av
    ```
* [Personal onpremise AI assistant](https://openclaw.ai/)
* [AI Workflow Automation Platform & Tools](https://n8n.io/)
* [Ollama is the easiest way to automate your work using open models onprem](https://ollama.com/)
* [Rundeck is the orchestration tool for all of your existing automation](https://www.rundeck.com/)
* [Ascender provides a web-based user interface, REST API, and task engine for Ansible](https://github.com/ctrliq/ascender)
* [FreeIPA Workshop](https://github.com/freeipa/freeipa/tree/master/doc/workshop)


# Disclaimer and License Notice

All content published in this Linux wiki is released under the terms of the **GNU General Public License v3.0 (GPLv3)** unless explicitly stated otherwise.

You are free to use, modify, and redistribute the content in accordance with the provisions of the GPLv3. A copy of the license should be provided alongside any redistribution. If not included, it can be obtained from: https://www.gnu.org/licenses/gpl-3.0.html

All information, configurations, scripts, commands, and how-to guides provided in this wiki are supplied **“as is”**, without warranty of any kind, express or implied. This includes, but is not limited to, accuracy or completeness of the information, fitness for a particular purpose, suitability for production environments, and absence of errors or omissions.

If you choose to use, apply, execute, implement, or otherwise rely on any commands, configurations, scripts, or procedures described here, you do so entirely at your own risk.

Under no circumstances shall the author(s) or contributor(s) be held liable for data loss, service interruptions, security breaches, hardware or software damage, financial losses, or any direct, indirect, incidental, or consequential damages resulting from the use or misuse of the content provided.

It is your responsibility to validate all commands and configurations before applying them, test changes in a controlled environment, maintain proper backups, and comply with applicable laws and organizational policies.

If you do not agree with these terms, do not use the content provided here. 
