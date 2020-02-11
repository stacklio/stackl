---
title: Tasks and Processing
kind: advanced
weight: 3
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

STACKL can be given work through its API.
Work is internally converted to a **Task**, an atomic unit of work with a result.
Task are submitted for management to a **Task Broker**  which delegates them to distributed workers through the message channel.
Depending on the task, the worker may interact with the datastore and/or external agents.
STACKL manages the full life cycle of the task, ensuring it happens completely or is rolled back, to report the result back to the user and to achieve eventual consistency between its representation of the user's IT environment (through documents) and the actual user's IT environment (i.e., instantiated applications and accessible infrastructure).

{{< figure src="task_processing_overview.png" width="70" caption="Task processing overview" >}}
{{< figure src="task_processing_flow.png" width="90" caption="Task processing flow" >}}

STACKL uses pluggable modules for the task broker; which manages the tasks, for the message channel; for communicating tasks with workers, and for the workers, to allow for different types of logic engines.
Modules allow the use of different task broker systems (e.g., custom implementations, Celery, Faust, ...), message channels, (e.g., Redis, RabbitMQ, Kafka, ...) and worker systems (e.g., custom containers, FaaS, ...) .
The choice of module determines the performance characteristics of STACKL task processing, such as simplicity, scalability, reliability, cost, and so on.

## Tasks

Tasks are atomic units of work constructed by STACKL when receiving an API call.
These can be: creating or modifying documents, creating or instantiating stack templates, complex queries, and so on.
The lifetime of a task is based on the principle of eventual consistency: either all actions in a task are performed correctly, including at the user and in the datastore, or it fails, due to a timeout or failure result, and all made changes are rolled back to the previous state.
Once the desired state is achieved or rollbacked and this is correctly represented in STACKL and is consistent, the task is removed.

Tasks have the following properties:

* **Atomicity:** Done entirely or not-at-all
* **Topics:** What the task is about
* **Status:** A report of the current state of the task, either Available, (In-Progress), Failed or Completed
* **Self-contained:** A task contains all the info needed to execute it at processing time, to allow for workers to be stateless and simplifying rollback
* **Subproperties:** Depending on the topic, there can be other necessary subproperties

### Task Topics

TODO

Stack Task

Result Task

Document Task

## Task Broker

The Task broker manages tasks atomically: done completely or rolled-back.
It is a pluggable module that is chosen during the deployment of STACKL.
The pluggable module is accessed transparently through a general wrapper/interface, the  task broker interface.
A pluggable task broker implements this interface so that tasks are always interacted with in the same way, independent from the backend, and only the performance characteristics change.
The task broker itself does not process tasks but only manages them.

It accepts the tasks from producers and communicates them to workers.
Before delegating tasks for processing, it may add additional information such as communication parameters so that the task is self-contained.

See [Task Broker Interface]({{< ref "../modules/task_broker_interface.md" >}}) for information about the available modules and how to create your own.

## Message Channel

The message channel is the medium through which STACKL communicates with other parties during the processing of a task.
It is a pluggable module that is chosen during the deployment of STACKL.
The pluggable module is accessed transparently through an interface, the message channel interface.
Each plugged technology, whether custom or third-party, provides an implementation of this interface so that from tasks are communicated in the same way, independent from the backend, and only the performance characteristics change.

See [Message Channel Interface]({{< ref "../modules/message_channel_interface.md" >}}) for information about the available modules and how to create your own.

## Workers

Workers are software entities that process the tasks and function as self-contained logic engines.
Workers are stateless, able to communicate with STACKL and agents, and able to execute the actions described in a task.
This allows horizontal scalability and to keep the concept of a worker general for extensibility.

Currently, workers are containers that use various handlers and managers implemented in STACKL to process tasks.
For the processing of tasks, they have to be able to:

* Retrieve it from the task broker
* Do processing on key/value documents
* Report back a result
* Communicate with agents
* Access the database

### Worker containers

Workers, when implemented as containers, use several parts of the codebase of STACKL to manage tasks.
There is a hierarchical processing structure based on responsibilities which consists of the top-level Worker, mid-level Managers and bottom-level Handlers.

A Worker does the high-level task management and has two responsibilities: (1) retrieving/receiving the Task from the TB and (2) delegating the (parts of the) task to a suitable Manager.

A Manager does the low-level task management and has three responsibilities: (1) handle the main persistent results of in the task, such as writing to the database and communicating with agents, (2) publish the result of the task (success/failure), and (3) delegating the processing elements of the tasks to suitable Handlers.

Handlers do the computational parts of the tasks, for instance, constraint solving and potentially storing intermediary results of the task.
