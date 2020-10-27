---
title: Stack Infrastructure Template
kind: documents
weight: 3
date: 2020-02-17 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
Models IT infrastructure as infrastructure targets originating from the environment, location, and zone and possessing a set of infrastructure capabilities

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**description** | **str** |  | [optional] [default to '']
**infrastructure_targets** | [**list[InfrastructureTarget]**](InfrastructureTarget.md) |  | 
**infrastructure_capabilities** | [**dict(str, StackInfrastructureTarget)**](StackInfrastructureTarget.md) |  | [optional] 
**type** | **str** |  | [optional] [default to 'stack_infrastructure_template']
**category** | **str** |  | [optional] [default to 'configs']