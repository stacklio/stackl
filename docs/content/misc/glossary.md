---
title: Glossary
navtitle: Glossary
kind: misc
weight: 3
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

This section provides a glossary of commonly used terms, and their abbreviations, in STACKL.

##### Automation Endpoint (AE)

Servers or containers that execute a client-side workflow for configuration and deployment of an application or service on a target machine.
They contain the automation scripts and their corresponding orchestration tools (for example Ansible, Terraform, Packer, Powershell, …).

##### Application (app)

The entirety of a software entity, potentially distributed, that fulfills a larger use-case as a collection of loosely coupled services.
In reality, the running representation of a stack instance on the users IT infrastructure.

##### Services (srv)

A software entity that performs a clear function as a part of an application and which has a set of service requirements.

##### Service Requirements

The functional and resource requirements a service has so it can perform its function.

##### Functional Requirements (FR)

The configuration packages required of the operating environment (an infrastructure target) for the the service to perform its functions, such as a Linux OS, DNS or Web configuration, nginx, a local datastore requirement, ... .

##### Resource Requirements (RR)

The resource requirements to run the service such as CPU, memory, hard disk capacity, and so on.

##### Policies (POL)

Used for either applications or infrastructure targets.
For applications, they describe application requirements that give additional specifications for how the collection of services function together and other application-level requirements.
These map to behavioral constraints on and across services, such as high availability of a service through redundancy, a low latency requirement between two services or strict security conditions.
For infrastructure targets, they model additional requirements of the IT environment, such as exclusivity in hosting for a highly available target.

##### Stack

A Stack is a declarative description of an application and the IT infrastructure it may run on.
Stacks are a conceptual element that describes the desired orchestration of an application in the IT environment.
SATs, SITs, STs and SIs are stored documents which are given, processed, tracked, and maintained in the datastore and represent the parts and stages of a Stack.

##### Stack Application Template(SAT)

Template that describes the application as a set of services and policies.

##### Stack Infrastructure Template (SIT)

Template that models the  IT infrastructure originating from the provided environments, locations, and zones.
It gives a list of deployable infrastructure targets possessing a set of infrastructure capabilities and any policies.

##### Infrastructure Targets

A part of the IT infrastructure, a virtual or physical entity capable of executing software (clusters, VMs, desktop computers, ...), that can be targeted to run services.

##### Infrastructure Capabilities

A set of properties that the infrastructure has, such as specific software packages, CPU, memory, and so on, and which are used to determine its suitableness for hosting a service.

##### Stack Templates (ST)

Template that models a stack as a deployable set of services matched to suitable infrastructure targets.
It contains all viable solutions that result from matching the requirements of a SAT to the requirements and capabilities of a SIT at a certain point in time.

##### Stack Instance (SI)

An instantiation of one of the viable solutions of a ST on the IT infrastructure, representing a real-life running application.

##### Task

An atomic unit of work, done completely or rolled back, given by an Operator to STACKL for processing.
E.g., create a stack instance.

##### Task Broker (TB)

The pluggable module in STACKL that manages the end-to-end life cycle of tasks ensuring they are done completely or rolled back.

##### Message Channel (MC)

The messaging backend used by STACKL to communicate with workers for processing tasks.

##### Agent

Entities with access to the user's IT environment that manage the user-side aspects of tasks given to them by workers from STACKL, such as the instantiation of stacks instances through automation endpoints.

##### Operator

The entity that gives work to STACKL.
For instance, a user doing a REST API call through the web interface to create a stack.

##### Worker

The entity that accepts or takes work, in the form of tasks, from STACKL and performs the desired actions, such as storing documents or instantiating stacks.

##### Datastore

The pluggable storage module in STACKL that processes, retrieves, and stores documents.

##### Document

A JSON or YAML-based file with a specific type that models IT infrastructure building blocks, application service definitions, and their configuration data.

##### Items

Category of types for documents that are tangible elements of a user's IT environment, namely files that are actionable or represent an interactive entity, and commonly form the data that serves as input for orchestration tools.

##### Configurations

Category of types for documents that model or describe elements or concepts of the user's IT environment and are files that by themselves are not actionable but serve as configuration.
