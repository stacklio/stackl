# Copyright 2020 The STACKL Authors.  All rights reserved.
# Use of this source code is governed by an GPLv3
# license that can be found in the LICENSE file.


######################################################
#
# Documentation targets
#
######################################################

# The docs-% pattern target will shim to the
# makefile in ./docs
.PHONY: docs-%
docs-%:
	$(MAKE) -C docs $*

.PHONY: build_core
build_core:
	@echo "Building stackl core"
	cd stackl/application; docker build -t stackl_app -f Dockerfile_app .
	@echo "stackl_app ready"

.PHONY: build_worker
build_worker:
	@echo "Building stackl worker"
	cd stackl/application; docker build -t stackl_worker -f Dockerfile_worker .
	@echo "stackl_worker ready"

.PHONY: build_agent
build_agent:
	@echo "Building stackl agent"
	cd stackl/agent/websocket_agent; docker build -t stackl_agent .
	@echo "stackl_agent ready"

.PHONY: build_grpc_agent
build_grpc_agent:
	@echo "Building stackl grpc agent"
	cd stackl/agent/grpc_agent; docker build -t grpc_agent .
	@echo "grpc_agent ready"

.PHONY: build_local_agent
build_local_agent:
	@echo "Building stackl local agent"
	cd stackl/agent/local_agent; docker build -t local_agent .
	@echo "local_agent ready"

.PHONY: push_core
push_core:
	@echo "Pushing core"
	cd stackl/application; docker build -t nexus-dockerint.dome.dev/stackl/stackl-rest -f Dockerfile_app .
	docker push nexus-dockerint.dome.dev/stackl/stackl-rest

.PHONY: push_worker
push_worker:
	@echo "Pushing worker"
	cd stackl/application; docker build -t nexus-dockerint.dome.dev/stackl/stackl-worker -f Dockerfile_worker .
	docker push nexus-dockerint.dome.dev/stackl/stackl-worker

.PHONY: push_grpc_agent
push_grpc_agent:
	@echo "Pushing grpc agent"
	cd stackl/agent/grpc_agent; docker build -t nexus-dockerint.dome.dev/stackl/stackl-agent .
	docker push nexus-dockerint.dome.dev/stackl/stackl-agent

.PHONY: prepare
prepare:
	@echo "Creating docker-compose"
	docker run -v `pwd`/build/make/prepare/templates:/templates -v `pwd`/build/make/dev:/output -v `pwd`/build/make:/input  stackl/prepare:dev --conf /input/stackl.yml
	@echo "Created docker-compose file in build/make/dev"

.PHONY: start
start:
	@echo "Starting stackl"
	docker-compose -f build/make/dev/docker-compose.yml up -d
	@echo "Started stackl"

create_test_database:
	cd make/prepare/ ; cp -a ../example_database /home/sven/lfs_test_store/
#	cp lfs_test_store/ /Users/frederic/stackl/lfsdb/LFS_DB/

push: push_core push_worker push_grpc_agent

install: build_core build_worker build_agent build_grpc_agent build_local_agent prepare start
