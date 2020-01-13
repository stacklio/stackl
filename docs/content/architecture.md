---
title: Architecture
kind: documentation
weight: 1
---

This document describes the high-level architecture of STACKL, referring to additional other documents for further explanation. The architecture enables users to flexibly and easily model, describe, and automate their application orchestration workflow.

This workflow is supported as follows:

- A producer, a user that submits tasks to STACKL, uses STACKL as a tool to model, describe, and automate applications by using it as (1)  a datastore of application configuration and infrastructure model data and (2) a platform that uses this data to provide autonomous application orchestration.
- Authorized producers interact through an API specification to submit tasks. Tasks are mainly submitting documents that model the IT environment and describe applications and the instantiation of applications.
- Tasks are executed in STACKL through pluggable modules for authorization, storage, processing, automation endpoint execution, and monitoring and reporting.
-  STACKL thus has a Single Source Of Truth (SSOT) datastore that contains the information to provide end-to-end application orchestration for users.

## Diagram

![Alt](images/architecture_stackl.drawio)


## Description
This section briefly describes each explicit element in [Diagram](#diagram) and its responsibilities.

A **producer** is an entity that uses the STACKL API to make requests and receives the result or a confirmation in return. Requests can be queries for information, retrieving documents, storing or changing documents, and using documents for application orchestration. A producer can be anything that is capable of issuing HTTP requests, including other tools or actual users.

The **API Interface** is a frontend for access to STACKL and ensures requests are authorized, submitted to STACKL and the result delivered back to the requester. This API is based on HTTP and REST and also provides a web frontend.

The **Authorization Module** ensures that requests for STACKL are both allowed and delegated to the correct parties. This is a WIP that is intended to be offloaded to policy-driven system managed by an Open Policy Agent.

The **Task Broker** and **Workers** take requests in the form of tasks and take care of the correct, consistent, and timely end-to-end processing of the work therein.  This includes delegating it to multiple workers for horizontal scalability , reporting the result of the work, rolling back any changes in case of failure and interacting with third parties, such as agents, if needed. Workers contain the core logic needed to process the work, such as constraint solving and matching application requirements and infrastructure capabilities.

The **Document Datastore** stores and provides documents for workers to execute their tasks. It ensures documents are consistent, have a type, and thus forms a SSOT to model an IT enterprise environment and  application configuration data.

The **Monitoring Module** assists in the monitoring, logging, and maintenance of the IT enterprise environment and how it is modelled in the document datastore. It interacts with the task broker and agents to ensure both are consistent and queryable. This is a WIP that is intended to be offloaded to policy-driven system managed by an Open Policy Agent.

The **Agent Broker** and **Agents** enable STACKL to execute work and queries in a (remote) IT enterprise environment. The Agent Broker is an interface that allows to interact with the client-side agents. These agents there do the further processing of the work, such as executing invocations on automation endpoints.
