# Copyright 2020 The STACKL Authors.  All rights reserved.
# Use of this source code is governed by an GPLv3
# license that can be found in the LICENSE file.

CONTAINER_ENGINE = $(shell command -v podman 2> /dev/null || command -v docker 2> /dev/null)
DOCKER_IMAGE_PREPARE=stacklio/stackl-prepare
DOCKER_IMAGE_REST=stacklio/stackl-rest
DOCKER_IMAGE_WORKER=stacklio/stackl-worker
DOCKER_IMAGE_WEBSOCKET_AGENT=stacklio/stackl-websocket-agent
DOCKER_IMAGE_KUBERNETES_AGENT=stacklio/stackl-kubernetes-agent
DOCKER_IMAGE_DOCKER_AGENT=stacklio/stackl-docker-agent

VERSIONTAG=dev

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

.PHONY: build_prepare
build_prepare:
	@echo "Building prepare image"
	cd build/make/prepare; ${CONTAINER_ENGINE} build -t $(DOCKER_IMAGE_PREPARE):$(VERSIONTAG) .

.PHONY: build_rest
build_rest:
	@echo "Building stackl rest"
	cd stackl/application; ${CONTAINER_ENGINE} build -t $(DOCKER_IMAGE_REST):$(VERSIONTAG) -f Dockerfile_rest .

.PHONY: build_worker
build_worker:
	@echo "Building stackl worker"
	cd stackl/application; ${CONTAINER_ENGINE} build -t $(DOCKER_IMAGE_WORKER):$(VERSIONTAG) -f Dockerfile_worker .

.PHONY: build_websocket_agent
build_websocket_agent:
	@echo "Building stackl websocket agent"
	cd stackl/agents/websocket_agent; ${CONTAINER_ENGINE} build -t $(DOCKER_IMAGE_WEBSOCKET_AGENT):$(VERSIONTAG) .

.PHONY: build_kubernetes_agent
build_kubernetes_agent:
	@echo "Building stackl kubernetes agent"
	cd stackl/agents/kubernetes_agent; ${CONTAINER_ENGINE} build -t $(DOCKER_IMAGE_KUBERNETES_AGENT):$(VERSIONTAG) .

build_grpc_base:
	@echo "Building grpc base"
	cd stackl/agents/grpc_base; ${CONTAINER_ENGINE} build -t stacklio/grpc-base:latest .

.PHONY: build_docker_agent
build_docker_agent:
	@echo "Building stackl docker agent"
	cd stackl/agents/docker_agent; ${CONTAINER_ENGINE} build -t $(DOCKER_IMAGE_DOCKER_AGENT):$(VERSIONTAG) .

.PHONY: push_prepare
push_prepare:
	@echo "Pushing prepare"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_PREPARE):$(VERSIONTAG)

.PHONY: push_rest
push_rest:
	@echo "Pushing rest"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_REST):$(VERSIONTAG)

.PHONY: push_worker
push_worker:
	@echo "Pushing worker"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_WORKER):$(VERSIONTAG)

.PHONY: push_docker_agent
push_docker_agent:
	@echo "Pushing docker agent"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_DOCKER_AGENT):$(VERSIONTAG)

.PHONY: push_kubernetes_agent
push_kubernetes_agent:
	@echo "Pushing kubernetes agent"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_KUBERNETES_AGENT):$(VERSIONTAG)

.PHONY: prepare
prepare:
	@echo "Creating docker-compose"
	${CONTAINER_ENGINE} run -v `pwd`/build/make/prepare/templates:/templates -v `pwd`/build/make/dev:/output -v `pwd`/build/make:/input $(DOCKER_IMAGE_PREPARE):$(VERSIONTAG) --conf /input/stackl.yml
	@echo "Created docker-compose file in build/make/dev"

.PHONY: proto
proto:
	python3 -m grpc_tools.protoc -Istackl/protos --python_out=stackl/agents/grpc_base/protos/. --grpc_python_out=stackl/agents/grpc_base/protos/. stackl/protos/agent.proto
	python3 -m grpc_tools.protoc -Istackl/protos --python_out=stackl/application/protos/. --grpc_python_out=stackl/application/protos/. stackl/protos/agent.proto

.PHONY: start
start:
	@echo "Starting stackl"
	docker-compose -f build/make/dev/docker-compose.yml up -d
	@echo "Started stackl"

.PHONY: restart
restart:
	@echo "Restarting stackl"
	docker-compose -f build/make/dev/docker-compose.yml down
	@echo "Starting stackl"
	docker-compose -f build/make/dev/docker-compose.yml up -d
	@echo "Started stackl"

.PHONY: kaniko-warmer
kaniko-warmer:
	@echo "Pulling images for caching"
	mkdir -p /var/snap/microk8s/common/kaniko/
	${CONTAINER_ENGINE} run -v /var/snap/microk8s/common/kaniko/:/workspace gcr.io/kaniko-project/warmer:latest --cache-dir=/workspace/cache --image=stacklio/grpc-base:latest --image=python:3.8.1-slim-buster --image=tiangolo/uvicorn-gunicorn-fastapi:python3.7-2020-04-06

.PHONY: skaffold
skaffold:
	skaffold dev --force=false --port-forward

build: build_prepare build_rest build_worker build_websocket_agent build_grpc_base build_kubernetes_agent build_docker_agent
push: push_prepare push_rest push_worker push_kubernetes_agent push_docker_agent
install: build prepare start
dev: kaniko-warmer skaffold