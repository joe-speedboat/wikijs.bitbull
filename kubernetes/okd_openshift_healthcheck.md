---
title: OKD Healthcheck 4.x
description: Howto Check OKD or Openshift Clusters for health
published: true
date: 2026-10-26T14:12:22.408Z
tags: okd, openshift, kubernetes, healthcheck
editor: markdown
dateCreated: 2026-02-15T08:43:26.256Z
---

# Links

* https://docs.openshift.com/container-platform/3.9/day_two_guide/environment_health_checks.html
* https://docs.openshift.com/container-platform/4.4/backup_and_restore/replacing-unhealthy-etcd-member.html
* https://kubernetes.io/docs/concepts/

# Nodes

Kubernetes runs your workload by placing containers into Pods to run on Nodes. A node may be a virtual or physical machine, depending on the cluster. Each node contains the services necessary to run Pods.

## Overview

```
[chris@control(zabbix-dev/system:admin) ~]$ oc get nodes -o wide
NAME       STATUS   ROLES           AGE   VERSION   INTERNAL-IP       EXTERNAL-IP   OS-IMAGE                                   KERNEL-VERSION                CONTAINER-RUNTIME
master01   Ready    master,worker   40d   v1.17.1   192.168.100.221   <none>        RHEL CoreOS 44.81.202005062110-0 (Ootpa)   4.18.0-147.8.1.el8_1.x86_64   cri-o://1.17.4-8.dev.rhaos4.4.git5f5c5e4.el8
master02   Ready    master,worker   40d   v1.17.1   192.168.100.222   <none>        RHEL CoreOS 44.81.202005062110-0 (Ootpa)   4.18.0-147.8.1.el8_1.x86_64   cri-o://1.17.4-8.dev.rhaos4.4.git5f5c5e4.el8
master03   Ready    master,worker   40d   v1.17.1   192.168.100.223   <none>        RHEL CoreOS 44.81.202005062110-0 (Ootpa)   4.18.0-147.8.1.el8_1.x86_64   cri-o://1.17.4-8.dev.rhaos4.4.git5f5c5e4.el8
worker01   Ready    worker          40d   v1.17.1   192.168.100.231   <none>        RHEL CoreOS 44.81.202005062110-0 (Ootpa)   4.18.0-147.8.1.el8_1.x86_64   cri-o://1.17.4-8.dev.rhaos4.4.git5f5c5e4.el8
worker02   Ready    worker          40d   v1.17.1   192.168.100.232   <none>        RHEL CoreOS 44.81.202005062110-0 (Ootpa)   4.18.0-147.8.1.el8_1.x86_64   cri-o://1.17.4-8.dev.rhaos4.4.git5f5c5e4.el8
```

## Resources

```
Usage:
  oc adm top [flags]

Available Commands:
  images       Show usage statistics for Images
  imagestreams Show usage statistics for ImageStreams
  node         Display Resource (CPU/Memory/Storage) usage of nodes
  pod          Display Resource (CPU/Memory/Storage) usage of pods
```

```
[chris@control(default/system:admin) ~]$ oc adm top nodes
NAME       CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
master01   796m         22%    3601Mi          52%
master02   852m         24%    3626Mi          52%
master03   578m         16%    2494Mi          36%
worker01   596m         17%    2644Mi          38%
worker02   538m         15%    2426Mi          35%
```

## Pending certificate signing requests

Certificate signing requests are issued by OpenShift automatically. But you have to approve them manually.  
Pending CSRs mostly result in a cluster that is not fully functioning.

```
[chris@control(openshift-console/system:admin) ~]$ oc get csr
NAME        AGE     SIGNERNAME                                    REQUESTOR                                                                   CONDITION
csr-2g82l   3m23s   kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-bz74n   9m25s   kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
```

```
[chris@control(openshift-console/system:admin) ~]$ oc get csr -o name | xargs oc adm certificate approve
certificatesigningrequest.certificates.k8s.io/csr-2g82l approved
certificatesigningrequest.certificates.k8s.io/csr-bz74n approved
```

```
[chris@control(openshift-console/system:admin) ~]$ oc get csr
NAME        AGE     SIGNERNAME                                    REQUESTOR                                                                   CONDITION
csr-2g82l   3m55s   kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Approved,Issued
csr-bz74n   9m57s   kubernetes.io/kube-apiserver-client-kubelet   system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Approved,Issued
```

# Kubernetes API health endpoints

The Kubernetes API server provides API endpoints to indicate the current status of the API server.

```
kubectl get --raw='/readyz?verbose'
```

# etcd

etcd is a consistent and highly-available key value store used as Kubernetes’ backing store for all cluster data.

```
[chris@control(zabbix-dev/system:admin) ~]$ oc get etcd -o=jsonpath='{range .items[0].status.conditions[?(@.type=="EtcdMembersAvailable")]}{.message}{"\n"}'
master02,master01,master03 members are available,  have not started,  are unhealthy,  are unknown
```

# router

There are many ways to get traffic into the cluster. The most common approach is to use the OpenShift Container Platform router as the ingress point for external traffic destined for services in your OpenShift Container Platform installation.

```
[chris@control(default/system:admin) ~]$ oc get deployment,pod --namespace openshift-ingress
NAME                             READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/router-default   2/2     2            2           40d

NAME                                  READY   STATUS    RESTARTS   AGE
pod/router-default-5fdb964dfb-kkl5p    1/1     Running   0          3d1h
pod/router-default-5fdb964dfb-nb8ff    1/1     Running   0          3d1h
```

# registry

OpenShift Container Platform can build container images from your source code, deploy them, and manage their lifecycle. To enable this, OpenShift Container Platform provides an internal, integrated container image registry.

