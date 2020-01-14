---
title: "Introduction"
kind: basic
weight: 1
---

**STACKL** is an open-source software platform that enables users to flexibly model, describe, and automate their application orchestration.

STACKL supports the autonomous configuration, coordination, and management of applications and IT infrastructure by:

* forming the Single Source of Truth (SSOT) configuration data lookup store for your IT environment including infrastructure resources, application definitions, and their characteristics and services
* decoupling configuration data, automation strategy, and deployment targets thereby simplifying the automated infrastructure management for code and configuration tooling
* providing pluggable modules for backend systems, such as processing and data storage, to support different scalability and performance requirements and enable users to choose their prefered tools

In essence, it allows to ***Model***, ***Describe***, and ***Automate*** your application orchestration workflow. Users are saved from  manual work each time they want to deploy their projects by automating and simplifying IT infrastructure selection, application specification, and choosing suitable orchestration tools. Users now simply model their available infrastructure, describe their desired applications, and specify the desired orchestration tools once. STACKL then transparantly and autonomously uses this information to correctly and efficiently orchestrate and automate applications in the available IT environment across their lifetime and managing dynamic changes.

See [STACKL slides](https://drive.google.com/open?id=10ZmqGU3pOc6EJyZpED4fMgav5pD01RztLkfSn3Jl9EA) for a short presentation about STACKL.

<!-- **Features**

Visuals (Tools like [ttygif](https://github.com/icholy/ttygif) can help, but check out [Asciinema](https://asciinema.org/) for a more sophisticated method) -->

## Core goals

* Open-source and community-oriented
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

## Features

* STACKL works with YAML or JSON documents to allow  for easy Key/Value management and uture-proof cross-system compatibility
* STACKL provides a REST API with a web interface
* Users supply Stack Application Templates (SATs), which model and describe the desired applications, and Stack Infrastructure Templates (SITs), which specify the IT infrastructure available for use for the application. SITs and SATs can be processed and matched according to specified policies and result in a Stack Template, a Key/Value document that describes the desired state of an application on the infrastructure and can be deployed in the users IT environment by orchestration tools
* STACKL supports pluggable modules to allow users to use their desired technological backendsL. For instance, the used data store and task processing solutions can be specified by the user
* STACKL is engineered to allow easy extensions for new technological backends through providing interfaces that enable transparent interaction
* Entities, i.e., workers, automation platforms, agents, … ,  are fully decoupled and can be distributed to improve fault-tolerance and scalability.
* The deployment and use of STACKL works with popular DevOps technologies and platforms: docker, kubernetes, ansible, azure, AWS, and is oriented towards the future, for instance, for serverless computing (FaaS/SaaS).
* Autonomous operation is a key focus: as much as possible, after deployment of STACKL, the system and its entities will self-manage and self-discover
* To allow rapid use of STACKL, it provides a minimal and fast setup on a regular computer for a normal user. Button-press fire-and-forget deployment of STACKL enables users to take it for a quick spin.



## Contributing

Contributions, issues, and feature requests are always more than welcome! Feel free to check [issues page](https://github.com/kefranabg/readme-md-generator/issues) if you want to contribute.

See [CONTRIBUTING](../CONTRIBUTING) to get started.

Please also read the [CODE_OF_CONDUCT](../CODE_OF_CONDUCT).


## License

The code in this project is licensed under the [GLPv3](../LICENSE) license.
