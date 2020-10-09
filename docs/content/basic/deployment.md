---
title: Deployment
kind: basic
weight: 3
date: 2020-02-17 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

## Kubernetes

STACKL can be quickly deployed on any kubernetes cluster by using Helm

### Prerequisites

You should have a working Kubernetes cluster, this can be local (Minikube, Microk8s), on premise or a cluster in the cloud.

You'll also need Helm and kubectl configured.

### Installing with Helm

This section shows how to quickly deploy STACKL on top of Kubernetes to try it out.

#### Install Stackl

Clone the stackl-helm repository:

```sh
git clone https://github.com/stacklio/stackl-helm.git
```

Create a namespace that will house the STACKL deployment:

```sh
kubectl create namespace stackl
```

Execute the following command to deploy STACKL and all of its components in the active K8s context:

```sh
helm install stackl-helm/stackl -n stackl --generate-name
```

You can see all the pods with the following command:

```sh
kubectl get pods -n stackl
```

At this point STACKL is up and running.

#### Stackl agent

The Stackl Helm chart will not install an agent, which is used to perform automation. For the stackl-agent a separate helm chart is used.
The Stackl agent can be installed within the same namespace, another namespace or even another kubernetes cluster. As long as the stackl-agent has access to the redis instance.

Jobs can be limited to specified agents by their name, but for now the name is "common", this way it will pick up all the jobs.

Install the stackl-agent:

```sh
helm install stackl-helm/stackl-agent -n stackl agent
```

#### Persistent storage

The Helm charts make use of the default storage class to create a persistent volume where the documents will be stored.

#### Helm advanced configuration

For more configuration make sure to check the [configuration page](../configuration).

### Logging with Kubernetes

STACKL has built in logging for each component. STACKL logs to stdout and the default log level is `INFO`.

You can execute following command to see all running pods:

```sh
kubectl get pods -n stackl
```

To check the logs you can execute the following command:

```sh
kubectl logs -f <pod_name>
```
