---
title: REST API
navtitle: REST API
kind: misc
weight: 1
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

This document is the authoritative specification of the STACKL REST API.

<https://restfulapi.net/idempotent-rest-apis/> and <https://tools.ietf.org/html/rfc7231#section-4.3.3>
Consistent use of put/post
PUT: Create or Update (Overwrite) the document. Is idempotent.
POST: Create the document. Not idempotent
Enforce this consistently, in contrast to now
