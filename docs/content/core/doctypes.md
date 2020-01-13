---
title: Document Types
kind: documentation
weight: 3
---
A Document is a text-file in the JSON or YAML format that models IT infrastructure building blocks, application service definitions, and their configuration data.

There are two categories of documents: items and configurations. Configs represent specified or given documents that model elements or concepts of  the client’s IT domain and are ‘things’ that by themselves are not actionable but serve as configuration. Items represent resulting documents that are tangible elements of a client’s IT domain, data that is actionable or an interactable entity.  Items can be the result of the aggregation or merging of several non-items. For instance, a deployable piece of hardware (infrastructure target) described by a document is an item and can be the result of a client’s environment, zone and location documents which together uniquely represent that hardware.
