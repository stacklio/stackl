---
title: STACKL Glossary
navtitle: Glossary
kind: misc
weight: 16
---
## Automation Endpoint (AE)
Servers or containers that execute a client-side workflow for configuration and deployment of an application or service on a target machine. They contain the automation scripts and their corresponding orchestration tools (for example Ansible, Terraform, Packer, Powershell,…).

##Application (app)
Software entity, potentially distributed, that fulfills a larger use-case and results from linked (micro)services and the functional, non-functional and extra-functional requirements. In effect, the executing parts of a stack instance on the IT infrastructure.

##Services (srv)
Software entity that performs a small piece of functionality and has a clear set of service requirements. A constituent part of an application.

##Service Requirements
The functional and non-functional dependencies a service has so it performs as desired.

##Functional Requirements (FR)
The configuration packets required of the operating environment for the the service to perform its functions, such as a Linux OS, DNS or Web configuration, or nginx.

##Non-Functional Requirements	(NFR)
The hardware resource requirements to run the service such as CPU, memory, hard disk capacity, and so on.

##Extra-Functional Requirements (EFR)
Application requirements that go beyond runtime requirements of a single service, such as multiple service instantiations, latency links between services, security guarantees on subparts of the application or availability conditions.

##Stack
A declarative description of an application and the IT infrastructure it may run on.  It consists of a SAT and SIT but is not necessarily realisable. A realisable (i.e., solved) Stack is called an ST.

##Stack Application Template(SAT)
Template that models the application as a set of services with their requirements, links and any EFRs.

##Stack Infrastructure Template (SIT)
Template that models IT infrastructure as infrastructure targets originating from the environment, location, and zone and possessing a set of infrastructure capabilities.

##Infrastructure Targets
A part of the IT infrastructure, a virtual or physical entity capable of executing software (VM’s, desktop computers, …), that can be targeted to run services.

##Infrastructure Capabilities
A set of properties that the infrastructure has, such as specific software, CPU, memory, and so on.

##Stack Templates (ST)
Template that models a stack as a deployable set of services matched to suitable infrastructure targets. It contains all viable solutions resulting from merging the SAT and SIT at a certain point in time.

##Stack Instance (SI)
An instantiation of one of the viable solutions of a ST on the IT infrastructure.

##Task
An atomic unit of work, done completely or rolled back, given by a Producer to STACKL for processing. E.g., create a stack instance.

##Task Broker (TB)
The pluggable module in STACKL that manages the end-to-end life cycle of tasks ensuring they are done completely or rolled back

##Message Channel (MC)
The messaging system used by STACKL to communicate with other entities for processing tasks, such as Agents or Workers.

##Agent
Entities that take care of the client-side execution of tasks given to STACKL. This is mainly the instantiation of stacks instances through automation endpoints on the client’s IT infrastructure.

##Producer
The entity that gives work to STACKL. For instance, a user doing a REST API call through the web interface to create a stack.

##Worker
The entity that accepts or takes work, in the form of tasks, from STACKL and processes it to a desired state, including storing it or communicating it to other entities.

##Datastore
The pluggable storage module in STACKL that processes, retrieves and stores documents.

##Document
A JSON or YAML-based file with a specific type that models IT infrastructure building blocks, application service definitions, and their configuration data.

##Items
Category of types for documents that represent a tangible part of the clients IT domain. This can be infrastructure targets, services, or applications/stack-instances and is the result of the hierarchical key/value merging of its constituent sub-parts. For instance, an infrastructure target is the result of an environment, location and zone with a certain hierarchical relationship.

##Configurations
Category of types for documents that model elements related to the clients IT domain. Such as allowed types, authentication documents, etc.

#Deprecated Terminology
Resources 	→ Services, inline with the microservice architecture approach
Roles 		→ Functional Requirements (i.e., configuration packets for machines so that they can perform certain functions)
Shape 		→ Non-Functional Requirements
Proxy 		→ Now Agents
