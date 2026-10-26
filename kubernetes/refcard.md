---
title: refcard
description: Daily commands that make your life easier
published: true
date: 2026-10-26T14:12:25.781Z
tags: helpers, kubernetes
editor: markdown
dateCreated: 2026-02-17T17:11:22.686Z
---

# k3s
## setup
### prepare os
```bash
dnf -y upgrade
dnf -y install setroubleshoot-server curl lsof wget tar vim git bash-completion

sed -i  '/swap/d' /etc/fstab
swapoff -a
dnf -y upgrade
reboot
```

### install k3s
```bash
curl -sfL https://get.k3s.io | sh
grep 'kubectl completion bash' $HOME/.bashrc || echo 'source <(kubectl completion bash)' >> $HOME/.bashrc
```

## helpers
### helm
```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | sh
helm completion bash > /etc/bash_completion.d/helm
```

### kustomize
```bash
sudo 'cd /usr/local/bin ; curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash'
```
### kubectl-neat
```bash
cd /usr/local/bin
rm -f kubectl-neat
wget https://github.com/itaysk/kubectl-neat/releases/latest/download/kubectl-neat_linux_amd64.tar.gz
chmod 700 kubectl-neat
tar vxfz kubectl-neat_linux_amd64.tar.gz
rm -f LICENSE kubectl-neat_linux_amd64.tar.gz
```

## velero
```bash
tar -xvf velero-v1.17.2-linux-amd64.tar.gz
sudo mv velero-v1.17.2-linux-amd64/velero /usr/local/bin/
velero version
```
### velero example
* create/rent s3 bucket
* `vi credentials-velero` (src+target) 
```
[default]
aws_access_key_id = XXXXXXXXXXXXXXXXXXXXXXX
aws_secret_access_key = YYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
```

* install velero (src+target)
```bash
bucket=velero-transfer
s3=s3.service.com
velero install   --provider aws   --plugins velero/velero-plugin-for-aws:latest \
  --bucket $bucket   --secret-file ./credentials-velero  \
  --backup-location-config region=eu-central-1,s3ForcePathStyle="true",s3Url=https://$s3 \
  --use-node-agent   --default-volumes-to-fs-backup   --use-volume-snapshots=false
```

* create backup on source into s3 bucket
```bash
velero backup create wiki-backup   --include-namespaces wiki   --default-volumes-to-fs-backup   --wait
```
* restore backup in destination from s3 bucket
```bash
velero restore create --from-backup wiki-pv-full2 --wait
```

### Velero scheduled backup
Short how-to for creating namespace-specific Velero backup schedules.

#### Current Backup Status

Existing manual backup:

```bash
velero backup get
````

```text
NAME           STATUS      ERRORS   WARNINGS   CREATED                          EXPIRES   STORAGE LOCATION   SELECTOR
vikunja-snap   Completed   0        0          2026-05-01 09:47:30 +0200 CEST   29d       default            <none>
```

#### Create Scheduled Backups

##### Example: daily 185d

Daily backup at **19:00**, retention **185 days**.

```bash
velero schedule create vaultwarden-daily-185d \
  --schedule="0 19 * * *" \
  --include-namespaces vaultwarden \
  --default-volumes-to-fs-backup \
  --ttl=4440h0m0s
```

##### Example: 4 times a day, keep 30d 

Backup at **09:00, 12:00, 15:00, and 18:00**, retention **30 days**.

```bash
velero schedule create n8n-four-times-daily-30d \
  --schedule="0 9,12,15,18 * * *" \
  --include-namespaces n8n \
  --default-volumes-to-fs-backup \
  --ttl=720h0m0s
```

##### Verify Schedules

```bash
velero schedule get
```

Expected result:

```text
NAME                       STATUS    SCHEDULE             BACKUP TTL   LAST BACKUP   SELECTOR   PAUSED
n8n-four-times-daily-30d   Enabled   0 9,12,15,18 * * *   720h0m0s     n/a           <none>     false
vaultwarden-daily-185d     Enabled   0 19 * * *           4440h0m0s    n/a           <none>     false
```

##### Notes

* Each schedule backs up only one namespace.
* `--include-namespaces` defines the namespace included in the scheduled backup.
* `--default-volumes-to-fs-backup` enables Velero file-system backup for persistent volumes.
* `--ttl` defines retention:

  * `720h0m0s` = 30 days
  * `4440h0m0s` = 185 days

### headlamp (admin ui)
* Install
```bash
kubectl config set-context --current --namespace kube-system
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/headlamp/main/kubernetes-headlamp.yaml

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: headlamp
  namespace: kube-system
spec:
  ingressClassName: traefik
  rules:
  - host: admin.domain.tld
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: headlamp
            port:
              number: 80
EOF
```
* Create creds to access the ui
```bash
kubectl -n kube-system create serviceaccount headlamp-admin
kubectl create clusterrolebinding headlamp-admin --serviceaccount=kube-system:headlamp-admin --clusterrole=cluster-admin
kubectl -n kube-system create token headlamp-admin --duration=8760h   # ~1 year
```

# applications
## postgresql
### setup
```bash
cd ; mkdir git ; cd git
git clone https://github.com/joe-speedboat/kube.postgresql.git
cd kube.postgresql
bash deploy_postgresql.sh
```
### login
```bash
PGPASSWORD="$POSTGRES_PASSWORD" \
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

## mariadb
### setup
```bash
cd ; mkdir git ; cd git
git clone https://github.com/joe-speedboat/kube.mariadb.git
cd kube.mariadb
bash deploy_mariadb.sh
```
### login (MYSQL vars)
```bash
mariadb \
  -h 127.0.0.1 \
  -u "$MYSQL_USER" \
  -p"$MYSQL_PASSWORD" \
  "$MYSQL_DATABASE"
```

### login (MARIADB vars)
```bash
mariadb \
  -h 127.0.0.1 \
  -u "$MARIADB_USER" \
  -p"$MARIADB_PASSWORD" \
  "$MARIADB_DATABASE"
```

# Troubleshoot/Fix
## Fact gathering
### CPU and Memory overview
```bash
kubectl top pods -A --no-headers |
awk '{print $1, $2, $3}' |
while read -r ns pod usage; do
  request=$(
    kubectl get pod -n "$ns" "$pod" -o json |
    jq -r '
      def millicpu:
        if . == null or . == "" then 0
        elif test("m$") then sub("m$"; "") | tonumber
        else tonumber * 1000
        end;
      [.spec.containers[].resources.requests.cpu | millicpu] | add
    '
  )
  printf "%-20s %-55s request=%5sm usage=%s\n" \
    "$ns" "$pod" "$request" "$usage"
done |
sort -k3 -nr
```

## cleanup
### Remove pods that refuse to terminate
```bash
kubectl get pods -n kube-system | awk '/Terminating/ {print $1}' | \
  xargs -r kubectl delete pod -n kube-system --grace-period=0 --force
```