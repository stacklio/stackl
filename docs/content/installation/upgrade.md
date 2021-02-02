---
title: Upgrade
kind: installation
weight: 5
date: 2020-02-17 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

Following section describes how to upgrade Stackl. To avoid any conflict, make sure Stackl and its agents are always running on the same version.

## Helm

Using Helm, clone the [Stackl Helm git repository](https://github.com/stacklio/stackl-helm).

```bash
git clone https://github.com/stacklio/stackl-helm.git
```

Configure Stackl using the variables in the [configuration table](../configuration).

Make sure to edit the `stacklAgent.image` and `stackl.image` to the desired values. Perform a Helm upgrade

```bash
helm install stackl-helm/stackl -n stackl stackl-name -f path/to/values.yml
```

```bash
helm install stackl-helm/stackl-agent -n stackl stackl-agent-name -f path/to/values.yml
```

## Upgrade from Stackl 0.2.x to 0.3.x

Upgrading from Stackl 0.2.x to 0.3.x involves a change in existing Stackl documents and existing Stack Instances. Following guide will describe the steps needed to upgrade Stackl.

- Upgrade Stackl-core and Stackl-agent
- Upgrade Stackl-client and Stackl-cli
- Update SAT documents

### Upgrade Stackl-core and Stackl-agent

Upgrading Stackl-core and Stackl-agent is as easy as described above. Simply change the image version to the desired 0.3.x versions. Once deployed, Stackl-core will attempt to make a change to existing Stackl Instances to accomodate the changes in 0.3.x and to make sure existing Stack Instances still work in the newer version. For this to work, Stackl needs to be able to connect to the datastore. If the datastore is not running at the time of Stackl-core's start, it will throw an error.

### Upgrade Stackl-client and Stackl-cli

As described at the beginning of this section, make sure all Stackl-components are running on the same version. After upgrading, make sure that any tool using Stackl (automation images, pipelines, ...) is upgraded to the correct version to ensure everything keeps working.

### Update SAT documents

Next, be sure to update the SAT documents. In Stackl 0.3.x a new feature is introduced to allow for multiple of the same services to be used in a Stack Instance and in a SAT. The `services` field in SAT documents changed from a list of string to a list of dicts. For example:

```yaml
category: configs
name: example_sat
services:
  - example_service
type: stack_application_template
```

Should become:

```yaml
category: configs
name: example_sat
services:
  - name: example_service
    service: example_service
type: stack_application_template
```
