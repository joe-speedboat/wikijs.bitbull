---
title: RustFS: Install and Upgrade
description: Install, Configure and Upgrade RustFS on k3s
published: true
date: 2026-10-26T14:13:41.307Z
tags: kubernetes, s3, rustfs
editor: markdown
dateCreated: 2026-06-30T12:28:48.906Z
---

---
title: RustFS: Install and Upgrade
description: Install, Configure and Upgrade RustFS on k3s
published: true
date: 2026-09-02T17:40:28.981Z
tags: kubernetes, s3, rustfs
editor: markdown
dateCreated: 2026-06-30T12:28:48.906Z
---

# RustFS on k3s: Setup, Operations, and Upgrade Runbook

## Placeholder Values

Production hostnames and IP addresses have been replaced with neutral documentation placeholders.

| Purpose             | Placeholder                  |
| ------------------- | ---------------------------- |
| Kubernetes host     | `k3s-node.example.net`       |
| S3/API endpoint     | `rustfs.example.net`         |
| Browser console     | `rustfs-console.example.net` |
| External Ingress IP | `203.0.113.10`               |
| Administrative user | `admin`                      |

## Purpose

This article documents the RustFS deployment on a single-node k3s cluster.

It is intended as an operational runbook for managing the service later, including:

* checking service health
* retrieving credentials
* changing configuration
* upgrading the Helm release
* re-applying the console Ingress
* troubleshooting common issues

RustFS provides an S3-compatible object storage endpoint with a separate browser console.

## Current Service Endpoints

| Service               | URL                                                                                    |
| --------------------- | -------------------------------------------------------------------------------------- |
| S3/API endpoint       | `https://rustfs.example.net`                                                           |
| Browser console       | `https://rustfs-console.example.net/rustfs/console/`                                   |
| Console root redirect | `https://rustfs-console.example.net/` redirects browser requests to `/rustfs/console/` |

The public API endpoint serves the S3-compatible API.

A plain unauthenticated `GET /` or `HEAD /` request may return XML errors such as `AccessDenied` or `NotImplemented`. This is expected behavior for an S3 endpoint.

Use `/health` for unauthenticated service health checks.

## Architecture

The deployment is intentionally simple because the cluster is a single-node k3s host.

| Component                        | Value                                                                                                          |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Kubernetes host                  | `k3s-node.example.net`                                                                                         |
| Kubernetes distribution          | k3s                                                                                                            |
| Namespace                        | `rustfs`                                                                                                       |
| Helm release                     | `rustfs`                                                                                                       |
| Helm chart                       | `oci://registry-1.docker.io/cloudpirates/rustfs`                                                               |
| Chart version at deployment time | `0.9.1`                                                                                                        |
| RustFS image at deployment time  | `docker.io/rustfs/rustfs:1.0.0-beta.1@sha256:3c2d55977829620284ece8593901bf776bcfc0fc9972784352de4dcffdb92416` |
| Ingress controller               | Traefik                                                                                                        |
| StorageClass                     | `local-path`                                                                                                   |
| Data volume                      | `rustfs-data`, `20Gi`, `ReadWriteOnce`                                                                         |
| Logs volume                      | `rustfs-logs`, `1Gi`, `ReadWriteOnce`                                                                          |

## Kubernetes Services

| Service          | Type      | Purpose         | Port   |
| ---------------- | --------- | --------------- | ------ |
| `rustfs`         | ClusterIP | S3/API endpoint | `9000` |
| `rustfs-console` | ClusterIP | Browser console | `9001` |

## Ingresses

| Ingress          | Host                         | Backend                                  |
| ---------------- | ---------------------------- | ---------------------------------------- |
| `rustfs`         | `rustfs.example.net`         | Service `rustfs`, port `api`             |
| `rustfs-console` | `rustfs-console.example.net` | Service `rustfs-console`, port `console` |

## Files on the Cluster

The deployment files are stored on the Kubernetes host:

```bash
/home/admin/rustfs-deploy/values-rustfs.yaml
/home/admin/rustfs-deploy/ingress-console.yaml
```

The Helm values file manages the main RustFS release.

The console Ingress is managed as a separate Kubernetes manifest because the tested chart version includes `extraObjects` in the default values but did not render the desired object in this setup.

## Helm Values

Current important values:

