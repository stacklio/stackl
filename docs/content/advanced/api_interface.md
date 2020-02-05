---
title: API Interface
kind: advanced
weight: 2
---

STACKL offers a REST API for interactions.
The API is implemented using Flask as a WSGI server, thus offering a regular REST API that supports the basic HTTP methods (GET, POST, PUT, DELETE).
STACKL exposes its listening server on 8080, the IP of the hosting docker container and a web interface. 
For a local deployment, this is <http://localhost:8080/>.
Interactions happen through API calls with associated parameters, either through curl commands in the command line interface or using the web interface (implemented through Swagger), using any browser.

STACKL exposes five types of operations:

* Document operations
* Item operations
* Stack operations
* User operations
* About operations

## Document operations

All operations related to documents.
This interface serves two purposes: (1) to retrieve one or more documents as-is and (2) to submit a document of a valid type for storing, modifying, or deleting.
These operations are expressly used to get, add, and delete documents and do nothing beyond that.
For instance, these can be used to add or change config data or items (such as SITs, SATs or services).

## Item operations

All operations related to items and their K/Vs.
This interface serves to correctly retrieve and process item-type documents.
As items are actionable elements that can be the result of a hierarchical K/V lookup of its constituent documents, the item or its subparts (such as a K/V pair) might not be directly stored and need to be resolved from its constituent sub-documents.
The difference with document operations is that these operations require processing beyond datastore manipulations.

## Stack operations

All operations related to stacks.
This interface serves to retrieve and act on stack_template and stack_instance-type documents.
As these documents are items that represent possible and running applications, operations made through this interface enable to instantiate, modify, or delete them.
The difference with document operations is that these operations have results beyond changes in the datastore.

## User operations

All operations related to users.
To get, add or delete users.

## About operations

All operations related to information about STACKL.
