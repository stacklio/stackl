# Copyright 2020 The STACKL Authors.  All rights reserved.
# Use of this source code is governed by an GPLv3
# license that can be found in the LICENSE file.

CONTAINER_ENGINE=$(shell command -v podman 2> /dev/null || command -v docker 2> /dev/null)
DOCKER_IMAGE_PREPARE=stacklio/stackl-prepare
DOCKER_IMAGE_CORE=stacklio/stackl-core
DOCKER_IMAGE_AGENT=stacklio/stackl-agent
DOCKER_IMAGE_CLI=stacklio/stackl-cli
DOCKER_IMAGE_OPA=stacklio/opa
DOCKER_IMAGE_REDIS=quay.io/stackl/stackl-redis

CORE_VERSION=v$(shell sed -n 's/.*version = "\([^"]*\)".*/\1/p' stackl/core/pyproject.toml)
AGENT_VERSION=v$(shell sed -n 's/.*version = "\([^"]*\)".*/\1/p' stackl/agent/pyproject.toml)
CLI_VERSION=v$(shell sed -n 's/.*__version__ = "\([^"]*\)".*/\1/p' stackl/cli/setup.py)
OPA_VERSION=v0.31.0
REDIS_VERSION=v6.2.5
PREPARE_VERSION=latest

######################################################
#
# Documentation targets
#
######################################################
.DEFAULT_GOAL := all
# The docs-% pattern target will shim to the
# makefile in ./docs
.PHONY: docs-%
docs-%:
	$(MAKE) -C docs $*

.PHONY: build_prepare
build_prepare:
	@echo "Building prepare image"
	cd build/make/prepare; ${CONTAINER_ENGINE} build -t $(DOCKER_IMAGE_PREPARE):$(PREPARE_VERSION) --build-arg CORE_VERSION=$(CORE_VERSION) --build-arg AGENT_VERSION=$(AGENT_VERSION) .

.PHONY: build_core
build_core:
	@echo "Building stackl core"
	${CONTAINER_ENGINE} build -f stackl/core/Dockerfile -t $(DOCKER_IMAGE_CORE):$(CORE_VERSION) .

.PHONY: build_agent
build_agent:
	@echo "Building agent "
	${CONTAINER_ENGINE} build -f stackl/agent/Dockerfile -t $(DOCKER_IMAGE_AGENT):$(AGENT_VERSION) .

.PHONY: build_stackl_cli
build_stackl_cli:
	@echo "Building stackl-cli"
	${CONTAINER_ENGINE} build -f stackl/cli/Dockerfile -t $(DOCKER_IMAGE_CLI):$(CLI_VERSION) stackl/cli

.PHONY: build_opa
build_opa:
	@echo "Building opa"
	${CONTAINER_ENGINE} build -f stackl/opa/Dockerfile --build-arg "OPA_VERSION=${OPA_VERSION}" -t $(DOCKER_IMAGE_OPA):$(OPA_VERSION) stackl/opa

.PHONY: build_redis
build_redis:
	@echo "Building redis"
	${CONTAINER_ENGINE} build --no-cache -f stackl/redis/Dockerfile -t $(DOCKER_IMAGE_REDIS):$(REDIS_VERSION) stackl/redis

.PHONY: build_prepare_dev
build_prepare_dev:
	@echo "Building prepare image"
	cd build/make/prepare; ${CONTAINER_ENGINE} build -t ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_PREPARE):$(PREPARE_VERSION) --build-arg CORE_VERSION=$(CORE_VERSION) --build-arg AGENT_VERSION=$(AGENT_VERSION) .

.PHONY: build_core_dev
build_core_dev:
	@echo "Building stackl core"
	${CONTAINER_ENGINE} build -f stackl/core/Dockerfile -t ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_CORE):$(CORE_VERSION) .

.PHONY: build_agent_dev
build_agent_dev:
	@echo "Building agent "
	${CONTAINER_ENGINE} build -f stackl/agent/Dockerfile -t ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_AGENT):$(AGENT_VERSION) .

.PHONY: build_stackl_cli_dev
build_stackl_cli_dev:
	@echo "Building stackl-cli"
	${CONTAINER_ENGINE} build -f stackl/cli/Dockerfile -t ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_CLI):$(CLI_VERSION) stackl/cli

