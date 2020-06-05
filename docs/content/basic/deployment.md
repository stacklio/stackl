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

STACKL can be quickly deployed in different IT environments through either Docker or Kubernetes.
This page describes how to set it up simply and also how to view the logs of the various deployed components.
A Docker deployment is easy and quick with the only requirement being a working docker installation, which is available for every common operating system. This is further described in [Docker](#docker).
A Kubernetes deployment requires a working kubernetes cluster. Since this is not always trivial, we provide a Vagrant Development box which only needs VirtualBox and Vagrant. This is further described in [Kubernetes](#kubernetes).

In order to get you properly started, make sure to clone the STACKL repository to the system you're using:

```sh
git clone https://github.com/stacklio/stackl.git
```

## Docker

Docker makes it easy to deploy STACKL locally on your own machine.

In this section we will explain how to use the official STACKL Docker images in combination with Docker Compose to easily get STACKL up and running.

STACKL releases are available as images on Docker Hub.

* [stacklio/stackl](https://hub.docker.com/orgs/stacklio/repositories)

### Prerequisites

You will need to check if docker and docker-compose is installed before installing STACKL.

* Docker environment: <https://docs.docker.com/engine/installation/>
* Docker-compose: <https://docs.docker.com/compose/install/>

### Running with Docker

Because STACKL makes use of different components we use Docker Compose to set everything up, to get started you can use the docker compose file provided in [build/example-docker](https://github.com/stacklio/stackl/tree/master/build/example_docker/docker-compose.yaml).

The Docker Compose file exists out of 4 services:

* `stackl-rest`: The rest api for STACKL
* `stackl-worker`: The STACKL worker
* `stackl-redis`: A Redis instance, used as message channel
* `stackl-agent`: Component responsible for creating stack-instances

Simply execute the following commands to set up your environment. We assume that you already cloned the repository to your own system and that you are in the root of the project.

_**Note**_
_We copied the example database to the `tmp` directory, don't skip this step since this path is required in the Docker Compose file. You should also create a Docker network named `stackl_bridge` which is used for the STACKL deployment._

```sh
cp -R build/example_database /tmp/example_database
cd build/example_docker
docker network create stackl_bridge
docker-compose up -d
```

By default, STACKL will run on port 8080, you can issue following command to check if STACKL is available:

```sh
curl -i localhost:8080/
```

If you want to cleanup your Docker Compose environment, you can simply run following command:

```sh
docker-compose down
```

#### Volume Mounts

The simplest way to load documents into STACKL is to provide them via the
Docker volume mounts. By default `/tmp/example_database` (configured [above](#running-with-docker)).

#### Advanced configuration

For more configuration make sure to check the [configuration page](../configuration).

### Logging with Docker

STACKL has built in logging for each component. STACKL logs to stdout and the log level can be set in the `LOGLEVEL` variable in the [Docker Compose file](https://github.com/stacklio/stackl/tree/master/build/example_docker/docker-compose.yaml). You can simply modify the variable in the file and rerun the `docker-compose up -d` command. The default log level is `INFO`.

You can execute following command to see all running containers:

```sh
docker ps
```

To check the logs you can execute the following command:

```sh
docker logs -f <container_id>
```

## Kubernetes

### Prerequisites

You should have a working Kubernetes cluster, this can be locally (Minikube, Microk8s) or a cluster in the cloud. If you don't have any cluster yet you can make use of a local development environment provided by [STACKL](https://stackl.io).
The Vagrant development environment meets all requirements needed to install STACKL. The development box is a CentOS7 distribution and has following tools installed:

* [Ansible](https://www.ansible.com/): `2.9.2`
* [Kubectl](https://kubernetes.io/docs/reference/kubectl/overview/): `1.17`
* [Microk8s](https://microk8s.io/): `1.17`
* [oc](https://docs.openshift.com/container-platform/4.2/cli_reference/openshift_cli/getting-started-cli.html): `3.11.0`
* [Pip 3](https://pip.pypa.io/en/stable/): `9.0.3`
* [Podman](https://podman.io/): `1.4.4`
* [Python 3](https://www.python.org/): `3.6.8`
* [snapd](https://snapcraft.io/snapd): `2.42.2`

If you want to run the [STACKL Vagrant box](https://app.vagrantup.com/stacklio/boxes/centos7-devbox/) as development environment, your system should meet following requirements:

* [VirtualBox](https://www.virtualbox.org/wiki/Downloads) should be installed.
* [Vagrant](https://www.vagrantup.com/downloads.html) should be installed.

The STACKL development environment can be set up using following commands

```sh
vagrant init stacklio/centos7-devbox
vagrant up
```

Once the box is properly set up, you can easily enter it issuing following command:

```sh
vagrant ssh
```

If synced folders are enabled, you will see it in the output and you can access it by going to `cd /vagrant`.

Without synced folder clone the STACKL repository into the Vagrant box (execute following command inside the Vagrant box):

```sh
git clone https://github.com/stacklio/stackl.git
```

Now you're all set to get started installing STACKL using Helm templates! You can continue with the next steps like STACKL [installation](#installing-with-helm) or [development with Skaffold]([http://development](https://skaffold.dev/docs/workflows/dev/)), for example with `make dev`.

Done using the Vagrant box? You can either stop this box so that you can use it again later or delete it entirely with one of following commands:

```sh
# Stop the Vagrant box
vagrant halt

# Destroy the Vagrant box
vagrant destroy -f
```

### Installing with Helm

This section shows how to quickly deploy STACKL on top of Kubernetes to try it out.

#### Install Stackl

These steps assume Kubernetes is deployed with Microk8s. If you are using a different Kubernetes provider, the steps should be similar. You may need to use a different Service configuration at the end. You should have already cloned the Helm repository, if not you can clone the repository with: `git clone https://github.com/stacklio/stackl.git`.

Create a namespace that will house the STACKL deployment:

```sh
kubectl create namespace stackl
```

Execute the following command to deploy STACKL and all of its components in the active K8s context:

```sh
helm install stackl/build/helm -n stackl --generate-name
```

You can see all the pods with the following command:

```sh
watch kubectl get pods -n stackl
```

At this point STACKL is up and running.

#### Stackl agent

The Stackl Helm chart will not install an agent, which is used to perform automation. For the stackl-agent a separate helm chart is used.
The Stackl agent can be installed within the same namespace, another namespace or even another kubernetes cluster. As long as the stackl agent
is able to establish a http/2 connection to stackl.

Jobs can be limited to specified agents with the stacklAgent.selector value. This is in the format of <environment>.<location>.<zone> 
using * instead of the name of an environment, location or zone will make it so the agent can be used for each of those.

Install the stackl-agent:

```sh
helm install stackl/build/helm-agent -n stackl agent
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

## Logging

### REST API

The logs of the `stackl-rest` container show data of all the requests made to the STACKL API.

Example:

```sh
[pid: 37|app: 0|req: 6/7] 172.26.0.1 () {42 vars in 690 bytes} [Fri Feb 14 15:15:31 2020] GET /swagger.json => generated 11028 bytes in 19 msecs (HTTP/1.1 200) 3 headers in 106 bytes (1 switches on core 0)
[pid: 30|app: 0|req: 2/8] 172.26.0.1 () {42 vars in 704 bytes} [Fri Feb 14 15:15:42 2020] GET /documents/environment => generated 270 bytes in 10 msecs (HTTP/1.1 200) 3 headers in 104 bytes (1 switches on core 0)
```

### Worker

The `stackl-worker` displays logs of all STACKL tasks and connection info to e.g. Redis.

Example:

```sh
{'time':'2020-02-14 15:15:12,665', 'level': 'DEBUG', 'message': '[Worker] Initialised Worker.'}
{'time':'2020-02-14 15:15:12,665', 'level': 'DEBUG', 'message': '[Worker] Starting Worker'}
{'time':'2020-02-14 15:15:17,672', 'level': 'DEBUG', 'message': '[Worker] Starting queue listen'}
{'time':'2020-02-14 15:15:17,674', 'level': 'INFO', 'message': '[Worker] start_task_popping. Starting listening on redis queue'}
{'time':'2020-02-14 15:15:17,676', 'level': 'INFO', 'message': '[Worker] Waiting for items to appear in queue'}
```

### Agent

The `stackl-agent` used by the Helm chart is a Kubernetes agent, this means that the agent will create a new pod for every automation job. The agent will log the incoming stack instance creation requests.

Example:

```sh
starting kubernetes agent
action: "create"
invocation {
  image: "stacklio/terraform-vm"
  infrastructure_target: "production.brussels.cluster1"
  stack_instance: "test_vm"
  service: "webserver"
  functional_requirement: "linux"
  tool: "terraform"
}
```

### Redis

The `stackl-redis` container contains logs about Redis.

```sh
1:M 14 Feb 2020 15:15:16.645 * 1 changes in 3600 seconds. Saving...
1:M 14 Feb 2020 15:15:16.645 * Background saving started by pid 19
19:C 14 Feb 2020 15:15:16.660 * DB saved on disk
19:C 14 Feb 2020 15:15:16.661 * RDB: 0 MB of memory used by copy-on-write
1:M 14 Feb 2020 15:15:16.746 * Background saving terminated with success
```
