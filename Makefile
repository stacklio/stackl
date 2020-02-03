build_core: 
	@echo "Building stackl core"
	cd stackl/application; docker build -t stackl_app -f Dockerfile_app .
	@echo "stackl_app ready"

build_worker:
	@echo "Building stackl worker"
	cd stackl/application; docker build -t stackl_worker -f Dockerfile_worker .
	@echo "stackl_worker ready"

build_agent:
	@echo "Building stackl agent"
	cd stackl/agent/websocket_agent; docker build -t stackl_agent .
	@echo "stackl_agent ready"

build_grpc_agent:
	@echo "Building stackl grpc agent"
	cd stackl/agent/grpc_agent; docker build -t grpc_agent .
	@echo "grpc_agent ready"

build_local_agent:
	@echo "Building stackl local agent"
	cd stackl/agent/local_agent; docker build -t local_agent .
	@echo "local_agent ready"

push_core:
	@echo "Pushing core"
	cd stackl/application; docker build -t nexus-dockerint.dome.dev/stackl/stackl-rest -f Dockerfile_app .
	docker push nexus-dockerint.dome.dev/stackl/stackl-rest

push_worker:
	@echo "Pushing worker"
	cd stackl/application; docker build -t nexus-dockerint.dome.dev/stackl/stackl-worker -f Dockerfile_worker .
	docker push nexus-dockerint.dome.dev/stackl/stackl-worker

push_grpc_agent:
	@echo "Pushing grpc agent"
	cd stackl/agent/grpc_agent; docker build -t nexus-dockerint.dome.dev/stackl/stackl-agent .
	docker push nexus-dockerint.dome.dev/stackl/stackl-agent

prepare:
	@echo "Creating docker-compose"
	docker run -v `pwd`/make/prepare/templates:/templates -v `pwd`/make/dev:/output -v `pwd`/make:/input  stackl/prepare:dev --conf /input/stackl.yml
	@echo "Created docker-compose file in make/dev"

start:
	@echo "Starting stackl"
	docker-compose -f make/dev/docker-compose.yml up -d
	@echo "Started stackl"

create_test_database:
	cd make/prepare/ ; cp -a ../example_database /home/sven/lfs_test_store/
#	cp lfs_test_store/ /Users/frederic/stackl/lfsdb/LFS_DB/

push: push_core push_worker push_grpc_agent

install: build_core build_worker build_agent build_grpc_agent build_local_agent prepare start
