---
title: Service
kind: documents
weight: 5
date: 2020-02-17 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
Software entity that performs a small piece of functionality and has a clear set of service requirements

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**category** | **str** |  | [optional] [default to 'items']
**type** | **str** |  | [optional] [default to 'service']
**params** | [**object**](.md) |  | [optional] 
**secrets** | [**object**](.md) |  | [optional] 
**description** | **str** |  | [optional] [default to 'Base Document']
**functional_requirements** | **list[str]** |  | 
**resource_requirements** | [**object**](.md) |  | [optional] 