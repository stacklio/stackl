---
title: Task management
kind: advanced
weight: 3
---
STACKL is a system that performs work given by Producers through API calls. Internally it represents the work as atomic Tasks and uses Workers for processing. Task are submitted for management to the Task Broker (TB) which communicates them with workers through the Message Channel (MC). Depending on the task, the worker may interact with the Datastore and/or external Agents. STACKL manages the full life cycle of the task, ensuring it happens completely or is rolled back, to achieve eventual consistency between itself (i.e., the database and its modelling) and the clients IT environment (i.e., instantiated applications and accessible infrastructure).

STACKL allows for pluggable task brokers; for managing the tasks, pluggable message channels; for communicating the tasks with workers, and workers, to allow for different types of managing entities. This enables different task broker systems, such as custom implementations, Celery, Faust, ..., message channels, such as Redis, RabbitMQ, Kafka, …., and worker systems, such as custom containers, FaaS, … . These systems are chosen during the deployment of STACKL to achieve desired characteristics, such as simplicity, scalability, reliability, cost, and so on.

## Tasks
Tasks are atomic units of work constructed by STACKL for internal processing when a Producer makes a request. For regular API calls, these can be: creating or modifying documents, creating or instantiating ST, complex queries and so on. The lifetime of a task is based on the principle of eventual consistency: either all actions in a task are performed correctly, including at the client and in the datastore, or it fails, due to a timeout or failure result, and all made changes are rolled back to the previous state. As such, a task is alive for as long as it takes for consistency to be achieved or for as long as its specified timeout.. Once the system is consistent, the task can be deleted.

Tasks have the following properties:

* Atomicity: done entirely or not-at-all
* Topics: what the task is
  - a Stack Task concerns itself with doing things on Stacks, a Result Task on communicating the result of another task, and so on
  - This allows STACKL to correctly process a task
* Status: a report of the current state of the task
  - Available, (In-Progress), Failed or Completed
  - This allows STACKL to monitor the task
* Self-contained
  - A task contains all the info needed to execute it at processing time, to allow for workers to be stateless and simplifying rollback
* Subproperties
  - Depends on the topic
  - Origin
    - To report the result of the task to

## Task Broker
A Task Broker manages submitted tasks in an atomic fashion: done completely or rolled-back. It is a pluggable module that is chosen during the deployment of STACKL. The pluggable module is accessed transparently through a general wrapper/interface, the TB Interface. A pluggable TB provides an implementation of the interface so that tasks are always interacted with in the same way, independent from the backend, and only the performance characteristics may change.

The TB itself does not process tasks but only manages them. It accepts the tasks from Producers and communicates them to Workers. Before delegating task for processing, it may add additional information such as communication parameters so that the task is self-contained. There are many systems that manage tasks. A minimal set for the MVP of STACKL are Custom and either Celery or Faust.

Other targets or ideas can be found:

* https://taskqueues.com/ and http://queues.io/
* Gevent (concurrency) http://charlesleifer.com/blog/ditching-the-task-queue-for-gevent/

Producers have to be able to:
  * Give a task to the TB

### Modules

#### Custom Task Broker
The Custom TB accepts tasks and puts them in a monitoring task queue and submits it to the MC.
The task queue keeps track of all the tasks by monitoring their timeout and changing their status based on worker results. If a task has failed (due to a time out or a negative result task), the TB does a rollback of the task and removes it from the queue. If a task has succeeded, it is removed from the queue.

## Message Channel
The message channel is the medium through which STACKL communicates with other parties during the processing of a task (for naming, see stackoverflow post). It is a pluggable module that is chosen during the deployment of STACKL. The pluggable module is accessed transparently through an interface, the MC Interface. Each plugged technology, whether custom or third-party, provides an implementation of this interface so that from tasks are communicated in the same way, independent from the backend, and only the performance characteristics change.

The MC can be any messaging system that allows to spread information. There are many systems that can do this. A minimal set for the MVP of STACKL are Redis and either RabbitMQ or Kafka.

The MC has to be able to provide messages to workers and process them transparently:

* Temporarily store messages
* Publish/subscribe
* Push/Pop system
* Process the communicated data so that the input and output are json files

### Modules

#### Redis
Redis provides a simple in-memory datastore/message queue that allows publish/subscribe communications as well as pushing/popping messages.

## Workers
Workers are software entities that process the tasks. Workers are stateless, able to communicate with STACKL and agents, and able to execute the actions described in a task. This allows horizontal scalability and  to keep the concept of a worker general with an eye towards the future (custom containers, functions on a server, etc ).

Currently, workers are containers that use various handlers and managers implemented in STACKL to process tasks. For the processing of tasks, they have to be able to:

* Retrieve it from the TB
* Report back a result
* Communicate with agents
* Access the database

### Worker containers
Workers, when implemented as containers, use several parts of the codebase of STACKL to manage tasks.
There is a hierarchical processing structure based on responsibilities which consists of the top-level Worker, mid-level Managers and Handlers.
A Worker does the high-level task management and has two responsibilities: (1) retrieving/receiving the Task from the TB and (2) delegating the (parts of the) task to a suitable Manager. A Manager does the low-level task management and has three responsibilities: (1) handle the main persistent results of in the task, such as writing to the database and communicating with agents, (2) publish the result of the task (success/failure), and (3) delegating the processing elements of the tasks to suitable Handlers. Handlers do the computational parts of the tasks, for instance, constraint solving and potentially storing intermediary results of the task.

## Considerations
