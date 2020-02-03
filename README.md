# STACKL
<!-- Badges come here -->
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](code-of-conduct.md)
**STACKL** is an open-source software platform that enables users to flexibly model, describe, and automate their application orchestration.
STACKL supports the autonomous configuration, coordination, and management of applications and IT infrastructure by:
* forming the Single Source of Truth (SSOT) configuration data lookup store for your IT environment including infrastructure resources, application definitions, and their characteristics and services
* decoupling configuration data, automation strategy, and deployment targets thereby simplifying the automated infrastructure management for code and configuration tooling
* providing pluggable modules for backend systems, such as processing and data storage, to support different scalability and performance requirements and enable users to choose their prefered tools
In essence, it allows to Model, Describe, and Automate your application orchestration workflow. Users are saved from  manual work each time they want to deploy their projects by automating and simplifying IT infrastructure selection, application specification, and choosing suitable orchestration tools. Users now simply model their available infrastructure, describe their desired applications, and specify the desired orchestration tools once. STACKL then transparantly and autonomously uses this information to correctly and efficiently orchestrate and automate applications in the available IT environment across their lifetime and managing dynamic changes.
<!-- **Features**
Visuals (Tools like [ttygif](https://github.com/icholy/ttygif) can help, but check out [Asciinema](https://asciinema.org/) for a more sophisticated method) -->
# :rocket:Installation
This section includes a quick guide to what is required, how to install, and how to do a first test run.
## Prerequisites
* Kubernetes environment
* Helm 3
* Kubectl
## Installing
* Clone the helm repository URL TO THE GIT TBI (to be implemented)
* Create a namespace that will house the STACKL deployment
* Execute the following command: `helm install <name> <path to local STACKL helm repository folder> -n <namespace>`
This will deploy STACKL and all of its components in the active k8s context.
## Getting started
For this example we will create a SIT (Stack Infrastructure Template) and a SAT (Stack Application Template). We will use this to deploy an application defined in the SAT on the environment specified in the SIT.
### Configuration
#### What is a Stack Infrastructure Template
A stack infrastructure template specifies which IT Infrastructure is available to the application deployment. An SIT needs the following components (documents):
* Environment

  example JSON:
```json
{
    "description": "Production environment",
    "type": "environment",
    "name": "production",
    "hostname": "vsphere.local",
    "username": "administrator@vsphere.local",
    "password": "supersecurepassword123!",
    "datastore": "vsanDatastore"
}
```
* Location

```json
{
    "description": "Brussels DC",
    "type": "location",
    "name": "brussels",
    "datacenter": "DC01"
}
```
* Zone

```json
{
    "description": "Our First Cluster",
    "type": "zone",
    "name": "cluster1",
    "cluster": "CL01",
    "CPU": "4GHz",
    "RAM": "4GB",
    "config": [
        "linux",
        "nginx"
    ],
}
```
* Stack Infrastructure Template
We can combine the above documents into the SIT
example:
```json
{
    "category": "configs",
    "description": "sit updated at 2020-01-30 10h38m46s",
    "environment": [
        "production"
    ],
    "infrastructure_capabilities": {},
    "infrastructure_targets": [
        "production.brussels.cluster1"
    ],
    "location": [
        "brussels"
    ],
    "name": "stackl",
    "parameters": {},
    "subcategory": "SIT",
    "type": "stack_infrastructure_template",
    "zone": [
        "cluster1"
    ]
}
```
#### What is a Stack Application Template
Stack application templates are templates that define an application. It consist out of the following components: 
* Functional requirement

```json
{
    "category": "configs",
    "description": "type functional_requirement with name linux",
    "invocation": {
        "description": "installs centos",
        "image": "nexus-dockerint.dome.dev/stackl/terraform-vm",
        "tool": "terraform"
    },
    "name": "linux",
    "params": {
        "aws_ami": "ami-12345",
        "vmw_image": "centOS8-template"
    },
    "type": "functional_requirement"
}
```
* Service

```json
{
    "name": "webserver",
    "type": "virtual_machine",
    "functional_requirements": ["linux"],
    "non_functional_requirements": {
        "CPU": "1GHz",
        "RAM": "2GB"
    },
    "params": {
        "webserver": "nginx"
    }
}
```
* Stack Application Template
```json
{
    "name": "web",
    "type": "stack_application_template",
    "services": ["webserver"],
    "extra_functional_requirements": {},
    "service_policies": {
        "webserver": {
            "replicas": 2,
            "policies": ["opa_policy1", "opa_policy2"]
        }
    }
}
```
### Uploading the documents to STACKL

Go to the STACKL web interface, (use `kubectl get service` to get the IP address). use the `/documents/{type_name}` endpoint to POST the documents using the correct type.

### Create stack instances

Use the following payload:

```
{
  "parameters": {
    "replicas": "1",
    "vm_name": "stackl_vm"
  },
  "infrastructure_template_name": "stackl",
  "application_template_name": "web",
  "stack_instance_name": "web_example_stack1"
}
```

and make a POST-request to /stack/instances, this will instantiate a stack instance and will create a Virtual Machine.

You can then see the status of the stack instance by using the /stack/instances/web_example_stack1 endpoint.

# More info about STACKL
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
- STACKL works with YAML or JSON documents to allow  for easy Key/Value management and uture-proof cross-system compatibility
- STACKL provides a REST API with a web interface
- Users supply Stack Application Templates (SATs), which model and describe the desired applications, and Stack Infrastructure Templates (SITs), which specify the IT infrastructure available for use for the application. SITs and SATs can be processed and matched according to specified policies and result in a Stack Template, a Key/Value document that describes the desired state of an application on the infrastructure and can be deployed in the users IT environment by orchestration tools
- STACKL supports pluggable modules to allow users to use their desired technological backendsL. For instance, the used data store and task processing solutions can be specified by the user
- STACKL is engineered to allow easy extensions for new technological backends through providing interfaces that enable transparent interaction
- Entities, i.e., workers, automation platforms, agents, … ,  are fully decoupled and can be distributed to improve fault-tolerance and scalability.
- The deployment and use of STACKL works with popular DevOps technologies and platforms: docker, kubernetes, ansible, azure, AWS, and is oriented towards the future, for instance, for serverless computing (FaaS/SaaS).
- Autonomous operation is a key focus: as much as possible, after deployment of STACKL, the system and its entities will self-manage and self-discover
- To allow rapid use of STACKL, it provides a minimal and fast setup on a regular computer for a normal user. Button-press fire-and-forget deployment of STACKL enables users to take it for a quick spin.
## Even more information
- See [stackl.io](https://www.stackl.io) to get started with documentation and tutorials.
- See [STACKL slides](https://drive.google.com/open?id=10ZmqGU3pOc6EJyZpED4fMgav5pD01RztLkfSn3Jl9EA) for a short presentation about STACKL.
# :handshake:Contributing
Contributions, issues, and feature requests are always more than welcome! Feel free to check [issues page](https://github.com/kefranabg/readme-md-generator/issues) if you want to contribute.
See [CONTRIBUTING](CONTRIBUTING.md) to get started.
Please also read the [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md).
# :memo:License
The code in this project is licensed under the [GLPv3](LICENSE) license.
# Acknowledgments
STACKL was initially created for in-house use by a DevOps company, [Nubera](https://www.nubera.eu/), who saw the need for platform to better provide  services to clients. After some time, it became clear that STACKL could be useful to the general DevOps community as well so the decision was made to spin it off as an open source project.
Hence, thanks to Nubera  and @Yannick Struyf who put in much of the hard initial work.