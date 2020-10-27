---
title: Policy Template
kind: documents
weight: 7
date: 2020-02-17 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
service- and application-level requirements that specify additional requirements on the service or applications, such as replicas, service latency links, availability conditions, ...

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**description** | **str** |  | [optional] 
**category** | **str** |  | [optional] [default to 'configs']
**type** | **str** |  | [optional] [default to 'policy_template']
**policy** | **str** |  | 
**inputs** | **list[str]** |  | 
**outputs** | **list[str]** |  | [optional]