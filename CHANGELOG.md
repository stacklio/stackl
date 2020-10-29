# Changelog

All notable changes to STACKL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[unreleased]: https://github.com/stacklio/stackl/compare/v0.2.5...HEAD
[0.2.5]: https://github.com/stacklio/stackl/compare/v0.2.4...v0.2.5
