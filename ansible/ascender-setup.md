---
title: Ascender Setup
description: Setup Ascender (AWX) on Rocky Linux 10
published: true
date: 2026-10-26T14:12:24.110Z
tags: ansible, awx, ascender, kubernetes
editor: markdown
dateCreated: 2026-02-15T15:06:49.959Z
---

Ascender provides a web-based user interface, REST API, and task engine built on top of Ansible. It is based off the upstream project of AWX.

# Prerequisites
* Kubernetes admin knowledge
  * understand CRDs
* Understand operator concept
* Ansible admin knowledge
* Understand git

# VM Setup

## VM requirements
Just setup a Rocky Linux 9 minimal VM with the following requirements
* CPU: 2
* MEM: 8GB (6 GB may work as well)
* DISK: 40G (7GB used on a fresh setup)

## Prepare OS
```bash
dnf -y upgrade
dnf -y install setroubleshoot-server curl lsof wget git bash-completion openssl

sed -i  '/swap/d' /etc/fstab
swapoff -a

systemctl enable firewalld --now
firewall-cmd --permanent --zone=public --add-service=https
# firewall-cmd --zone=public --add-masquerade --permanent
firewall-cmd --reload
reboot
```



# Setup K3S
```bash
curl -sfL https://get.k3s.io | sh

cat /etc/systemd/system/k3s.service
systemctl status k3s

kubectl get nodes
# all pods in running state? fine!
kubectl get pods --all-namespaces
```

# Setup Ascender
```bash
APP_FQDN=$(hostname -f)

cd
mkdir git
cd git

openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes -subj "/C=CH/ST=SG/L=StGall/O=BITBULL/OU=IT/CN=$APP_FQDN"

git clone https://github.com/ctrliq/ascender-install.git

cd ascender-install

# we skip the installer config cmd, we already have our settings
# bash config_vars.sh

# VERIFY VERSIONS AND VARS, OR JUST USE `config_vars.sh`
echo '---
k8s_platform: k3s
kube_install: false
k8s_offline: false
download_kubeconfig: true
k8s_lb_protocol: https
k3s_master_node_ip: "127.0.0.1"
use_etc_hosts: false
tls_crt_path: "~/git/cert.pem"
tls_key_path: "~/git/key.pem"
tmp_dir: "{{ playbook_dir}}/../ascender_install_artifacts"
ASCENDER_HOSTNAME: awx.sun.bitbull.ch
ASCENDER_NAMESPACE: ascender
ASCENDER_ADMIN_USER: admin
ASCENDER_ADMIN_PASSWORD: "ChangeMeNow."
ASCENDER_VERSION: 25.3.4       
ANSIBLE_OPERATOR_VERSION: 2.19.3
ascender_garbage_collect_secrets: false
ascender_replicas: 1
image_pull_policy: Always
ascender_setup_playbooks: false
LEDGER_INSTALL: false' > custom.config.yml

sed -i "s/ASCENDER_HOSTNAME:.*/ASCENDER_HOSTNAME: $APP_FQDN/" custom.config.yml
bash ./setup.sh
```
* Finaly: Test Login

# Upgrade Ascender
```bash
cd                              
cd git/ascender-install     
git pull
test -f custom.config.yml.setup || cp -av custom.config.yml custom.config.yml.setup
```
```bash
ASCENDER_VERSION=25.2.0         
sed -i 's/kube_install:.*/kube_install: false/' custom.config.yml
sed -i 's/download_kubeconfig: .*/download_kubeconfig: false/' custom.config.yml
sed -i "s/ASCENDER_VERSION:.*/ASCENDER_VERSION: $ASCENDER_VERSION/" custom.config.yml         
sed -i 's/image_pull_policy:.*/image_pull_policy: Always/' custom.config.yml
                                
diff custom.config.yml custom.config.yml.setup
bash ./setup.sh                 
```


# Notes (untested)
## Backup

* `vim awx-backup.yml`
```
---
apiVersion: awx.ansible.com/v1beta1
kind: AWXBackup
metadata:
  name: awxbackup-20220311
  namespace: ascender
spec:
  deployment_name: ascender
...
```

`kubectl apply -f awx-backup.yml`

`kubectl get awxbackups awxbackup-20220311 -o yaml`
```
apiVersion: awx.ansible.com/v1beta1
kind: AWXBackup
...
name: awxbackup-20220311
...
status:
  backupClaim: awx-backup-claim
  backupDirectory: /backups/awx-backup-2022-03-11-05:45:56
  conditions:
  - lastTransitionTime: "2022-03-11T05:45:07Z"
    reason: Successful
    status: "True"
    type: Running
```

* Keep that as well for DR reason
`kubectl get awxbackups awxbackup-20220311 -o yaml > awxbackup-20220311.yml`

```
ll awx-backup-2022-03-11-05\:45\:56/
total 13072
-rw-r--r--. 1 1000680000 root      600 Mar 11 06:46 awx_object
-rw-r--r--. 1 1000680000 root      670 Mar 11 06:46 secrets.yml
-rw-------. 1 1000680000 root 13377441 Mar 11 06:46 tower.db
```

## Restore
`vim awx-restore.yml`
```
---
apiVersion: awx.ansible.com/v1beta1
kind: AWXRestore
metadata:
  name: awxrestore-20230221
  namespace: ascender
spec:
  deployment_name: ascender
  backup_pvc_namespace: ascender
  backup_dir: /backups/awx-backup-2023-02-20-17:04:58
  backup_pvc: awx-backup-claim
...
```
`kubectl apply -f ascender-restore.yml`

`kubectl get awxrestores -o yaml`



