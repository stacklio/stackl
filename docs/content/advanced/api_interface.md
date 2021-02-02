---
title: API Interface
kind: advanced
weight: 2
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: true
tags: []
---

STACKL offers a REST API for interactions with operators.
The API is implemented using [FastAPI]<https://fastapi.tiangolo.com/> as a web framework, thereby offering a standards-based REST API based on Python type hints and high performance.
Interactions happen through API calls with associated parameters, either through curl commands in the command line interface or using the web interface (implemented through OpenAPI), using any browser.

STACKL exposes operations for most of its consitituent elements.
The three most important for regular queries, orchestration, and management are:

* Document operations
* Policy Agent operations
* Stack Instance operations

## Document operations

All operations related to documents of all types.
This interface serves two purposes: (1) to retrieve one or more documents and (2) to submit a document of a valid type for storing, modifying, or deleting.
These operations are expressly used to get, add, and delete documents and do nothing beyond that.
For instance, these can be used to add or change any configuration data (such as SITs, SATs or services).

## Policy Agent operations

All operations related to interacting with STACKL's policy agent.
This interface allows users to manually evaluate results of additional policies on their IT environment.

## Stack Instance operations

All operations related to stack instances.
This interface allows to instantiate your application as a stack instance on the provided description IT infrastructure (i.e., the SIT) and the provided modelling application description (i.e., the SAT).
In addition, it exposes operations to get, modify, or delete stack instances.

## Other APIs

In addition to these main ones, there are two categories of API endpoints: (1) to allow specifically manipulating documents of a type, such as functional requirements, services, SITs, SATs and policy templates, or (2) to explicitly interact with other components of STACKL, such as configurator tools and querying additional info about STACKL.

### Policy Template operations

All operations related to policy templates for storing and manipulation in STACKL.
To get, add or delete policy templates as pieces of config data in the datastore.

### TODO Add the rest - depending on how it evolves