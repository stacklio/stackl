---
title: Document Datastore
kind: advanced
weight: 2
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
A Datastore is the software system used by STACKL to store and process documents.
A document in STACKL is a file in either JSON or YAML format that models parts of the IT infrastructure, applications and services, and their configuration data.
The datastore is the place in STACKL that provides a single source of truth for application configuration data for IT enterprise environments.
The datastore is interacted with either directly, in the case of idempotent changes, or indirectly, by specifying a task STACKL processes through workers which make permanent changes to the datastore.
These changes are made by STACKL's document manager.

The datastore is a general module that can be chosen by the user when STACKL is deployed.
This makes it possible for the user to specify a variety of datastore systems, such as local file system, CouchDB, S3, and so on.
The choice for a datastore depends on the desired such as simplicity, scalability, reliability, cost, and so on.
Documents are in either JSON or YAML since YAML is a superset of JSON and they are a lightweight and common way to represent data, both for communication or configuration.

## Datastore design

The datastore is responsible for managing documents.
It performs three functions: (1) storing documents, (2) retrieving documents, and (3) running queries over its stored files.
The datastore is a pluggable module, chosen during the deployment of STACKL.
The pluggable module is accessed transparently through a general wrapper/interface.
Each plugged technology, whether custom or third-party, provides an implementation of this interface so that documents are always interacted with in the same way, independent from the backend, and only the performance characteristics change.

The datastore itself does not change documents but is interacted with in two ways: either for idempotent operations on documents, such as gets, or by workers during their handling of a task.
The documents are versioned in the datastore through git, independently of any versioning the underlying module might offer (WIP).
Any backend data storage system can be used so long as an interface is made.
The interface needs to provide two things: (1) ensure that the data is in a JSON-format when STACKL works on it and (2) that STACKL can uniformly access the data, translating its data access to the real data access in the underlying system.
Currently, STACKL implements a local file system as datastore.
Future targets can be CouchDB, S3, MongoDB, YugabyteDB, and so on.

See [Datestore Interface]({{< ref "../modules/datastore_interface.md" >}}) for information about the available modules and how to create your own.
