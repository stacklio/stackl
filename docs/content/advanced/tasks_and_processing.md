---
title: Task System
kind: advanced
weight: 3
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

STACKL is a task-based system that performs work for producers through wrapping their requests in atomic and distributable tasks in an asynchronous design. 
Through this system, STACKL maintains consistency, failure resilience, scalability, and enforceable time constraints whatever happens in the IT environment so that users are never blocked or left with an unstable system.
This is critical in todays highly variable IT enterprise infrastructure with different requirements and many possible configurations.

The task system is therefore designed with the following core properties:

* Task processing scalability and performance
    * Tasks are distributable for processing to a scalable task processing module or to vertically scaling workers
    * Tasks are non-blocking and specifically time-bound
    * Producers are never left undeterminably waiting on a task but either directly notified within a certain timebound of the result or given the location of the eventual result report 
* Data consistency
    * All work done for producers is done through tasks
    * Tasks acquire atomic locks on data they are working on (TODO WIP)
    * Tasks are done completely or not at all, being rollbacked (atomic operation)
* History
    * Tasks are tracked in a queue in which their lifecycle is managed, from beginning until success or failure
    * The result of tasks are stored (TODO WIP)
    * The state of the elements that the task changes are stored as snapshots 
* Failure resilience
    * Rollbacks are done if a task is not succesfully completed, through the history and snapshots
    * Tasks remain in the queue until they either produce a succesful, success or failure, or a time-out
    * If a task fails or timeouts, a rollback task is executed, undoing all the changes the task made

## Overview of Task System Design

The task system is based on five decoupled elements: the API, tasks, task brokers, task processing through a pluggable module or workers, and a history datastore.
How they work togheter is illustrated in the below figures.
Each element is tackled in-depth in a separate section.

The **API** enables producers to make requests.
The API does not contain any logic but wraps the request into a STACKL understandable **Task** and either starts an asynchronous time-bound wait on the task result or notifies the producer where the request result can be found.
Critically, in this way, there is no logic in the API at all - all it does is task creation, submission, and reporting.
The task is given to STACKL's **Task Broker** who starts tracking the task by putting it into a task queue and then distributes it, either through a pluggable **Task Processing Module** or itself through a pluggable message channel to **workers**.
The task broker tracks the task until it receives a result from the module or a worker or until the timeout of the task expires. 
During the processing of the task, any changes made to STACKLs data require the data item to be first snapshot and stored in the **History Datastore** and then atomically locked during the processing. 
Once either occurs, the result (success or failure) is is stored in the history datastore and also reported back if there is a asynchronously waiting API, depending on the task.
If the result was a failure, either due to faulty processing or a timeout, it is rollbacked by STACKL using the files in the history database so that STACKL and the IT environment are restored back to their initial state.
In this way, STACKL achieves eventual consistency between its representation of the user’s IT environment (through documents) and the actual user’s IT environment (i.e., instantiated applications and accessible infrastructure).

{{< figure src="task_processing_overview.png" width="70" caption="DEPRECATED Task processing overview" >}}
{{< figure src="task_processing_flow.png" width="90" caption="DEPRECATED Task processing flow" >}}

STACKL uses pluggable modules for the task broker; which manages the tasks, for the message channel; for communicating tasks with workers, and for the workers, to allow for different types of logic engines.
Modules allow the use of different task broker systems (e.g., custom implementations, Celery, Faust, ...), message channels, (e.g., Redis, RabbitMQ, Kafka, ...) and worker systems (e.g., custom containers, FaaS, ...) .
The choice of module determines the performance characteristics of STACKL task processing, such as simplicity, scalability, reliability, cost, and so on.

## The API and Tasks

This section discusses how the API interacts with the task system.
The API interface itself is discussed in [API Interface](api_interface.md).

Each request made to STACKL's API is transformed into an atomic task object that contains all the necessary data contained in the request, including its type, subtype, and any arguments or other data.
This task is then given to the task broker where it will be processed until either a mandatory timeout expires, it is processed succesfully, or has to be rollbacked.
Depending on the request, the API will either starts asynchronously waiting on the result of the task, waiting until the timeout in the worst case, or is immediately given the future location where the result of the request may be reviewed.

