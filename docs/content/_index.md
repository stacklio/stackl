---
title: "Introduction"
kind: basic
weight: 1
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags:
  - open-source
  - SSOT
  - configuration management
  - infrastructure automation
  - DevOps
  - orchestration
---

**STACKL is an open-source software platform that enables users to flexibly model, describe, and automate their application orchestration.**
Writing good application code is difficult enough.
But then successful continuous integration and delivery of your app in your IT infrastructure opens up a whole other can of worms.
What other services do you need for your app? Where do you deploy them? Which IT resources can you use to test your development app? Which are optimal to run your production app?
Even more: how do you deploy your application? What orchestration tools do you use? Does it have the authorization to access your resources? How do you manage the app after deployment?
You started off with the honest desire to just write some good code and now reality hits you with all kinds of concerns you want nothing to do with. That is where ***STACKL*** comes into play.

STACKL supports the autonomous configuration, coordination, and management of applications and IT infrastructure by:

* Forming the Single Source of Truth (SSOT) configuration data lookup store for your IT environment including infrastructure resources, application definitions, and their characteristics and services.
* Decoupling configuration data, automation strategy, and deployment targets thereby simplifying the automated infrastructure management for code and configuration tooling.
* Providing pluggable modules for backend systems, such as processing and data storage, to support different scalability and performance requirements and enable users to choose their prefered tools.

In essence, it allows to ***Model***, ***Describe***, and ***Automate*** your application orchestration workflow.
Users are saved from  manual work each time they want to deploy their projects by automating and simplifying IT infrastructure selection, application specification, and choosing suitable orchestration tools. Users now simply model their available infrastructure, describe their desired applications, and specify the desired orchestration tools once.
STACKL then transparently and autonomously uses this information to correctly and efficiently orchestrate and automate applications in the available IT environment across their lifetime and manage dynamic changes.
Button-press fire-and-forget application orchestration according to the specific desire of the user and the current use-case becomes tractable and easy which allows users to focus better on producing and using their apps.

See [STACKL slides](https://drive.google.com/open?id=10ZmqGU3pOc6EJyZpED4fMgav5pD01RztLkfSn3Jl9EA) for a short presentation about STACKL.