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

1. Execute the release-patch target to generate boilerplate patch. Give the semantic version of the release:

	```
	make release-patch VERSION=0.12.8 > ~/release.patch
	```

1. Apply the release patch to the working copy and preview the changes:

	```
	patch -p1 < ~/release.patch
	git diff
	```

	> Amend the changes as necessary, e.g., many of the Fixes and Miscellaneous
	> changes may not be user facing (so remove them). Also, if there have been
	> any significant API changes, call them out in their own sections.

1. Commit the changes and push to remote repository.

	```
	git commit -a -s -m "Prepare v<version> release"
	git push origin master
	```

1. Tag repository with release version and push tags to remote repository.

	```
	git tag v<semver>
	git push origin --tags
	```

1. Execute the dev-patch target to generate boilerplate patch. Give the semantic version of the next release:

	```
	make dev-patch VERSION=0.12.9 > ~/dev.patch
	```

	> The semantic version of the next release typically increments the point version by one.

1. Apply the patch to the working copy and preview the changes:

	```
	patch -p1 < ~/dev.patch
	git diff
	```

1. Commit the changes and push to remote repository.

	```
	git commit -a -s -m "Prepare v<next_semvar> development"
	git push origin master
	```

## Building

1. Obtain copy of remote repository.

	```
	git clone git@github.com:stacklio/stackl.git
	```

1. Execute the release target. The results can be found under _release/VERSION:

	```
	make release VERSION=0.12.8
	```

## Publishing

1. Open browser and go to https://github.com/stacklio/stackl/releases

1. Create a new release for the version.
	- Copy the changelog content into the message.

## Notes

- The docs and website should update and be published automatically. 
  If they are not you can trigger one by a couple of methods:
	- Login to Netlify (requires permission for the project) and manually trigger a build.
	- Post to the build webhook via:
		```bash
		curl -X POST -d {} https://api.netlify.com/build_hooks/5cc3aa86495f22c7a368f1d2
		```

# Bugfix Release Process

If this is the first bugfix for the release, create the release branch from the
release tag:

```bash
git checkout -b release-0.14 v0.14.0
```

Otherwise, checkout the release branch and rebase on upstream:

```bash
git fetch upstream
git checkout release-0.14
git rebase upstream/release-0.14
```

Cherry pick the changes from master or other branches onto the bugfix branch:

```bash
git cherry-pick -x <commit-id>
```

Update the `VERSION` variable in the Makefile (e.g., edit and set to `0.14.1`).
Commit this change:

```bash
git commit -s -a -m 'Prepare v0.14.1 release'
```

Push the release branch to your fork and open a Pull Request against the
upstream release branch. Be careful to open the Pull Request against the correct
upstream release branch. **DO NOT** open/merge the Pull Request into master or
other release branches:

```bash
git push origin release-0.14
```

Once the Pull Request has been merged you can tag the release at the commit created above. 
<!-- Once the tag is pushed to `open-policy-agent/opa`, CI jobs will automatically build and publish the Docker images and website updates. -->

The last step is to try a build.

```
make release VERSION=0.14.1
```

> The release binaries are located under `_release/<version>` in your working
> copy.
