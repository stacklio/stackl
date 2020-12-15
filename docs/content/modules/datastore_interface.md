---
title: Datastore Interface
kind: modules
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: true
tags: []
---

The Datastore Interface is the interface that allows pluggable backend data storage system for STACKL documents.
The implementation of the interface has to provide two things: (1) ensuring that the data is in a JSON-format when STACKL works on it and (2) that STACKL can uniformly access the data, translating its data access to the real data access in the underlying system.
Currently, STACKL offers two pluggable datastores: a local file system and a Redis datastore .
Future targets can be S3, MongoDB, YugabyteDB, and so on.

#### Local file system

The local file system datastore stores the files directly on the hard drive of the same machine as STACKL is deployed to.
It offers an easy deployment, requiring few additional resources, but relies directly on the STACKL machine.
As such, it has no redundancy, no advanced querying or caching capabilities and mediocre performance, requiring disk writes/reads.
However, it can be flexibly extended and use regular Linux tools for data and querying access.
In this sense, it is the most customizable system.

### Redis datastore

The Redis datastore is an in-memory, open-source data store that voids seek time delays and can access data in microseconds.
supports data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs, geospatial indexes with radius queries and streams. Redis has built-in replication, Lua scripting, LRU eviction, transactions and different levels of on-disk persistence, and provides high availability via Redis Sentinel and automatic partitioning with Redis Cluster.
Redis works with an in-memory data set.
Depending on the use case, it can persist data, either by dumping the data set to disk every once in a while, or by appending each command to a log.
Redis can also support master-slave asynchronous replication, with fast non-blocking first synchronization, auto-reconnection with partial resynchronization on net split.
As such, it is a quick and easy datastore for low amounts of data and readily accessible.

Read more about Redis on [redis.io](https://redis.io/).