.PHONY: build_opa_dev
build_opa_dev:
	@echo "Building opa"
	${CONTAINER_ENGINE} build -f stackl/opa/Dockerfile --build-arg "OPA_VERSION=${OPA_VERSION}" -t ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_OPA):$(OPA_VERSION) stackl/opa

.PHONY: build_redis_dev
build_redis_dev:
	@echo "Building redis"
	${CONTAINER_ENGINE} build -f stackl/redis/Dockerfile -t ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_REDIS):$(REDIS_VERSION) stackl/redis


.PHONY: push_prepare
push_prepare:
	@echo "Pushing prepare"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_PREPARE):$(PREPARE_VERSION)

.PHONY: push_core
push_core:
	@echo "Pushing core"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_CORE):$(CORE_VERSION)

.PHONY: push_agent
push_agent:
	@echo "Pushing agent"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_AGENT):$(AGENT_VERSION)

.PHONY: push_prepare_dev
push_prepare_dev:
	@echo "Pushing prepare DEV"
	${CONTAINER_ENGINE} push ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_PREPARE):$(PREPARE_VERSION)

.PHONY: push_core_dev
push_core_dev:
	@echo "Pushing core DEV"
	${CONTAINER_ENGINE} push ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_CORE):$(CORE_VERSION)

.PHONY: push_agent_dev
push_agent_dev:
	@echo "Pushing agent DEV"
	${CONTAINER_ENGINE} push ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_AGENT):$(AGENT_VERSION)

.PHONY: push_cli_dev
push_cli_dev:
	@echo "Pushing agent DEV"
	${CONTAINER_ENGINE} push ${DOCKER_DEV_REPO}/$(DOCKER_IMAGE_CLI):$(CLI_VERSION)

.PHONY: prepare
prepare:
	@echo "Creating docker-compose"
	${CONTAINER_ENGINE} run -v `pwd`/build/make/prepare/templates:/templates -v `pwd`/build/make/dev:/output -v `pwd`/build/make:/input $(DOCKER_IMAGE_PREPARE):$(PREPARE_VERSION) --conf /input/stackl.yml
	@echo "Created docker-compose file in build/make/dev"

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
	skaffold version || (curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/v1.8.0/skaffold-linux-amd64 && chmod +x skaffold && sudo mv skaffold /usr/local/bin)
	sudo mkdir -p /var/snap/microk8s/common/kaniko/ && sudo chmod -R 766 /var/snap/microk8s/common/kaniko
	${CONTAINER_ENGINE} run -v /var/snap/microk8s/common/kaniko/:/workspace \
	  gcr.io/kaniko-project/warmer:latest\
	  --cache-dir=/workspace/cache \
	  --image=registry.access.redhat.com/ubi8/ubi-minimal:8.4-208

.PHONY: config-microk8s-registry
config-microk8s-registry:
	# microk8s.enable registry dns storage
	# echo '127.0.0.1 registry.container-registry.svc.cluster.local' | sudo tee --append /etc/hosts
	kubectl port-forward service/registry -n container-registry 5000:5000 &

.PHONY: skaffold
skaffold: config-microk8s-registry build_grpc_base_dev push_grpc_base_dev
	kubectl port-forward service/registry -n container-registry 5000:5000 &
	skaffold dev --force=false --port-forward --no-prune=true --no-prune-children=true

.PHONY: openapi
openapi:
	openapi-generator generate -i http://localhost:8000/openapi.json -g python -t build/openapi-generator --package-name stackl_client --additional-properties=packageVersion=${CORE_VERSION} -o /tmp/stackl-client
	pip3 install /tmp/stackl-client

.PHONY: stackl_cli
stackl_cli:
	pip3 install -e stackl/cli/

build: build_prepare build_core build_agent build_opa build_redis
push: push_prepare push_core push_agent
build_dev: build_prepare_dev build_core_dev build_agent_dev build_opa_dev build_redis_dev
push_dev: push_prepare_dev push_agent_dev push_core_dev
install: build prepare start
full_install: install openapi stackl_cli
dev: kaniko-warmer skaffold
kubernetes: build_kubernetes_agent push_kubernetes_agent
all: build push
