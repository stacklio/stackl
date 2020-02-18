# Developer guide

This guide provides instructions to run Stackl from source.

## Prerequisites

| Software       | Version  |
| :------------- | :------- |
| docker         | 18.09.0+ |
| docker-compose | 1.23.0+  |
| python         | 3.7.4+   |

## Clone the source code

```sh
git clone https://github.com/stacklio/stackl.git
```

## Configuration

Before running Stackl, go to build/make and copy the stackl.yml.tpl and name it stackl.yml, take a look at the file and make the necessary changes

```sh
cd build/make
cp stackl.yml.tpl stackl.yml
vim stackl.yml
```

Make a copy of the example_database in build/example database. Use the path of this copy in stackl.yml

## Build and run

The following command will build all the necessary images, template a docker-compose file and bring up Stackl. The templated docker-compose will be available in the make/dev directory.

```sh
make install
```

## Verify

If everything worked fine, you should be able to access the rest-api at

`localhost:<the_port_provided_in_config>/docs` (Default 8080)

# Makefile

## Target

| Target        | Description                                                       |
| :------------ | :---------------------------------------------------------------- |
| build_prepare    | Builds the Stackl prepare image                                |
| build_rest    | Builds the Stackl rest image                                      |
| build_worker | Builds the Stackl worker                                           |
| build_websocket_agent   | Builds the Stackl websocket agent image                 |
| build_kubernetes_agent   | Builds the Stackl kubernetes agent image               |
| build_docker_agent   | Builds the Stackl docker agent image                       |
| push_rest    | Push the Stackl rest image                                         |
| push_worker | Push the Stackl worker                                              |
| push_prepare   | Push the Stackl prepare image                                    |
| push_kubernetes_agent   | Push the Stackl kubernetes agent image                  |
| push_docker_agent   | Push the Stackl docker agent image                          |
| prepare       | Create the docker-compose file                                    |
| start         | Start Stackl with the docker-compose file in make/dev             |
| build         | Build all images                                                  |
| push          | Push all images to repository                                     |
| install       | Build all images, template the docker compose file and run Stackl |
