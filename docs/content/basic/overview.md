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
The main concept of STACKL is that users should be able to flexibly **Model** their infrastructure and simply **Describe** their applications to allow STACKL to autonomously **Automate** all the rest.

Users model their infrastructure and describe their applications using standardised JSON or YAML-based documents.
These documents are stored by STACKL in a pluggable Single Source of Truth datastore for further management and use.
Users can then easily give tasks to STACKL to orchestrate their applications or ask queries about their IT environment.
Tasks are processed by a pluggable and distributed task manager which will aim for its correct and eventually consistent completion and report back.
If needed, STACKL can contact pluggable user-side agents to execute parts of the task in the user's IT environment such as invocations on application orchestration tools.
Users are able to fine-tune the performance of their application orchestration automation strategy by providing multiple choices for pluggable modules as well as hiding the complexity associated with doing so.

The combination of a document-based Single Source of Truth datastores with a powerful task-based processing system and a technological backend based on pluggable modules provides an end-to-end transparent and flexible application orchestration that allows users to go back to their core focus: writing and using applications.

## Features

* STACKL works with YAML or JSON documents to allow for easy Key/Value management and future-proof cross-system compatibility
* STACKL provides a REST API with a web interface
* Users supply Stack Application Templates (SATs), which model and describe the desired applications, and Stack Infrastructure Templates (SITs), which specify the IT infrastructure available for use for the application.
SITs and SATs are processed and matched according to specified policies and result in a Stack Template, a Key/Value document that describes the desired state of an application on the infrastructure and can be deployed in the users IT environment by orchestration tools
* STACKL supports pluggable modules to allow users to use their desired technological backends.
For instance, the used data store and task processing solutions can be specified by the user
* STACKL is engineered to allow easy extensions for new technological backends through providing interfaces that enable transparent interaction
* Entities, i.e., workers, automation platforms, agents  are fully decoupled and can be distributed to improve fault-tolerance and scalability.
* The deployment and use of STACKL works with popular DevOps technologies and platforms: docker, kubernetes, ansible, azure, AWS, and so on and is oriented towards the future, for instance, for serverless computing (FaaS/SaaS).
* Autonomous operation is a key focus: as much as possible, after deployment of STACKL, the system and its entities will self-manage and self-discover
* To allow rapid use of STACKL, it provides a minimal and fast setup on a regular computer for a normal user.
Button-press fire-and-forget deployment of STACKL enables users to take it for a quick spin.

## Core goals

* Open source and community-oriented
  * Based on coding best practices
  * Consistent use of standards and guidelines
  * Documented
* Adaptable, flexible, general-purpose, and extensible
  * Integrates with a variety of pluggable modules including custom and no critical technology dependencies
  * Focus on working with current known and popular tools and softwares
  * Internally/externally uniform and accessible by using universal standards and terminology
  * Driven by specifiable policies to enable flexible orchestration
* Scalable, lightweight, and performant
  * Distributable across infrastructure and easy to scale
  * Able to make trade-offs to match different quality-of-service requirements
* End-to-end support for microservices-based applications and infrastructure management in a DevOps workflow (interesting read: [What is DevOps?](https://www.atlassian.com/devops))
