---
title: Datastore Interface
kind: modules
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

Any backend data storage system can be used so long as an interface is made.
The interface needs to provide two things: (1) ensure that the data is in a JSON-format when STACKL works on it and (2) that STACKL can uniformly access the data, translating its data access to the real data access in the underlying system.
Currently, STACKL implements a local file system as datastore.
Future targets can be CouchDB, S3, MongoDB, YugabyteDB, and so on.

#### Local file system

The local file system datastore stores the files directly on the hard drive of the same machine as STACKL is deployed.
It offers an easy deployment, requiring few additional resources, but is directly reliant on the STACKL machine.
As such, it has no redundancy, no advanced query or cache capabilities and mediocre performance, requiring disk writes/reads.
However, it can be flexibly extended and use regular Linux tools for data and querying access.
In this sense, it is the most customizable system.
