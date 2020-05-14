---
title: Message Channel Interface
kind: modules
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

(TODO) Work in progress

The message channel can be any messaging middleware that can spread data.
There are many systems that can do this.
A minimal set for the MVP of STACKL are Redis and either RabbitMQ or Kafka.

The message channel has to be able to provide messages to workers and process them transparently:

* Temporarily store messages
* Publish/subscribe
* Push/Pop system
* Process the communicated data so that the input and output are json files

#### Redis

Redis provides a simple in-memory datastore/message queue that allows publish/subscribe communications as well as pushing/popping messages.
