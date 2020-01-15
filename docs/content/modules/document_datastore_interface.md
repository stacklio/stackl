---
title: Document Datastore
kind: modules
weight: 2
---
A Datastore is the software system used by STACKL to store and process documents.
A Document in STACKL is a file in either JSON or YAML format that models parts of the IT infrastructure, applications and services, and their configuration data. The datastore is the piece in STACKL that forms the single source of truth for application configuration data for IT enterprise environments. The datastore is interacted with either directly, in the case of idempotent changes, or indirectly, by specifying a task STACKL processes through workers which make permanent changes to the datastore. These changes are made by STACKLs document manager.

The datastore is a general module that can be chosen by the user when STACKL is deployed. This makes it possible for the user to specify a variety of datastore systems, such as local file system, CouchDB, S3, and so on. The choice for a datastore depends on the desired such as simplicity, scalability, reliability, cost, and so on.
Documents are in either JSON or YAML since YAML is a superset of JSON and they are a lightweight and common way to represent data, both for communication or configuration.

## Document design
Documents are the basic units of data in STACKL. These are text files that model the IT enterprises infrastructure, application service definitions and its configuration data. An authorised Producer can give, change, delete and retrieve documents to either add, change or query IT resources and execute their automation strategy enabling infrastructure as code and configuration management tooling. Documents are communicated by Producers in either JSON or YAML formats and are always internally converted to JSON. Documents are used by STACKL as the data to fulfil use cases.

There are four broad groups of documents that the datastore has to manage: (1) related to infrastructure building blocks, (2) related to users, (3) related to applications, and (4) related to stacks (templates and instances). The first category, infrastructure documents, specify the IT infrastructure. The types in this category are hierarchical, going from conceptual areas down to the specific machine. The types, in order, are: environment, location, and zone. The combination of these three uniquely specify a potential infrastructure resource for deploying code. The second category, user documents, specify the IT infrastructure users and serves for authentication purposes. The third category, application documents, describe applications, their constituent services, and their requirements. The types in this category are: service, functional requirements and non-functional requirements. A service is always specified in terms of its functional and non-functional requirements. The fourth category, stack documents, further explained in Stack Templates, model the combination of infrastructure documents and application documents, to provide actionable and instantiable templates to execute automation strategies on and with or for users as specified in the user documents. The types within these groups fall in either the configs category or items category, see Document Types.

## Datastore design
The datastore has the responsibility of managing documents. It needs to be able to do three things: (1) store documents, (2) retrieve documents, and (3) run a set of limited queries over its stored files. The datastore is a pluggable module, chosen during the deployment of STACKL. The pluggable module is accessed transparently through a general wrapper/interface. Each plugged technology, whether custom or third-party, provides an implementation of this interface so that documents are always interacted with in the same way, independent from the backend, and only the performance characteristics change.

The datastore itself does not change documents but is interacted with in two ways: either for idempotent operations on documents such as gets or by workers during their handling of a task. The documents are versioned in the datastore through git, independently of any versioning the underlying module might offer (WIP). Any backend data storage system can be used so long as an interface is made. The interface needs to provide two things: (1) ensure that the data is in a JSON-format when STACKL works on it and (2) that STACKL can uniformly access the data, translating its data access to the real data access in the underlying system. A minimal set for the MVP of Stackl are a local file system and couchDB. Future targets can be S3, MongoDB, YugabyteDB, and so on.

### Modules

#### Local File System
The local file system (LFS) datastore stores the files directly on the hard drive of the same machine as STACKL is deployed. It offers an easy deployment, requiring few additional resources, but is directly reliant on the STACKL machine. As such, it has no redundancy, no advanced query or cache capabilities and mediocre performance, requiring disk writes/reads. However, it can be flexibly extended and use regular Linux tools for data and querying access. In this sense, it is the most customizable system.

## Design Considerations
The above design is a potential approach with the following questions or considerations to take into account:

* Do we want dynamically changeable databases? This can be handy in multiple instances: point towards a new couchdb (that would be easy) or a new different store (that would be possible but slightly more difficult). In theory, it could be possible or interesting to work with swappable datastores and/or multiple systems.
