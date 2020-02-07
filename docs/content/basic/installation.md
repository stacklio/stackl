---
title: Installation
kind: basic
weight: 3
---
This document helps you get STACKL up and running in different deployment
environments. You should read this document if you are planning to deploy STACKL.

## Docker

Docker makes it easy to deploy Stackl locally on your own machine. 

In this section we will explain how to use the official STACKL Docker images in combination with docker-compose to 
easily get STACKL up and running

STACKL releases are available as images on Docker Hub.

* [stacklio/stackl](https://hub.docker.com/orgs/stacklio/repositories)

### Running with Docker

Because STACKL makes use of different components we use docker-compose to set everything up, to start you use the following:

```yaml
version: '3'
networks:
  default:
    external:
      name: stackl
  stackl_bridge:
    external:
      name: stackl_bridge
services:
  stackl-rest:
    restart: always
    image: stacklio/stackl-rest:dev
    container_name: stackl_app
    networks:
      - stackl_bridge
    volumes:
      - /tmp/example_database:/lfs_test_store/
    ports:
      - 8080:80
      - 8888:8888
    environment:
      - STACKL_STORE=LFS
      - STACKL_TASK_BROKER=Custom
      - STACKL_AGENT_BROKER=Local
      - STACKL_AGENT_HOST=stackl-agent:50051
      - GRPC_VERBOSITY="DEBUG"
      - STACKL_LOGPATH=/var/log/stackl.log
      - STACKL_MESSAGE_CHANNEL=RedisSingle
      - STACKL_STACKLRESTHOST=stackl-rest
      - STACKL_STACKLRESTPORT=80
      - STACKL_REDISSENTINELHOST=stackl-redis
      - TCP_PORTS=80
      - SERVICE_PORTS=80
      - STACKL_REDIS_HOST=stackl-redis
      - LOGLEVEL=DEBUG
  stackl-worker:
    restart: always
    image: stacklio/stackl-worker:dev
    networks:
      - stackl_bridge
    stdin_open: true
    tty: true
    volumes:
      - /tmp/example_database:/lfs_test_store/
    depends_on:
      - stackl-rest
      - stackl-redis
    ports:
      - 9999:9999
    environment:
      - STACKL_STORE=LFS
      - STACKL_TASK_BROKER=Custom
      - STACKL_AGENT_BROKER=Local
      - STACKL_AGENT_HOST=stackl-agent:50051
      - GRPC_VERBOSITY="DEBUG"
      - STACKL_LOGPATH=/var/log/stackl.log
      - STACKL_MESSAGE_CHANNEL=RedisSingle
      - STACKL_STACKLRESTHOST=stackl-rest
      - STACKL_STACKLRESTPORT=80
      - STACKL_REDISSENTINELHOST=stackl-redis
      - STACKL_ROLE=worker
      - STACKL_REDIS_HOST=stackl-redis
      - TCP_PORTS=8888
      - LOGLEVEL=DEBUG
  stackl-redis:
    restart: always
    image: redis:5.0.5
    networks:
      - stackl_bridge
  stackl-agent:
    restart: always
    image: stacklio/stackl-docker-agent:dev
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - stackl_bridge
    ports:
      - 8889:8889
      - 50051:50051
    environment:
      - STACKL_HOST=stackl-rest:80
      - HOST_MACHINE=stackl-agent
      - TAGS=['common']
```

This Docker compose file exists out of 4 services:

* stackl-rest: The Rest api for STACKL
* stackl-worker: The STACKL worker
* stackl-redis: A redis instance, used as message channel
* stackl-agent: component responsable for creating stack-instances

Start STACKL by saving the above yaml to a file called docker-compose.yml and execute the following command in that directory:

`docker-compose up -d`

OPTIES DOCKER COMPOSE #TODO

By default, STACKL will now run on port 8080

Test that STACKL is available:

```
curl -i localhost:8080/
```

#### Logging

Each of the components has logging, use following command to see all running containers:

`docker ps`

and to see the logs use following command

`docker logs -f <container_id>`

##### Rest Api

The logs of this container show data of all the requests to the STACKL API

```
[StacklApiResource] API request received. Request environ: {'QUERY_STRING': '', 'REQUEST_METHOD': 'GET', 'CONTENT_TYPE': '', 'CONTENT_LENGTH': '', 'REQUEST_URI': '/documents/environment', 'PATH_INFO': '/documents/environment', 'DOCUMENT_ROOT': '/etc/nginx/html', 'SERVER_PROTOCOL': 'HTTP/1.1', 'REQUEST_SCHEME': 'http', 'REMOTE_ADDR': '172.26.0.1', 'REMOTE_PORT': '41432', 'SERVER_PORT': '80', 'SERVER_NAME': '', 'HTTP_HOST': 'localhost:8080', 'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:72.0) Gecko/20100101 Firefox/72.0', 'HTTP_ACCEPT': 'application/json', 'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.5', 'HTTP_ACCEPT_ENCODING': 'gzip, deflate', 'HTTP_REFERER': 'http://localhost:8080/', 'HTTP_CONNECTION': 'keep-alive', 'HTTP_COOKIE': 'cookieconsent_status=dismiss; intercom-id-v1eeh3ou=61ed63fc-6bcd-468a-a6a8-0df4aaebf387', 'wsgi.input': <uwsgi._Input object at 0x7f4ce613fca8>, 'wsgi.file_wrapper': <built-in function uwsgi_sendfile>, 'wsgi.version': (1, 0), 'wsgi.errors': <_io.TextIOWrapper name=2 mode='w' encoding='UTF-8'>, 'wsgi.run_once': False, 'wsgi.multithread': False, 'wsgi.multiprocess': True, 'wsgi.url_scheme': 'http', 'uwsgi.version': b'2.0.18', 'uwsgi.node': b'2d4f3c454cca', 'werkzeug.request': <Request 'http://localhost:8080/documents/environment' [GET]>}
```

##### Worker

display logs of all Stackl tasks and connection info to e.g. Redis

```
info][RedisQueue] Broker got message: '{'type': 'subscribe', 'pattern': None, 'channel': b'c159d934cbe2', 'data': 3}'
INFO:RedisQueue:info][RedisQueue] Broker got message: '{'type': 'subscribe', 'pattern': None, 'channel': b'c159d934cbe2', 'data': 3}
```

##### Agent

Shows the log of incoming stack instance creation requests

##### Redis

Contains logs about the Redis

#### Volume Mounts

LEG HIER UIT HOE LFS DATABASE WERKT EN GEMOUNT

The simplest way to load data and policies into OPA is to provide them via the
file system as command line arguments. When running inside Docker, you can
provide files via volume mounts.

#### More Information

See configuration.md for more information (link naar configuration.md)

### Tagging

#TODO 

## Kubernetes

### Kicking the Tires

WAT MOET IK HEBBEN
KUBERNETES -> SNELLE SETUP MET MICROK8S
HELM DEPLOYMENT

This section shows how to quickly deploy OPA on top of Kubernetes to try it out.

MAAK HIER MICROK8S VAN
> These steps assume Kubernetes is deployed with
[minikube](https://github.com/kubernetes/minikube). If you are using a different
Kubernetes provider, the steps should be similar. You may need to use a
different Service configuration at the end.

CREATE HELM CHARTS

HELM VALUES UITLEGGEN
HELM INSTALL
HELM LS
KUBECTL GET PO
UITLEGGEN COMPONENTS


Next, create a HELM CHART to run STACKL. The ConfigMap containing the policy is
volume mounted into the container. This allows STACKL to load the policy from
the file system.

```

```bash
helm install -n test .
```

At this point STACKL is up and running. 

YOU CAN NOW SEE WHERE STACKL IS RUNNING BY KUBECTL GET SVC AND GO TO THE REST API

Create a Service to expose the OPA API so
that you can query it:

```bash
kubectl create -f service-opa.yaml
```

NAMAKEN
Get the URL of OPA using `minikube`:

```bash
OPA_URL=$(minikube service opa --url)
```

Now you can query OPA's API:

```bash
curl $OPA_URL/v1/data
```

CHECK STACKL WERKING
OPA will respond with the greeting from the policy (the pod hostname will differ):

```json
{
  "result": {
    "example": {
      "greeting": "hello from pod \"opa-78ccdfddd-xplxr\"!"
    }
  }
}
```

## HTTP Proxies

TODO