There is no computational logic in the API and it is completely asynchronous and decoupled from the task processing and will not block.
If the task should normally be done relatively soon, it justs awaits the result of the task asynchronously, allowing other work to be done in the meantime by the program and ensure a bounded waiting time.
Alternatively, if the task duration is long, it will not wait but simply allow the result of the task to be examined at a later point in time.
There is still a mandatory timeout in this case which will stop and rollback the task if exceeded, to avoid tasks from returning results long after they are relevant.
Accordingly, eventual consistency between the producer, his requests, the IT environemnt, tasks, and the internal datastore, is maintained and specificiable by a timeout.


## Tasks

Tasks are atomic units of work made by STACKL to correctly handle requests.
They are the basis on which STACKL can model, describe, and automate a clients IT environment while maintaining scalability, consistency, and accurate result reports.
The lifetime of a task is from the time of the request until a mandatory timeout or a result-based completion. 
Critical for STACKL is the principle of eventual consistency: either all actions in tasks are performed correctly and completely, including in the IT environment and STACKL's datastore, or it fails, due to a timeout or failure result, and all made changes are rolled back to the previous state.
Once the desired state is achieved or rolled back and this is correctly represented in STACKL and is consistent, the task is removed.

Tasks have the following properties:

* **Atomicity:** Done entirely or not-at-all
* **Id:** A task has a unique identifier
* **Timeout:** A task has timeout which is monitored from the moment it is available to be done
* **Source:** A task has a source, the entity which made the initial request
* **Topics:** What the task is about
* **Subtype:** The subtype related to the topic, what the task needs to do within the topic domain
* **Self-contained:** A task contains all the info needed to execute it at processing time, to allow for workers to be stateless and simplifying rollback. This can be in additional arguments or included documents

### Task Topics

<!-- TODO

Stack Task

Result Task

Document Task -->

## Task Broker

<!-- The Task broker manages tasks atomically: done completely or rolled-back.
It is a pluggable module that is chosen during the deployment of STACKL.
The pluggable module is accessed transparently through a general wrapper/interface, the  task broker interface.
A pluggable task broker implements this interface so that tasks are always interacted with in the same way, independent from the backend, and only the performance characteristics change.
The task broker itself does not process tasks but only manages them.

It accepts the tasks from producers and communicates them to workers.
Before delegating tasks for processing, it may add additional information such as communication parameters so that the task is self-contained.

See [Task Broker Interface]({{< ref "../modules/task_broker_interface.md" >}}) for information about the available modules and how to create your own. -->


## Task Processing Module

### Message Channel

<!-- The message channel is the medium through which STACKL communicates with other parties during the processing of a task.
It is a pluggable module that is chosen during the deployment of STACKL.
The pluggable module is accessed transparently through an interface, the message channel interface.
Each plugged technology, whether custom or third-party, provides an implementation of this interface so that from tasks are communicated in the same way, independent from the backend, and only the performance characteristics change.

See [Message Channel Interface]({{< ref "../modules/message_channel_interface.md" >}}) for information about the available modules and how to create your own. -->

### Workers

<!-- Workers are software entities that process the tasks and function as self-contained logic engines.
Workers are stateless, able to communicate with STACKL and agents, and able to execute the actions described in a task.
This allows horizontal scalability and to keep the concept of a worker general for extensibility.

Currently, workers are containers that use various handlers and managers implemented in STACKL to process tasks.
For the processing of tasks, they have to be able to:

* Retrieve it from the task broker
* Do processing on key/value documents
* Report back a result
* Communicate with agents
* Access the database -->

#### Worker containers

<!-- Workers, when implemented as containers, use several parts of the codebase of STACKL to manage tasks.
There is a hierarchical processing structure based on responsibilities which consists of the top-level Worker, mid-level Managers and bottom-level Handlers.

A Worker does the high-level task management and has two responsibilities: (1) retrieving/receiving the Task from the TB and (2) delegating the (parts of the) task to a suitable Manager.

A Manager does the low-level task management and has three responsibilities: (1) handle the main persistent results of in the task, such as writing to the database and communicating with agents, (2) publish the result of the task (success/failure), and (3) delegating the processing elements of the tasks to suitable Handlers.

Handlers do the computational parts of the tasks, for instance, constraint solving and potentially storing intermediary results of the task. -->

## History Datastore