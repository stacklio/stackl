---
title: Stack Templates
kind: advanced
weight: 3
---

A Stack is declarative description of an application and the IT infrastructure it may run on.
Stacks consist out of two concerns which are separated into a **Stack Application Template (SAT)** and a **Stack Infrastructure Template (SIT)**.
STACKL creates a Stack Template (ST) by constraint solving the SAT and SIT of the Stack, thus creating a valid mapping of an application to the IT infrastructure at that point in time.
An instantiation of this ST on the infrastructure is called a Stack Instance (SI).
Stacks are a concept.
SATs, SITs, STs and SIs are stored documents which are given, processed, tracked, and maintained in the datastore.

Users separately specify their application as a set of modular microservices in SATs and the available infrastructure in SITs.
Separate specification decouples applications from the infrastructure, allowing different SATs to be matched to different SITs, promoting flexibility, adaptability, and re-use.
Producers can submit a Stack to STACKL as a combination of a SAT and SIT.
If the stack is instantiable, STACKLs returns the set of possible instantiations in a ST which can become a SI, or running application.

## Stack Application Template

A SAT describes the application as a set of constituent services (actual software entities) that have functional and resource requirements (FR and RR) and additional service policies (POL) which describes extra-functional requirements or properties such as count.
The SAT aggregates the FRs, RRs, and POLs and can specify application-level RRs and POLs as well.
The resulting set of these requirements and policies are the constraints of the application to be able to run as desired on given infrastructure.

Services are either stored in separate documents or specified in the SAT itself.
FRs are what the service is supposed to do.
These map to configuration packets for the software host so that it can perform certain functions.
FRs can inherit from other FRs.
K/V pairs of an FR override those of the preceding FR.
FRs are stored in separate documents.
FRs have RRs that, in turn, determine the minimum RRs of the service and the service can specify additional RRs.
FRs also specify the invocation process that is needed to instantiate the FR.

RRs are what resources the service needs to functions
These map the resource requirements of the hosting infrastructure.
These are the minimum set of the requirements of the FRs, if specified, and the specified ones by the service.

Policies are additional specifications for how the service or applications functions.
These map to behavioural constraints on and across services, such as high availability of a service through redundancy or a low latency requirement between two services.
They can be both derived from the set of FRs or explicitly specified for the application. 

### Example: Simple SAT

```json
 #sat_simple.json
{
   "name": "sat_simple",
   "type": "stack_application_template",
   "services": {
        "single_calculator": "Single Calculator"
   },
   "extra_functional_requirements": {}
}
```

```json
#service_single_calculator.json
{
   "name": "single_calculator",
   "type": "processing server",
   "functional_requirements": ["linux"],
   "non_functional_requirements": {
           "CPU": "2Ghz",
           "memory": "4GB RAM"
   },
}
```

```json
#fr_linux.json
{
   "name" : "linux",
   "type" : "operating system",
   "disk_config": [
       {
         "size_gb": "16",
         "name": "disk1",
         "thin_provisioned": "false",
         "drive_letter": "c",
         "datastore": "vsanDatastore",
         "unit_number": "0"
       }
   ],
   "invocation": {
         "handler":"terraform",
         "version":"0.12",
         "target":"centos",
         "Description":"installs centos"
   }
}
```

### Example: Complex SAT

```json
#sat_complex.json
{
   "name": "sat_complex",
   "type": "stack_application_template",
   "services": {
        "web_app": "Web App",
        "database": "Database"
   },
   "extra_functional_requirements": {
        "redundancy" : [ { "database" : 2 } ]
        "same_zone" : [ [ "web_app", "database" ] ]
   }
}
```

```json
#service_web_app.json
{
   "name" : "web_app",
   "type" : "Web application",
   "functional_requirements": ["WebConfig", "DNSConfig"],
   "non_functional_requirements": {
           "CPU": "3Ghz",
           "memory": "6GB RAM"
   }
}
```

```json
#service_database.json
{
   "name" : "database",
   "type" : "database",
   "functional_requirements": ["DatabaseConfig"],
   "non_functional_requirements": {
           "hard_disk": "100GB"
   },
  "description": ""
}
```

```json
#fr_webconfig.json
{
   "name" : "WebConfig",
   "inherits": "ubuntu",
   "git_token": "random_token",
   "git_user": "web_user",
   "description": "",
   "invocation": {
         "handler":"terraform",
         "version":"0.12",
         "target":"centos.yml",
         "Description":"installs centos"
   }
}
```

```json
#fr_dnsconfig.json
{
   "name" : "DNSConfig",
   "inherits": "ubuntu",
   "git_token": "random_token",
   "git_user": "dns_user",
   "description": "",
   "invocation": {
         "handler":"terraform",
         "version":"0.12",
         "target":"centos.yml",
         "description":"installs centos"
   }
}
```

## Stack Infrastructure Template

