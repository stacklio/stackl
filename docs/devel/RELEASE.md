# Release Process

## Overview

Every release consists of three phases: (1) versioning, (2) building, and (3) publishing.
We use semantic versioning, see also [semver](https://semver.org/).

Versioning involves maintaining the following files:

- **CHANGELOG.md** - a list of all the important changes in each release.
- **Makefile** - contains the VERSION number for the latest version of the project.
- **docs/website/RELEASES*** - gives the versions of documentation that are public [documentation](https://www.stackl.io/docs). 
__The first entry on the list is the latest version.__

The steps below explain how to update these files.
In addition, the repository should be tagged with the semantic version identifying the release.

Building involves obtaining a copy of the repository and checking out the release tag.

Publishing involves creating a new *Release* on GitHub with the relevant CHANGELOG.md snippet.

## Versioning

1. Clone the repository.

	```
	git clone git@github.com:stacklio/stackl.git
	```

2. Execute the release-patch target to generate boilerplate patch. Give the semantic version of the release:

	```
	make release-patch VERSION=0.1.1 > ~/release.patch
	```

3. Apply the release patch to the working copy and preview the changes:

	```
	patch -p1 < ~/release.patch
	git diff
	```

	> Amend the changes as necessary, e.g., many of the Fixes and Miscellaneous
	> changes may not be user facing (so remove them). Also, if there have been
	> any significant API changes, call them out in their own sections.

4. Commit the changes and push to remote repository.

	```
	git commit -a -s -m "Prepare v<version> release"
	git push origin master
	```

5. Tag repository with release version and push tags to remote repository.

	```
	git tag v<semver>
	git push origin --tags
	```

6. Execute the dev-patch target to generate boilerplate patch. Give the semantic version of the next release:

	```
	make dev-patch VERSION=0.1.2 > ~/dev.patch
	```

	> The semantic version of the next release typically increments the point version by one.

7. Apply the patch to the working copy and preview the changes:

	```
	patch -p1 < ~/dev.patch
	git diff
	```

8. Commit the changes and push to remote repository.

	```
	git commit -a -s -m "Prepare v<next_semvar> development"
	git push origin master
	```
