---
title: Add Extra Services
kind: advanced
weight: 9
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
Sometimes it can be useful to add an extra service to an already existing stack instance. This way applications can be extended with for example an extra database, message queue, etc.

Please note that this only works when using "Stackl Manifests" as it is not yet supported through CLI commands.

## Example

To make this functionality more clear take a look at the following Stack Application Template

```yaml
category: configs
description: ""
name: nginx
services:
  - name: example-webserver
    service: nginx
policies: {}
type: stack_application_template
```

From this SAT we can create a Stack Instance which will deploy an nginx webserver using the following manifest:

```yaml
stack_infrastructure_template: example
stack_application_template: nginx
params: {}
secrets: {}
```

We can now instantiate it using the stackl CLI:

`stackl apply -c <manifest> <stack_instance_name>`

Now imagine our webserver is running fine, but now we want an extra Postgres database in this instance, instead of adding it to the SAT and making a new instance we can just edit the manifest and update our existing instance:

```yaml
stack_infrastructure_template: example
stack_application_template: nginx
params: {}
secrets: {}
services:
  - name: example-database
    service: postgres
```

Now running the previous command again will add the Postgres service to the Stack Instance and will start the needed automation.

`stackl apply -c <manifest> <stack_instance_name>`

### Removing an extra service

Extra services can be easily removed again by removing them from the manifest. Apply the manifest again and a delete action will be invoked for the services that were removed.
