# Copyright 2020 The STACKL Authors.  All rights reserved.
# Use of this source code is governed by an GPLv3
# license that can be found in the LICENSE file.

CONTAINER_ENGINE = $(shell command -v podman 2> /dev/null || command -v docker 2> /dev/null)
DOCKER_IMAGE_PREPARE=stacklio/stackl-prepare
DOCKER_IMAGE_CORE=stacklio/stackl-core
DOCKER_IMAGE_AGENT=stacklio/stackl-agent
DOCKER_IMAGE_CLI=stacklio/stackl-cli
DOCKER_IMAGE_OPA=stacklio/opa
DOCKER_IMAGE_REDIS=stacklio/redis

OPA_VERSION=v0.21.1
REDIS_VERSION=5.0.3
VERSIONTAG=0.2.2dev


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
	cd build/make/prepare; ${CONTAINER_ENGINE} build -t $(DOCKER_IMAGE_PREPARE):v$(VERSIONTAG) .

.PHONY: build_core
build_core:
	@echo "Building stackl core"
	${CONTAINER_ENGINE} build -f stackl/core/Dockerfile -t $(DOCKER_IMAGE_CORE):v$(VERSIONTAG) .

.PHONY: build_agent
build_agent:
	@echo "Building agent "
	${CONTAINER_ENGINE} build -f stackl/agent/Dockerfile -t $(DOCKER_IMAGE_AGENT):v$(VERSIONTAG) .

.PHONY: build_stackl_cli
build_stackl_cli:
	@echo "Building stackl-cli"
	${CONTAINER_ENGINE} build -f stackl/cli/Dockerfile -t $(DOCKER_IMAGE_CLI):v$(VERSIONTAG) stackl/cli

.PHONY: build_opa
build_opa:
	@echo "Building opa"
	${CONTAINER_ENGINE} build -f stackl/opa/Dockerfile --build-arg "OPA_VERSION=${OPA_VERSION}" -t $(DOCKER_IMAGE_OPA):$(OPA_VERSION) stackl/opa

.PHONY: build_redis
build_redis:
	@echo "Building redis"
	${CONTAINER_ENGINE} build -f stackl/redis/Dockerfile -t $(DOCKER_IMAGE_REDIS):v$(REDIS_VERSION) stackl/redis

.PHONY: push_prepare
push_prepare:
	@echo "Pushing prepare"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_PREPARE):v$(VERSIONTAG)

.PHONY: push_core
push_core:
	@echo "Pushing core"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_CORE):v$(VERSIONTAG)

.PHONY: push_agent
push_agent:
	@echo "Pushing agent"
	${CONTAINER_ENGINE} push $(DOCKER_IMAGE_AGENT):v$(VERSIONTAG)

.PHONY: prepare
prepare:
	@echo "Creating docker-compose"
	${CONTAINER_ENGINE} run -v `pwd`/build/make/prepare/templates:/templates -v `pwd`/build/make/dev:/output -v `pwd`/build/make:/input $(DOCKER_IMAGE_PREPARE):v$(VERSIONTAG) --conf /input/stackl.yml
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
	  --image=registry.access.redhat.com/ubi8/ubi-minimal:8.2-345

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
	openapi-generator generate -i http://localhost:8000/openapi.json -g python -t build/openapi-generator --package-name stackl_client --additional-properties=packageVersion=${VERSIONTAG} -o /tmp/stackl-client
	pip3 install /tmp/stackl-client

.PHONY: stackl_cli
stackl_cli:
	pip3 install -e stackl/cli/

build: build_prepare build_core build_agent build_opa build_redis
push: push_prepare push_core push_agent
install: build prepare start
full_install: install openapi stackl_cli
dev: kaniko-warmer skaffold
kubernetes: build_kubernetes_agent push_kubernetes_agent
all: build push
