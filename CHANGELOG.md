# Changelog

All notable changes to STACKL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2021-06-11

### Added

- Now possible to execute services in stages (#227)
- Service policies (#236)
- Supply private key to ansible using `stackl_private_key` (#248)

### Changed

- Ansible outputs now make use of callback plugin (#242)
- New way of supplying command args for all the handlers
- Terraform backend can now be a jinja template (#265)
- Vault secrets also can be used as env variables with envconsul 

### Fixed

- Generic invocation now gets chosen by default

## [0.3.3] - 2021-02-18

### Fixed

- Wait for all containers in a Stackl job pod to be ready (#198)
- Check if stack instance exists before deleting it (#199)

### Added

- Configurable Vault image for Vault secret handler (#200)
- Secrets can now be supplied for each service (#201)
- Terraform backend can now be set with params

### Changed

- Force delete now tries to delete every functional requirement (#213)
- Error message now also gets logged in agent

## [0.3.2] - 2021-01-28

### Fixed

- Host templating
- Ansible inventory script

## [0.3.1] - 2021-01-21

### Fixed

- Fixed Stackl hosts
- Fixed Stackl outputs

## [0.3.0] - 2021-01-07

### Fixed

- Fixed timeout issues for asyncio jobs

### Added

- Ability to add a multitude of the same services to a single stack instance
- Added an active deadline for Stackl jobs
- Vault init container will fail when a secret does not exist
- Counter for hostname feature

### Changed

- Documentation Layout changed
- Moved `ansible_playbook_path` to the invocation instead of the provisioning parameters
- Stackl agent code refactored

## [0.2.6] - 2020-11-12

### Fixed

- Fix update infra capabilities, so updates won't fail because policies did not have all the data (#176)
- Use loguru for uvicorn logs (#173)

## [0.2.5] - 2020-10-29

### Added
- Option for force deleting a stack instance
- Option added for configuring max_jobs for stackl agent
- Update deployment and configuration docs
- Added progressbar option when creating/updating stack instance
- Add Ansible-playbook docs
- Add docs on how to debug OPA
- Option to disable automatic rollback
- Option to supply Redis password for agent and core
- (EXPERIMENTAL) Elastic APM can be enabled for stackl core 

### Changed
- Using as_group on a functional-requirement will now group infrastructure targets in the stack instance status

### Fixed
- `stackl apply` for documents now fails when a document is not valid
- stackl core now passes pylint test
- stack instance creation will not fail when policies are not defined in SAT
- `python3-devel` package changed to `python38-devel` in Dockerfile core
- Fix inventory when running Ansible role with local connection

### Security
- Bumped UBI versions for images to 8.2-349 to fix issue with librepo package
- Add reporting policies
- Add codeql-analysis

[unreleased]: https://github.com/stacklio/stackl/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/stacklio/stackl/compare/v0.3.3...v0.4.0
[0.3.3]: https://github.com/stacklio/stackl/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/stacklio/stackl/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/stacklio/stackl/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/stacklio/stackl/compare/v0.2.6...v0.3.0
[0.2.6]: https://github.com/stacklio/stackl/compare/v0.2.5...v0.2.6
[0.2.5]: https://github.com/stacklio/stackl/compare/v0.2.4...v0.2.5
