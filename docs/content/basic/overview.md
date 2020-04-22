---
title: "Overview"
kind: basic
weight: 2
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

STACKL is a versatile platform that compliments your regular CI/CD workflow for application orchestration by tackling the complexity of configuring applications and deploying them on your suitable infrastructure.
The main concept of STACKL is that users should be able to flexibly **Model** their infrastructure and simply **Describe** their applications to allow STACKL to independtly **Automate** all the rest.

Users model their infrastructure and describe their applications using standardised JSON or YAML-based documents.
These documents are stored by STACKL in a pluggable Single Source of Truth datastore for further management and use.
Users can then easily give tasks to STACKL to orchestrate their applications or ask queries about their IT environment.
Tasks are processed by a pluggable and distributed task manager which will aim for its correct and eventually consistent completion and report back.
If needed, STACKL can contact pluggable user-side agents to execute parts of the task in the user's IT environment such as invocations on application orchestration tools.
Users are able to fine-tune the performance of their application orchestration automation strategy by providing multiple choices for pluggable modules as well as hiding the complexity associated with doing so.

The combination of a document-based Single Source of Truth datastores with a powerful task-based processing system and a technological backend built on pluggable modules provides an end-to-end transparent and flexible application orchestration that allows users to go back to their core focus: developing and using applications.

## Features

* STACKL works with YAML or JSON documents to allow for easy Key/Value management and future-proof cross-system compatibility
* STACKL provides a comprehensive REST API with a web interface that enables simple use and integration in a workflow
* Users create Stack Application Templates (SATs), which model and describe the desired applications, and Stack Infrastructure Templates (SITs), which specify the available IT infrastructure for the application.
SITs and SATs are processed according to their requirements and policies and result in a Stack Template, a Key/Value document that describes the state and workload placement of an application on the infrastructure
* Stack Templates can be instantiated to create Stack Instances, running applications in the users IT environment which are deployed and managed by orchestration tools through STACKL
* STACKL supports pluggable modules to allow users to use their desired technological backends.
For instance, the used data store and task processing solutions can be specified by the user
* STACKL allows easy extensions for new technological backends through providing interfaces that enable transparent interaction
* Entities, e.g., workers, automation platforms, and agents, are fully decoupled and distributable to improve fault-tolerance and scalability
* STACKL leverages current popular and best-in-class DevOps technologies and platforms: docker, kubernetes, ansible, azure, AWS, and so on, and is oriented towards the future, for instance, for serverless computing (FaaS/SaaS)
* Autonomous independent operation is a key focus: as much as possible, STACKL will manage and self-discover entities in the accessible IT environment to reduce load on users
* To allow rapid use of STACKL, it provides a minimal and fast setup on a regular computer for a normal user.
Button-press fire-and-forget deployment of STACKL enables users to take it for a quick spin

## Core goals

* End-to-end support for microservices-based applications and infrastructure management in a DevOps workflow through autonomous orchestration and management (interesting read: [What is DevOps?](https://www.atlassian.com/devops))
* Open source and community-oriented
  * Based on coding best practices
  * Consistent use of standards and guidelines
  * Clear documentation
  * Openness to community feedback and contributions
* Adaptable, flexible, general-purpose, and extensible
  * Integrates with a variety of pluggable modules including custom and no critical technology dependencies
  * Focus on working with current known and popular tools and softwares
  * Internally/externally uniform and accessible by using universal standards and terminology
  * Driven by specifiable policies to enable flexible orchestration
  * Coded with a clear and consistent design and using best-practice development guidelines
* Scalable, lightweight, and performant
  * Distributable across infrastructure and easy to scale
  * Able to make trade-offs to match different quality-of-service requirements