```yaml
deploymentType: deployment
replicaCount: 1

image:
  imagePullPolicy: IfNotPresent

auth:
  accessKey: rustfsadmin
  # secretKey intentionally omitted: Helm chart generates and preserves a random secret in the Kubernetes Secret.

config:
  volumes: /data
  externalAddress: https://rustfs.example.net
  corsAllowedOrigins: "https://rustfs.example.net"
  consoleEnabled: true
  logLevel: info

ingress:
  enabled: true
  className: traefik
  hosts:
    - host: rustfs.example.net
      paths:
        - path: /
          pathType: Prefix
  tls: []

consoleIngress:
  enabled: false

service:
  type: ClusterIP
  port: 9000
  consolePort: 9001

dataPersistence:
  enabled: true
  storageClass: local-path
  size: 20Gi
  accessModes:
    - ReadWriteOnce
  mountPath: /data

logsPersistence:
  enabled: true
  storageClass: local-path
  size: 1Gi
  accessModes:
    - ReadWriteOnce
  mountPath: /app/logs

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 1Gi
```

## Console Ingress Manifest

The browser console is published with a separate Ingress manifest:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rustfs-console
  namespace: rustfs
  labels:
    app.kubernetes.io/name: rustfs
    app.kubernetes.io/instance: rustfs
    app.kubernetes.io/component: console
    app.kubernetes.io/managed-by: admin
spec:
  ingressClassName: traefik
  rules:
    - host: rustfs-console.example.net
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: rustfs-console
                port:
                  name: console
```

Apply or re-apply it with:

```bash
kubectl apply -f /home/admin/rustfs-deploy/ingress-console.yaml
```

## Initial Install or Reinstall

Use this command to install or reconcile the RustFS Helm release:

```bash
cd /home/admin/rustfs-deploy

helm upgrade --install rustfs \
  oci://registry-1.docker.io/cloudpirates/rustfs \
  --namespace rustfs \
  --create-namespace \
  -f values-rustfs.yaml \
  --wait \
  --timeout 10m

kubectl apply -f ingress-console.yaml
```

Expected Helm status:

```text
NAME: rustfs
NAMESPACE: rustfs
STATUS: deployed
```

## Daily Health Checks

Check Kubernetes resources:

```bash
kubectl -n rustfs get deploy,pod,svc,pvc,ingress -o wide
```

Expected shape:

```text
deployment.apps/rustfs   1/1
pod/rustfs-...           1/1     Running
service/rustfs           ClusterIP   9000/TCP
service/rustfs-console   ClusterIP   9001/TCP
pvc/rustfs-data          Bound       20Gi   RWO   local-path
pvc/rustfs-logs          Bound       1Gi    RWO   local-path
ingress/rustfs           traefik     rustfs.example.net           203.0.113.10
ingress/rustfs-console   traefik     rustfs-console.example.net   203.0.113.10
```

Check the API health endpoint:

```bash
curl -sk https://rustfs.example.net/health
```

Expected response contains:

```json
{
  "ready": true,
  "service": "rustfs-endpoint",
  "status": "ok",
  "version": "1.0.0-beta.1"
}
```

Check the console with a browser-like request:

```bash
curl -skL \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  https://rustfs-console.example.net/ | head
```

A browser should show the RustFS login page with:

* `Key Login`
* `STS Login`
* `Account`
* `Key`
* `Login`

## Credentials

The access key is configured as:

```text
rustfsadmin
```

The secret key is generated by the chart and stored in the Kubernetes Secret `rustfs/rustfs`.

Do not put the secret key into documentation, Git, command transcripts, or shell history.

Retrieve the credentials only when needed:

```bash
kubectl -n rustfs get secret rustfs -o jsonpath='{.data.access-key}' | base64 -d; echo
kubectl -n rustfs get secret rustfs -o jsonpath='{.data.secret-key}' | base64 -d; echo
```

Use these credentials for the console `Key Login` fields:

| Field   | Value      |
| ------- | ---------- |
| Account | access key |
| Key     | secret key |

## Functional S3 Test

Use an ephemeral Kubernetes pod with `minio/mc`.

Prefer `secretKeyRef` for automated tests instead of placing secrets directly into command lines.

Minimal interactive pattern:

```bash
AK=$(kubectl -n rustfs get secret rustfs -o jsonpath='{.data.access-key}' | base64 -d)
SK=$(kubectl -n rustfs get secret rustfs -o jsonpath='{.data.secret-key}' | base64 -d)
BUCKET="manual-verify-$(date +%s)"

kubectl -n rustfs run rustfs-mc --rm -i --restart=Never \
  --image=minio/mc:RELEASE.2025-08-13T08-35-41Z \
  --env="AK=$AK" \
  --env="SK=$SK" \
  --env="BUCKET=$BUCKET" \
  --command -- sh -c '
    set -euo pipefail
    mc alias set rustfs http://rustfs:9000 "$AK" "$SK" >/dev/null
    printf "rustfs verification\n" > /tmp/verify.txt
    mc mb "rustfs/$BUCKET"
    mc cp /tmp/verify.txt "rustfs/$BUCKET/verify.txt"
    mc cat "rustfs/$BUCKET/verify.txt"
    mc rm "rustfs/$BUCKET/verify.txt"
    mc rb "rustfs/$BUCKET"
  '
