---
title: Task Broker Interface
kind: modules
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---


(TODO) Work in progress

There are many systems that manage tasks.
STACKL should support a custom simple implementation and either Celery or Faust.

Other targets or ideas can be found:

* <https://taskqueues.com/> and <http://queues.io/>
* Gevent (concurrency) <http://charlesleifer.com/blog/ditching-the-task-queue-for-gevent/>

Producers have to be able to:

* Give a task to the task broker

## Custom Task Broker

The Custom TB accepts tasks and puts them in a monitoring task queue and submits it to the MC.
The task queue keeps track of all the tasks by monitoring their timeout and changing their status based on worker results. If a task has failed (due to a time out or a negative result task), the TB does a rollback of the task and removes it from the queue. If a task has succeeded, it is removed from the queue.
