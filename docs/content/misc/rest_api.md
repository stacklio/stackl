---
title: REST API
navtitle: REST API
kind: misc
weight: 1
---

This document is the authoritative specification of the STACKL REST API.

<https://restfulapi.net/idempotent-rest-apis/> and <https://tools.ietf.org/html/rfc7231#section-4.3.3>
Consistent use of put/post
PUT: Create or Update (Overwrite) the document. Is idempotent.
POST: Create the document. Not idempotent
Enforce this consistently, in contrast to now