```

Expected object readback:

```text
rustfs verification
```

## Upgrade Procedure

### 1. Inspect Current State

```bash
helm -n rustfs status rustfs
helm -n rustfs get values rustfs
kubectl -n rustfs get deploy,pod,svc,pvc,ingress -o wide
kubectl -n rustfs get events --sort-by=.lastTimestamp | tail -30
```

Confirm that the service is healthy before changing it:

```bash
curl -sk https://rustfs.example.net/health
```

### 2. Check Available Chart Versions

```bash
helm show chart oci://registry-1.docker.io/cloudpirates/rustfs
helm show values oci://registry-1.docker.io/cloudpirates/rustfs > /tmp/rustfs-values-new.yaml
```

Compare the new default values against the current pinned values:

```bash
diff -u /home/admin/rustfs-deploy/values-default.yaml /tmp/rustfs-values-new.yaml || true
```

If a specific chart version is selected, pin it explicitly:

```bash
helm show chart oci://registry-1.docker.io/cloudpirates/rustfs --version <chart-version>
helm show values oci://registry-1.docker.io/cloudpirates/rustfs --version <chart-version> > /tmp/rustfs-values-new.yaml
```

### 3. Render and Validate Before Applying

Render locally:

```bash
cd /home/admin/rustfs-deploy

helm template rustfs \
  oci://registry-1.docker.io/cloudpirates/rustfs \
  --namespace rustfs \
  -f values-rustfs.yaml \
  > /tmp/rustfs-rendered.yaml
```

Run a server-side dry run:

```bash
kubectl apply --dry-run=server -f /tmp/rustfs-rendered.yaml
kubectl apply --dry-run=server -f /home/admin/rustfs-deploy/ingress-console.yaml
```

Review especially:

* image tag and digest
* service names and port names
* PVC names and sizes
* Ingress hostnames
* whether the chart now renders a console Ingress itself

### 4. Upgrade

```bash
cd /home/admin/rustfs-deploy

helm upgrade rustfs \
  oci://registry-1.docker.io/cloudpirates/rustfs \
  --namespace rustfs \
  -f values-rustfs.yaml \
  --wait \
  --timeout 10m

kubectl apply -f ingress-console.yaml
```

If upgrading to a specific chart version:

```bash
helm upgrade rustfs \
  oci://registry-1.docker.io/cloudpirates/rustfs \
  --version <chart-version> \
  --namespace rustfs \
  -f values-rustfs.yaml \
  --wait \
  --timeout 10m

kubectl apply -f ingress-console.yaml
```

### 5. Post-Upgrade Verification

```bash
helm -n rustfs status rustfs
kubectl -n rustfs rollout status deploy/rustfs --timeout=180s
kubectl -n rustfs get deploy,pod,svc,pvc,ingress -o wide
curl -sk https://rustfs.example.net/health
```

Open the console:

```text
https://rustfs-console.example.net/rustfs/console/
```

Then run a small S3 write/read/delete test as shown above.

## Rollback Procedure

List Helm history:

```bash
helm -n rustfs history rustfs
```

Rollback to a previous revision:

```bash
helm -n rustfs rollback rustfs <revision> --wait --timeout 10m
kubectl apply -f /home/admin/rustfs-deploy/ingress-console.yaml
```

Verify:

```bash
kubectl -n rustfs rollout status deploy/rustfs --timeout=180s
curl -sk https://rustfs.example.net/health
```

## Changing Configuration

Edit the Helm values file:

```bash
vi /home/admin/rustfs-deploy/values-rustfs.yaml
```

Apply the change:

```bash
cd /home/admin/rustfs-deploy

helm upgrade rustfs oci://registry-1.docker.io/cloudpirates/rustfs \
  --namespace rustfs \
  -f values-rustfs.yaml \
  --wait \
  --timeout 10m