```
[chris@control(default/system:admin) ~]$ oc get pod,deployment -n openshift-image-registry
NAME                                                    READY   STATUS    RESTARTS   AGE
pod/cluster-image-registry-operator-7bff4c7595-hkbqx    2/2     Running   0          2d23h
pod/image-registry-6b6745b4f9-wqwdx                      1/1     Running   0          3d2h
pod/node-ca-6wgpw                                        1/1     Running   0          3d2h
...

NAME                                              READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/cluster-image-registry-operator   1/1     1            1           40d
deployment.apps/image-registry                    1/1     1            1           40d
```

# ClusterOperators - Version 4x

Operators are pieces of software that ease the operational complexity of running another piece of software.

```
[chris@control(zabbix-dev/system:admin) ~]$ oc -n default get clusteroperators
NAME                               VERSION   AVAILABLE   PROGRESSING   DEGRADED   SINCE
authentication                     4.4.4     True        False         False      35d
cloud-credential                   4.4.4     True        False         False      40d
cluster-autoscaler                 4.4.4     True        False         False      40d
...
storage                            4.4.4     True        False         False      2d23h
```

# Deployment

A Deployment provides declarative updates for Pods and ReplicaSets.

```
[chris@control(zabbix-dev/system:admin) ~]$ oc get deployment --all-namespaces
NAMESPACE                         NAME                              READY   UP-TO-DATE   AVAILABLE   AGE
openshift-apiserver-operator      openshift-apiserver-operator      1/1     1            1           40d
openshift-apiserver               apiserver                         3/3     3            3           3d
```


# ReplicaSet

```
[chris@control(zabbix-dev/system:admin) ~]$ oc get replicaset --all-namespaces | egrep -v ' 0 .* 0 '
NAMESPACE                         NAME                                      DESIRED   CURRENT   READY   AGE
openshift-apiserver-operator      openshift-apiserver-operator-8596449546   1         1         1       3d
openshift-apiserver               apiserver-95c79c585                       3         3         3       2d21h
[...]
```

# Pods (restarts)

```
[chris@control(zabbix-dev/system:admin) ~]$ oc get pods --all-namespaces
NAMESPACE                         NAME                                           READY   STATUS    RESTARTS   AGE
openshift-apiserver-operator      openshift-apiserver-operator-8596449546-kmmt6  1/1     Running   0          2d20h
openshift-apiserver               apiserver-95c79c585-b4h7f                      1/1     Running   0          2d20h
[...]
```

# StatefulSets

```
[chris@control(zabbix-dev/system:admin) ~]$ oc get statefulset --all-namespaces
NAMESPACE              NAME                READY   AGE
openshift-monitoring   alertmanager-main   3/3     40d
openshift-monitoring   prometheus-k8s      2/2     40d
```

# DaemonSet

```
[chris@control(zabbix-dev/system:admin) ~]$ oc get daemonset --all-namespaces
NAMESPACE                                NAME               DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR                     AGE
openshift-cluster-node-tuning-operator   tuned              5         5         5       5            5           kubernetes.io/os=linux            2d23h
openshift-controller-manager             controller-manager 3         3         3       3            3           node-role.kubernetes.io/master=   40d
[...]
```

# ReplicationControllers

Result of a Deployment by DeploymentConfig.

```
[chris@control(zabbix-dev/system:admin) ~]$ oc get replicationcontroller --all-namespaces
NAMESPACE    NAME                       DESIRED   CURRENT   READY   AGE
zabbix-dev   mariadb-1                  1         1         1       2d1h
zabbix-dev   zabbix-cachet-1            0         0         0       45h
zabbix-dev   zabbix-server-mysql-1      1         1         1       2d1h
zabbix-dev   zabbix-web-nginx-mysql-1   1         1         1       2d1h
```

# Persistent Volumes

```
[chris@control(test/system:admin) ~]$ oc get pv
NAME          CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                                   STORAGECLASS   AGE
pv10          5Gi        RWO            Retain           Available                                                   40d
pv11          5Gi        RWO            Retain           Released   test/mariadb                              40d
pv20          5Gi        RWO            Retain           Bound      zabbix-dev/mariadb                        40d
registry-pv   100Gi      RWX            Retain           Bound      openshift-image-registry/registry-pvc     40d
[...]
```

# Persistent Volume Claims

```
[chris@control(test/system:admin) ~]$ oc get pvc --all-namespaces
NAMESPACE                  NAME                        STATUS    VOLUME        CAPACITY   ACCESS MODES   STORAGECLASS   AGE
openshift-image-registry   registry-pvc                Bound     registry-pv   100Gi      RWX                           40d
test                       mariadb                     Pending                                               11s
zabbix-dev                 mariadb                     Bound     pv20          5Gi        RWO                           2d1h
zabbix-dev                 zabbix-server-mysql-claim   Bound     pv38          5Gi        RWX                           2d1h
```

# events

```
[chris@control(test/system:admin) ~]$ oc get events --field-selector type!=Normal --watch
LAST SEEN   TYPE      REASON             OBJECT                MESSAGE
<unknown>   Warning   FailedScheduling   pod/mariadb-1-bcb8h   error while running "VolumeBinding" filter plugin for pod "mariadb-1-bcb8h": pod has unbound immediate PersistentVolumeClaims
```

```
[chris@control(test/system:admin) ~]$ kubectl get event --watch
LAST SEEN   TYPE    REASON                        OBJECT                            MESSAGE
107s        Normal  ReplicationControllerScaled   deploymentconfig/mariadb          Scaled replication controller "mariadb-1" from 1 to 0
```
