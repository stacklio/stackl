---
title: OPA Server
kind: advanced
weight: 5
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

STACKL uses an open source, general-purpose policy engine, called Open Policy Agent (OPA), to offload policy enforcement and decision making for applications, infrastructue, and authorization and authentication.
OPA, available from [https://www.openpolicyagent.org/](https://www.openpolicyagent.org/),  is a powerful and flexible open-source tool that uses a high-level declarative language to specify policy as code and offers a simple APIs to offload policy decision-making.
OPA is commonly used to enforce policies in microservices, Kubernetes, CI/CD pipelines, API gateways, and more.
STACKL integrates OPA to offload queries for decision making based on the user's IT environment and input, which may be certain policies, application placement, authorization, and so on.