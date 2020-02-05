# Copyright 2020 The STACKL Authors.  All rights reserved.
# Use of this source code is governed by an GPLv3
# license that can be found in the LICENSE file.

# Comments from tom
# ** I modified this file and based on the OPA makefile !
# - Repository must be a variable
# - When building and publishing, we need VERSIONS ?
# - Test database ... we need variables
# - I have not tested it
# - We need automated tests ?
# - We need to check before building ? (check OPA makefile)


DOCKER_INSTALLED := $(shell hash docker 2>/dev/null && echo 1 || echo 0)
DOCKER := docker
DOCKER_COMPOSE_INSTALLED := $(shell hash docker-compose 2>/dev/null && echo 1 || echo 0)
DOCKER-COMPOSE := docker-compose

STACKL_APP_DIR := stackl/application
STACKL_AGENT_DIR := stackl/agent
STACKL_MAKE_DIR := make

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

######################################################
#
# Build STACKL containers
#
######################################################

.PHONY: build_all
build_all: build_core build_worker build_agent build_grpc_agent build_local_agent

.PHONY: build_core
build_core:
ifeq ($(DOCKER_INSTALLED), 1)
	@echo "Building STACKL Core"
	cd $(STACKL_APP_DIR); $(DOCKER) build -t stackl_app -f Dockerfile_app .
	@echo "  stackl_app ready"
else
	@echo "Docker not installed. Skipping STACKL build."
endif

.PHONY: build_worker
build_worker:
ifeq ($(DOCKER_INSTALLED), 1)
	@echo "Building STACKL Worker"
	cd $(STACKL_APP_DIR); $(DOCKER) build -t stackl_worker -f Dockerfile_worker .
	@echo "  stackl_worker ready"
else
	@echo "Docker not installed. Skipping STACKL build."
endif

.PHONY: build_agent
build_agent:
ifeq ($(DOCKER_INSTALLED), 1)
	@echo "Building STACKL Agent"
	cd $(STACKL_AGENT_DIR)/websocket_agent; $(DOCKER) build -t stackl_agent .
	@echo "  stackl_agent ready"
else
	@echo "Docker not installed. Skipping STACKL build."
endif

.PHONY: build_grpc_agent
build_grpc_agent:
ifeq ($(DOCKER_INSTALLED), 1)
	@echo "Building STACKL GRPC Agent"
	cd $(STACKL_AGENT_DIR)/grpc_agent; $(DOCKER) build -t grpc_agent .
	@echo "  grpc_agent ready"
else
	@echo "Docker not installed. Skipping STACKL GPRC Agent build."
endif

.PHONY: build_local_agent
build_local_agent:
ifeq ($(DOCKER_INSTALLED), 1)
	@echo "Building STACKL Local Agent"
	cd $(STACKL_AGENT_DIR)/local_agent; $(DOCKER) build -t local_agent .
	@echo "  local_agent ready"
else
	@echo "Docker not installed. Skipping STACKL Local Agent build."
endif

######################################################
#
# Publish STACKL containers
#
######################################################

.PHONY:push_all
push_all: push_core push_worker push_grpc_agent

.PHONY: push_core
push_core: docker-login
ifeq ($(DOCKER_INSTALLED), 1)
	@echo "Publishing STACKL Core"
	cd $(STACKL_APP_DIR); $(DOCKER) build -t nexus-dockerint.dome.dev/stackl/stackl-rest -f Dockerfile_app .
	$(DOCKER) push nexus-dockerint.dome.dev/stackl/stackl-rest
else
	@echo "Docker not installed. Skipping publishing STACKL Core."
endif

.PHONY: push_worker
push_worker: docker-login
ifeq ($(DOCKER_INSTALLED), 1)
	@echo "Publishing STACKL Worker"
	cd $(STACKL_APP_DIR); $(DOCKER) build -t nexus-dockerint.dome.dev/stackl/stackl-worker -f Dockerfile_worker .
	$(DOCKER) push nexus-dockerint.dome.dev/stackl/stackl-worker
else
	@echo "Docker not installed. Skipping publishing STACKL Worker."
endif

.PHONY: push_grpc_agent
push_grpc_agent: docker-login
ifeq ($(DOCKER_INSTALLED), 1)
	@echo "Publishing STACKL GRPC Agent"
	cd $(STACKL_AGENT_DIR)/grpc_agent; $(DOCKER) build -t nexus-dockerint.dome.dev/stackl/stackl-agent .
	$(DOCKER) push nexus-dockerint.dome.dev/stackl/stackl-agent
else
	@echo "Docker not installed. Skipping publishing STACKL GRPC Agent."
endif

.PHONY: docker-login
docker-login:
	@$(DOCKER) login -u ${DOCKER_USER} -p ${DOCKER_PASSWORD}

######################################################
#
# Install STACKL containers
#
######################################################

.PHONY: install
install: build_all prepare start

.PHONY: prepare
prepare:
ifeq ($(DOCKER_INSTALLED), 1)
	@echo "Creating docker-compose"
	$(DOCKER) run -v `pwd`$(STACKL_MAKE_DIR)/prepare/templates:/templates -v `pwd`$(STACKL_MAKE_DIR)/dev:/output -v `pwd`$(STACKL_MAKE_DIR):/input  stackl/prepare:dev --conf /input/stackl.yml
	@echo "  Created docker-compose file in $(STACKL_MAKE_DIR)/dev"
else
	@echo "Docker not installed. Skipping STACKL preparation."
endif

.PHONY: start
prepare:
ifeq ($(DOCKER_COMPOSE_INSTALLED), 1)
	@echo "Creating docker-compose"
	$(DOCKER-COMPOSE) -f $(STACKL_MAKE_DIR)/dev/docker-compose.yml up -d
	@echo "  STACKL is started"
else
	@echo "Docker not installed. Skipping STACKL start."
endif


.PHONY: test_database
test_database:
 cd $(STACKL_MAKE_DIR)/prepare/ ; cp -a ../example_database /home/sven/lfs_test_store/