kubectl apply -f ingress-console.yaml
```

Always check the deployment afterwards:

```bash
kubectl -n rustfs get deploy,pod,svc,pvc,ingress -o wide
curl -sk https://rustfs.example.net/health
```

## Storage Notes

The cluster uses the k3s `local-path` StorageClass:

```text
local-path (default)   rancher.io/local-path   Delete   WaitForFirstConsumer   ALLOWVOLUMEEXPANSION=false
```

Implications:

* The data is node-local to `k8s-node.example.net`.
* This is suitable for the current single-node k3s setup.
* It is not multi-node replicated storage.
* The `rustfs-data` PVC is currently `20Gi`.
* `local-path` does not allow PVC expansion on this cluster.
* Increasing capacity later requires a migration plan, not only editing `size: 20Gi`.

Before destructive storage work, take an application-level backup or migrate objects to another S3 target.

## Backups

At minimum, back up:

* objects stored in RustFS
* Kubernetes Secret `rustfs/rustfs`
* `/home/admin/rustfs-deploy/values-rustfs.yaml`
* `/home/admin/rustfs-deploy/ingress-console.yaml`

Export the Kubernetes objects without exposing the secret in public documentation:

```bash
kubectl -n rustfs get deploy,svc,pvc,ingress,configmap -o yaml > rustfs-k8s-public-resources.yaml
kubectl -n rustfs get secret rustfs -o yaml > rustfs-secret.private.yaml
chmod 600 rustfs-secret.private.yaml
```

## Troubleshooting

### Pod Is Not Ready

```bash
kubectl -n rustfs get pods -o wide
kubectl -n rustfs describe pod -l app.kubernetes.io/instance=rustfs
kubectl -n rustfs logs deploy/rustfs --tail=200
kubectl -n rustfs get events --sort-by=.lastTimestamp | tail -50
```

Common causes:

* image pull failure
* PVC not bound
* local-path provisioner issue
* invalid Helm values
* container cannot write to mounted paths

### API Health Check Fails

```bash
kubectl -n rustfs get svc,endpoints,endpointslices -o wide
kubectl -n rustfs exec deploy/rustfs -- sh -c 'wget -S -O- -T 5 http://127.0.0.1:9000/health 2>&1 | head -20'
curl -skI https://rustfs.example.net/health
```

Check whether the failure is inside the pod, inside the cluster, or only through Traefik.

### Console Shows XML Instead of Login Page

The RustFS root path can behave differently depending on the request headers.

A plain request such as:

```bash
curl https://rustfs-console.example.net/
```

may return S3 XML. This does not necessarily mean the console is broken.

Use a browser-like request instead:

```bash
curl -skL \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  https://rustfs-console.example.net/ | head
```

Or open the console directly:

```text
https://rustfs-console.example.net/rustfs/console/
```

### Console Ingress Missing After Upgrade

Re-apply the separate manifest:

```bash
kubectl apply -f /home/admin/rustfs-deploy/ingress-console.yaml
kubectl -n rustfs get ingress rustfs-console -o wide
```

### Helm Chart Starts Rendering Its Own Console Ingress Later

If a future chart version correctly renders the console Ingress in deployment mode, choose one source of truth.

Do not keep two Ingress resources for the same host.

Suggested process:

1. Render the new chart with `helm template`.
2. Confirm whether it creates a correct `rustfs-console.example.net` Ingress.
3. If yes, move console Ingress management into `values-rustfs.yaml`.
4. Delete the separate manifest only after a successful test.
5. Update this article.

### Logs PVC Warning

Current logs showed:

```text
Failed to initialize file observability logging at '/logs': Permission denied. Falling back to stdout logging.
```

The chart mounts logs at `/app/logs`, while RustFS attempted to use `/logs`.

The service still runs and logs to stdout.

If persistent file logs become important, align the RustFS log directory environment or configuration with the mounted logs path and verify write permissions.

## Security Notes

* Do not commit RustFS secret values.
* Retrieve the secret from Kubernetes only when needed.
* The console is publicly reachable at `rustfs-console.example.net`.
* Use strong credentials.
* Consider adding an external authentication layer if this becomes production-critical.
* Treat this deployment as useful self-hosted object storage, not as a highly available production storage tier without additional validation.

## Quick Command Reference

```bash
# Status
helm -n rustfs status rustfs
kubectl -n rustfs get deploy,pod,svc,pvc,ingress -o wide

# Health
curl -sk https://rustfs.example.net/health

# Console
open https://rustfs-console.example.net/rustfs/console/

# Credentials
kubectl -n rustfs get secret rustfs -o jsonpath='{.data.access-key}' | base64 -d; echo
kubectl -n rustfs get secret rustfs -o jsonpath='{.data.secret-key}' | base64 -d; echo

# Upgrade/reconcile
cd /home/admin/rustfs-deploy
helm upgrade rustfs oci://registry-1.docker.io/cloudpirates/rustfs \
  --namespace rustfs \
  -f values-rustfs.yaml \
  --wait \
  --timeout 10m
kubectl apply -f ingress-console.yaml

# Rollback
helm -n rustfs history rustfs
helm -n rustfs rollback rustfs <revision> --wait --timeout 10m
kubectl apply -f /home/admin/rustfs-deploy/ingress-console.yaml
```
