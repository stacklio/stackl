---
title: Environment, Location and Zone
kind: documents
weight: 2
date: 2020-02-17 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
**Environment**
: represents an environment used within your IT infrastructure; production, testing,

**Location**
: represents a logical (or physical) location used where the IT infrastructure is present; a description of the geographical location such as a city, a region, ...

**Zone**
: represents a logical network, security zone, or direct IT environment used within the location IT infrastructure; subnets, clusters, security groups, actual devices, etc

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**category** | **str** |  | 
**type** | **str** |  | 
**cloud_provider** | **str** |  | [optional] [default to '']
**params** | [**object**](.md) |  | [optional] 
**secrets** | [**object**](.md) |  | [optional] 
**outputs** | [**object**](.md) |  | [optional] 
**resources** | [**object**](.md) |  | [optional] 
**policies** | [**object**](.md) |  | [optional] 
**packages** | **list[str]** |  | [optional] [default to []]
**tags** | [**object**](.md) |  | [optional] 
**agent** | **str** |  | [optional] [default to '']
**description** | **str** |  | [optional] [default to 'Base Document']