A SIT models the available infrastructure.
It describes the infrastructure in terms of the environment, location, and zones and explicitly specifies their relationship in a set of infrastructure targets.
Environment, location and zones are separate documents.
An infrastructure target is the result of merging these documents where the K/V pairs of the zone override the location which override the environment.
Each infrastructure target has capabilities.
These can vary over time due to dynamic factors (e.g., load on a server, power outages, ...).
As such, each SIT has an update policy which specifies when the capabilities of the infrastructure targets should be determined.

### Example: Stack Infrastructure Template

```json
# stack_infrastructure_template.json
{
   "name": "Example IT Infrastructure",
   "type": "sit_example",
   "environment": ["Production", "Development"],
   "location": ["VMW", "AWS"],
   "zone": ["V1", "V2", "S1", "S2"],
   "infrastructure_targets": ["P.VMW.V1", "P.VMW.V2", "D.AWS.S1", "D.AWS.S2"],
   "infrastructure_capabilities": {
       "P.VMW.V1": {
           "type": "",
           "properties": {
               "CPU": <<CPU>>,
               "memory": <<memory>>
           },
       "P.VMW.V2": {
           "type": "",
           "properties": {
               "CPU": <<CPU>>,
               "memory": <<memory>>
           },
       "D.AWS.S1": {
           "type": "",
           "properties": {
               "CPU": <<CPU>>,
               "memory": <<memory>>
           },
       "D.AWS.S2": {
           "type": "",
           "properties": {
               "CPU": <<CPU>>,
               "memory": <<memory>>
           }
     },
    "update_policy" : "always",
    "timestamp_last_update" : "None"
}
```

## Stack Template and Instance

A ST is the result of processing a submitted Stack, as a SAT and SIT, into a set of viable solutions where services are mapped to the infrastructure that is capable of running it.
Each solution can be instantiated as an SI.
The processing consists of a policy-based SIT update, a two part constraint solver and an actionable result.
The SIT is updated, if needed, by retrieving the current capabilities of each infrastructure target.
After, the SIT is written back as an updated document with the up-to-date capabilities included.
The first part of constraint solving considers each service in turn.
The FRs and RRs of each service are contrasted to the capabilities of each infrastructure targets.
The result is a set of targets the service can run on.
The second part of constraint solving considers the policies of the SAT and further filters suitable targets for services.
For instance, if a same-zone requirement for service_a and service_b cannot be satisfied if service_a is deployed on a target in a zone where service_b cannot be deployed, this target is deleted from the list of suitable targets of service_a.
The end result is a document that contains the mapping of services to infrastructure and which can be stored and acted upon.
If any service has no suitable targets, no ST is made since the application is uninstantiable.
If all services have suitable targets, an ST is made that drops the requirements of the services and capabilities of the targets, since it has been determined that these are satisfied, and keeps the RRs since these may provide necessary information during stack instantiation, for instance,  picking targets in the same zone

For instantiation, the targets need to be chosen.
This first needs to take into account the RRs so that only viable combinations of targets are selected.
If multiple solutions remain, one is chosen according to a policy, e.g., cheapest target first

### Example: Stack Template Simple

```json
#supposing that all infrastructure targets support Linux and the hardware requirements
#st_simple.json
{
   "name": "st_simple",
   "type": "stack_template",
   "services": {
      "single_vm": {
         "type" : "processing_server",
         "infrastructure_targets" : ["P.VMW.V1", "P.VMW.V2", "D.AWS.S1", "D.AWS.S2"]
   },
   "extra_functional_requirements": {}
}
```

There are 4 possible SI, one for each target.

```json
#si_simple1.json
{
   "name": "si_simple1",
   "type": "stack_instance",
   "services": {
      "single_vm": {
         "type" : "processing_server",
         "infrastructure_target" : "P.VMW.V1"
   }
}
```

### Example: Stack Template Complex

```json
#supposing that only VMW supports the DNSConfig and the hardware requirements
 #st_complex.json
{
   "name": "st_complex",
   "type": "stack_template",
   "services": {
      "web_app": {
         "type" : "Web Application",
         "infrastructure_targets" : ["P.VMW.V1", "P.VMW.V2"]

      },
      "database": {
         "type" : "Database",
         "infrastructure_targets" : ["P.VMW.V1", "P.VMW.V2",  "D.AWS.S1", "D.AWS.S2"]
      },
   },
   "extra_functional_requirements": {
        "redundancy" : [ { "database" : 2 } ]
        "same_zone" : [ [ "web_app", "database" ] ]
   }
}
```

There are two possible SI taking into account the same_zone policy.

```json
#si_complex1.json
{
   "name": "si_complex1"
   "type": "stack_template",
   "services": {
      "web_app": {
         "type" : "Web Application",
         "infrastructure_target" : "P.VMW.V1"
      },
      "database1": {
         "type" : "Database",
         "infrastructure_target" : "P.VMW.V1"
      },
      "database2": {
         "type" : "Database",
         "infrastructure_target" : "P.VMW.V1"
      }
   }
}
```
