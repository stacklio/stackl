# The STACKL Website and Documentation
The content and tooling is separated into a few places:

[devel/](./devel/) - Developer documentation for OPA (not part of the website)


[website/](./website/) - This directory contains all of the Markdown, HTML, Sass/CSS,
and other assets needed to build the [openpolicyagent.org](https://openpolicyagent.org)
website. See the section below for steps to build the site and test documentation changes
locally. This content is not versioned for each release, it is common scaffolding for
the website.

[content/](./content/) - The raw OPA documentation can be found under the
directory. This content is versioned for each release and should have all images
and code snippets alongside the markdown content files.

[website/data/integrations.yaml](./website/data/integrations.yaml) - Source for the
integrations index. See [Integration Index](#integration-index) below for more details.

## Website Components

The website ([openpolicyagent.org](https://openpolicyagent.org)) and doc's hosted there
([openpolicyagent.org/docs](https://openpolicyagent.org/docs)) have a few components
involved with the buildings and hosting.

The static site is generated with [Hugo](https://gohugo.io/) which uses the markdown
in [content/](./content) as its content for pages under `/docs/*`. There is a script
to generate the previous supported versions, automated via `make generate`, and the
latest (current working tree) documentations is under `/docs/edge/*`.

The static site content is then hosted by [Netlify](https://www.netlify.com/). To
support backwards compatible URLs (from pre-netlify days) and to have the `latest`
version of the docs URLs work
[openpolicyagent.org/docs/latest](https://openpolicyagent.org/docs/latest) the site
relies on Netlify URL [redirects and rewrites](https://www.netlify.com/docs/redirects/)
which are defined in [website/layouts/index.redirects](./webiste/layouts/index.redirects)
and are build into a `_redirects` file when the Hugo build happens via
`make production-build` or `make preview-build`.

### How to Edit and Test

Because of the different components at play there are a few different ways to
test/view the website. The choice depends largely on what is being modified:

#### Full Site Preview

Go to [Netlify](https://www.netlify.com/) and log-in. Link to your public fork of
OPA on github and have it deploy a site. As long as it is public this is free
and can be configured to deploy test branches before opening PR's on the official
OPA github repo.

This approach gives the best simulation for what the website will behave like once
code has merged.


#### Modifying `content` (*.md)

The majorify of this can be done with any markdown renderer (typically built-in or
a plug-in for IDE's). The rendered output will be very similar to what Hugo will
generate.

> This excludes the Hugo shortcodes (places with `{{< SHORT_CODE >}}` in the markdown.
  To see the output of these you'll need to involve Hugo. Additionally, to validate
  and view live code blocks, a full site build is required (e.g. `make serve`,
  details below). See the "Live Code Blocks" section for more information on
  how to write them.

#### Modifying the Hugo templates and/or website (HTML/CSS/JS)

The easiest way is to run Hugo locally in dev mode. Changes made will be reflected
immediately be the Hugo dev server. See
[Run the site locally using Docker](#run-the-site-locally-using-docker)

> This approach will *not* include the Netlify redirects so urls like
  `http://localhost:1313/docs/latest/` will not work. You must navigate directly to
  the version of docs you want to test. Typically this will be
  [http://localhost:1313/docs/edge/](http://localhost:1313/docs/edge/).
  It will also not include the processing required for live code blocks
  to show up correctly.


#### Modifying the netlify config/redirects

This requires either using the [Full Site Preview](#full-site-preview) or using
the local dev tools as described below in:
[Run the site locally without Docker](#run-the-site-locally-without-docker)

The local dev tools will *not* give live updates as the content changes, but
will give the most accurate production simulation.

## Run the site locally

You can run the site locally [with Docker](#run-the-site-locally-using-docker) or
[without Docker](#run-the-site-locally-without-docker).

### Generating Versioned Content ###

> This *MUST* be done before you can serve the site locally!

The site will show all versions of doc content from the tagged versions listed
in [RELEASES](./RELEASES).

To generate them run:
```shell
make generate
```
The content then will be placed into `docs/website/generated/docs/$VERSION/`.

This will attempt to fetch the latest tags from git. The fetch will be skipped
if the `OFFLINE` environment variable is defined. For example:

```shell
OFFLINE=1 make generate
```

### Run the site locally using Docker

> Note: running with docker only uses the Hugo server and not Netlify locally.
  This means that redirects and other Netlify features the site relies on will not work.
  It will also not include the processing required for live code blocks
  to show up correctly.

If [Docker is running](https://docs.docker.com/get-started/):

```bash
make docker-serve
```

Open your browser to http://localhost:1313 to see the site running locally. The docs
are available at http://localhost:1313/docs.

### Run the site locally without Docker

To build and serve the site locally without using Docker, install the following packages
on your system:

- The [Hugo](#installing-hugo) static site generator
- The [Netlify dev CLI](https://www.netlify.com/products/dev/)
- [NodeJS](https://nodejs.org) (and NPM)

The site will be running from the Hugo dev server and fronted through netlify running
as a local reverse proxy. This more closely simulates the production environment but
gives live updates as code changes.

#### Installing Hugo

Running the website locally requires installing the [Hugo](https://gohugo.io) static
site generator. The required version of Hugo is listed in the
[`netlify.toml`](./netlify.toml) configuration file (see the `HUGO_VERSION` variable).

Installation instructions for Hugo can be found in the [official
documentation](https://gohugo.io/getting-started/installing/).

Please note that you need to install the "extended" version of Hugo (with built-in
support) to run the site locally. If you get errors like this, it means that you're
using the non-extended version:

```
error: failed to transform resource: TOCSS: failed to transform "sass/style.sass" (text/x-sass): this feature is not available in your current Hugo version
```

#### Serving the full site

From this directory:

```shell
make serve
```

Watch the console output for a localhost URL (the port is randomized). The docs are
available at http://localhost:$PORT/docs.


## Site updates

The OPA site is automatically published using [Netlify](https://netlify.com). Whenever
changes in this directory are pushed to `master`, the site will be re-built and
re-deployed.

## Checking links

To check the site's links, first start the full site preview locally (see [Serving the full site](#serving-the-full-site) instructions))

Then run:

```bash
docker run --rm -it --net=host linkchecker/linkchecker $URL
```

Note: You may need to adjust the `URL` (host and/or port) depending on the environment. For OSX
and Windows the host might need to be `host.docker.internal` instead of `localhost`.

> This link checker will work on best with Netlify previews! Just point it at the preview URL instead of the local server.
  The "pretty url" feature seems to work best when deployed, running locally may result in erroneous links.


# Integration Index

The integration index makes it easy to find either a specific integration with OPA
or to browse the integrations with OPA within a particular category.  And it pulls
information about that integration (e.g. blogs, videos, tutorials, code) into a
single place while allowing integration authors to maintain the code wherever they like.

## Schema

The schema of integrations.yaml has the following highlevel entries, each of which is self-explanatory.
* integrations
* organizations
* software

Each entry is an object where keys are unique identifiers for each subentry.
Organizations and Software are self-explanatory by inspection.  The schema for integrations is as follows.

* title: string
* description: string
* software: array of strings
* labels: collection of key/value pairs.
* tutorials: array of links
* code: array of links
* inventors: array of either
  * string (organization name)
  * object with fields
    * name: string
    * organization: string
* videos: array of either
  * link
  * object with fields
    * title: string
    * speakers: array of name/organization objects
    * venue: string
    * link: string
* blogs: array of links

The UI for this is currently hosted at [https://openpolicyagent.org/docs/latest/ecosystem/](https://openpolicyagent.org/docs/latest/ecosystem/)

The future plan is to use the following labels to generate categories of integrations.

* layer: which layer of the stack does this belong to
* category: which kind of component within that layer is this
* type: what kind of integration this is.  Either `enforcement` or `poweredbyopa`.  `enforcement` is the default
  if `type` is missing.  `poweredbyopa` is intended to be integrations built using OPA that are not tied to a
  particular layer of the stack.  This distinction is the most ambiguous and may change.

As of now the labels are only displayed for each entry.

## Logos
For each entry in the [integrations.yaml](./website/data/integrations.yaml) integrations section the UI will use a
PNG logo with the same name as the key from [./website/static/img/logos/integrations](./website/static/img/logos/integrations)

For example:

```yaml
integrations:
  my-cool-integration:
    ...
```

Would need a file called `my-cool-integration.png` at `./website/static/img/logos/integrations/my-cool-integration.png`

If it doesn't exist the OPA logo will be shown by default.
