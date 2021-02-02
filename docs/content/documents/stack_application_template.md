---
title: Stack Application Template
kind: documents
weight: 6
date: 2020-02-17 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
models the application as a set of services with their requirements and policies

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  |
**description** | **str** |  | [optional] [default to '']
**services** | **list[str]** |  |
**policies** | **dict(str, list[object])** |  | [optional] 
**category** | **str** |  | [optional] [default to 'configs']
**type** | **str** |  | [optional] [default to 'stack_application_template']