# Release Process

## Overview

Every release of STACKL consists of three phases: (1) versioning, (2) building, and (3) publishing.
We use semantic versioning, see also [semver](https://semver.org/).

Versioning involves maintaining the following files:

- **CHANGELOG.md** - a list of all the important changes in each release.
- **Makefile** - contains the VERSION number for the latest version of the project.
- **docs/website/RELEASES*** - gives the versions of documentation that are public [documentation](https://www.stackl.io/docs). 
__The first entry on the list is the latest version.__

Releases are done through specifying the release tag, making the new release through the makefile, and providing an overview of changes in the changelog linked to that tag.
In addition, the repository should be tagged with the semantic version identifying the release.

## Versioning

1. Clone the repository.

	```
	git clone git@github.com:stacklio/stackl.git
	```

