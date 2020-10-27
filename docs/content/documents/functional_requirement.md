---
title: Functional Requirement
kind: documents
weight: 4
date: 2020-02-17 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
configuration packages required of the operating environment for the service to perform its functions

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**category** | **str** |  | 
**type** | **str** |  | [optional] [default to 'functional_requirement']
**params** | [**object**](.md) |  | [optional] 
**secrets** | [**object**](.md) |  | [optional] 
**description** | **str** |  | [optional] [default to 'Base Document']
**invocation** | [**dict(str, Invocation)**](Invocation.md) |  | 
**outputs** | [**object**](.md) |  | [optional] 
**outputs_format** | **str** |  | [optional] [default to 'json']