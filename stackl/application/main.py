#!/usr/local/bin/python
import logging
import os
import threading
from concurrent import futures

import grpc
from fastapi import FastAPI
from fastapi.routing import APIRoute

import protos
import stackl_globals
from agent_broker.automation_job_dispenser import AutomationJobDispenser
from manager.manager_factory import ManagerFactory
from message_channel.message_channel_factory import MessageChannelFactory
from opa_broker.opa_broker_factory import OPABrokerFactory
from routers import documents_router, stack_instances_router, functional_requirements_router, services_router, \
    stack_application_templates_router, \
    stack_infrastructure_templates_router, about_router, configurator_router, \
    policy_agent_router, policies_router
from task_broker.task_broker_factory import TaskBrokerFactory
from utils.general_utils import get_hostname

# Logger stuff
logger = logging.getLogger("STACKL_LOGGER")
level = os.environ.get("LOGLEVEL", "INFO").upper()
logger.setLevel(level)
ch = logging.StreamHandler()
ch.setLevel(level)
formatter = logging.Formatter('[[[%(asctime)s|%(message)s',
                              "%d.%m.%y|%H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Start initialisation of Application Logic
stackl_globals.initialize()

message_channel_factory = MessageChannelFactory()
message_channel = message_channel_factory.get_message_channel()

manager_factory = ManagerFactory()
task_broker_factory = TaskBrokerFactory()
opa_broker_factory = OPABrokerFactory()
document_manager = ManagerFactory().get_document_manager()

task_broker = task_broker_factory.get_task_broker()
opa_broker = opa_broker_factory.get_opa_broker()

task_broker_thread = threading.Thread(
    name="Task Broker Thread",
    target=task_broker.start_stackl,
    kwargs={"subscribe_channels": ['all', get_hostname(), 'rest']})
task_broker_thread.daemon = True
task_broker_thread.start()

opa_broker.start(manager_factory)

logger.info(
    "___________________ STARTING STACKL GRPC SERVER ____________________")
certificate_chain = """
-----BEGIN CERTIFICATE-----
MIIDyTCCArGgAwIBAgIUMmRxzKpI7bmP2n1/mZuTqM3qO2wwDQYJKoZIhvcNAQEL
BQAwdDELMAkGA1UEBhMCQkUxEDAOBgNVBAgMB0xpbWJ1cmcxFDASBgNVBAcMC1Rl
c3NlbmRlcmxvMQ8wDQYDVQQKDAZTVEFDS0wxDTALBgNVBAsMBERPTUUxHTAbBgNV
BAMMFHN0YWNrbC1ncnBjLmRvbWUuZGV2MB4XDTIwMDUyNTA4Mzg0MVoXDTIxMDUy
NTA4Mzg0MVowdDELMAkGA1UEBhMCQkUxEDAOBgNVBAgMB0xpbWJ1cmcxFDASBgNV
BAcMC1Rlc3NlbmRlcmxvMQ8wDQYDVQQKDAZTVEFDS0wxDTALBgNVBAsMBERPTUUx
HTAbBgNVBAMMFHN0YWNrbC1ncnBjLmRvbWUuZGV2MIIBIjANBgkqhkiG9w0BAQEF
AAOCAQ8AMIIBCgKCAQEApi0P4pWWP8UpIbUlTpCqyF/lLjBMAi0ksvb1VoOmoETQ
3fEYpjK6VWhIaR50fGuoklNnUW6uV0hLy+h1zpk4G/xy+kBjiuC7f9SCNuvCCJZE
qmS+bTcDAlrVROeIAxuJYFM5XiQYLMNUmnltTQVr6dlw7sVrrlqpuPr3aTbLnw8U
x8Q1cailAdX0DVvtRYTgSHaIP2BlLgNfEept4qAITpf2yhXwWdX93oEaTNwUpyOy
G2e20a8vAdHh3OroYvlACwpWDZu6ylPUp0UBjkxBa18rVFdhbeA2SWDt4+Nr8oZ3
wSlkXA/cHMD1XugMJATh06LJOkDIeVRynz4Wop/8uwIDAQABo1MwUTAdBgNVHQ4E
FgQUhx8a2iDHi6GBdhi5C0yXHkw8XH8wHwYDVR0jBBgwFoAUhx8a2iDHi6GBdhi5
C0yXHkw8XH8wDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAf4dk
02yk/PxSlolV61WdrCEMamLBYHK7uymQbZZnE1omYPH0lBK22wxJaTr2WllBjKiU
CGHOjeYBBvwUkxOg3NA/YoD99k756jIleRr6xiGjuzRk3ayH1xla+Iy2nviURlru
fuDycVz9+f9qlbhfjwaBQ2NT/Gvo8XashjLaVX6lXa6RB03/7CBHvbpL8lzfmAF3
cCk2DTYAsUvIBkU1KURKCfZBW+QbXAK6sU9XbV9FWOJtraYCfSjpP6zeHq0S/LhH
Rk7WgwzLQOvSRzzne7iSVVXnH2QExIebgdgRExe4Z6iWONlCsGlvQDqahTIGnI8u
8kjPCms2CX4/QCgbng==
-----END CERTIFICATE-----
"""

private_key = """
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCmLQ/ilZY/xSkh
tSVOkKrIX+UuMEwCLSSy9vVWg6agRNDd8RimMrpVaEhpHnR8a6iSU2dRbq5XSEvL
6HXOmTgb/HL6QGOK4Lt/1II268IIlkSqZL5tNwMCWtVE54gDG4lgUzleJBgsw1Sa
eW1NBWvp2XDuxWuuWqm4+vdpNsufDxTHxDVxqKUB1fQNW+1FhOBIdog/YGUuA18R
6m3ioAhOl/bKFfBZ1f3egRpM3BSnI7IbZ7bRry8B0eHc6uhi+UALClYNm7rKU9Sn
RQGOTEFrXytUV2Ft4DZJYO3j42vyhnfBKWRcD9wcwPVe6AwkBOHTosk6QMh5VHKf
Phain/y7AgMBAAECggEAFqNM5rE6JrXVRKJI0ssieOmXbxNlR2ae+UJrab3FlU/K
pHGTyhBfEgOC2c8sT0bbUBPMn2tUlM9khALHCb4Vxro9b5oV9XVoFaH9mz3C0Sin
cg8HYhl8b3WwWBKylLnLnTO5PPnt0StK+0BPg46ZhOH6YIzEfpwbQvftfIfadXCA
SReUt1lHKLc+al+i3x9D23pf9hod2R+fSdCuSdQZkxEn+UO64KUlCKTUGT8GVkFk
PnwE+YCMiJfg4fU76lReP2AfjDmpu/RxjkC8CHwBCFI0jDr4ySbSVxVR6i7muthD
KFQ7lQKx1qk9J93xKZ+zTCyGLKq2wMt3WzCqJd1RAQKBgQDVnZSUdooV24H5HqYq
ZM82OWsh78esCNRn3ByX3SXsgqplOB/D8VJF0qqMAozKSlQWbPjtIL0Ob6B0vKx3
ac5EMqC9aZ01K4UEU/f2FmPwXxI2A7g/ocQ8fA4imQSo+1qnH13VjWOwq/s6XCpO
ZNqDN85h5FbZSmv2wGkAakm85QKBgQDHJdTaW/rRKDV/A96r+WwsgN98xwyugBg+
gmviG24VKwv9izP9fLNE9J3CpYSFZNjxBK0VO1bi1QxzucKhndy+uFgxhP3kbU/N
ftHL5GiAoyWXxLUCe2ABM97sVsZrhIE0oR/ciPy4BKQhSYi48SXeuh1IVW33HH5F
ixqrIwTZHwKBgQDRbwQDYw0TTPlrQ69qlRfLdBQjW7GKa8XEZjvqcLoD3kAtqQ8L
zwf4yQjI6J8cni8/JWwRIS36f1rz2R/GnAfNOU37Jxco0BhEHAdaUK1/N9bk+lSk
nneFTaOWLCwzeOxyOgCHpW3+Az/3AfHAloTebdJ8i6DSvXKIpDDOZWcSOQKBgF3t
8xI29fs26tyIt7sHfsUS19ZjkBCyLD03iKjx5R8o2ZPx10jFS0zHz60iInpEUaqE
WRq9jUKZ2DCxOiK+cYKnMjnRD2txP4WePlfb2Ipr6OxHhFSyWlrW21s/poDJ06M+
J+f92Kz2y29D3q/UVddSk0MtwBsgnlIwxRhZAQ1jAoGBAKoNcGCiN6+M7SKs0w6l
n8tsBtkWRV4FMCz4TeJxHaPhezeEHno4/3xk/5R339Nw7x1EWm/L4K87Nx7Y6Lkd
lMP4XmBHHfAQvK/TmwuDyOgm2xjqQI0fVlQ4aNmyc+NSasb2oiRYWQJ8NR3yulff
JyOK4/nEdp6LhhAvXYcpuoZr
-----END PRIVATE KEY-----
"""

# server_credentials = grpc.ssl_server_credentials(
#   ((bytes(private_key, 'utf-8'), bytes(certificate_chain, 'utf-8')),))
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
protos.agent_pb2_grpc.add_StacklAgentServicer_to_server(
    AutomationJobDispenser(stackl_globals.redis_cache, document_manager),
    server)
server.add_insecure_port('[::]:50051')
# server.add_secure_port('[::]:50051', server_credentials)
server.start()

logger.info(
    "___________________ STARTING STACKL API SERVER ____________________")

# Add routes
app = FastAPI(
    title="STACKL",
    description="stackl",
)

app.include_router(documents_router.router,
                   prefix="/documents",
                   tags=["documents"])
app.include_router(policies_router.router,
                   prefix="/policies",
                   tags=["policies"])
app.include_router(policy_agent_router.router,
                   prefix="/policy_agent",
                   tags=["policy_agent"])
app.include_router(stack_instances_router.router,
                   prefix="/stack_instances",
                   tags=["stack_instances"])
app.include_router(functional_requirements_router.router,
                   prefix="/functional_requirements",
                   tags=["functional_requirements"])
app.include_router(services_router.router,
                   prefix="/services",
                   tags=["services"])
app.include_router(stack_application_templates_router.router,
                   prefix="/stack_application_templates",
                   tags=["stack_application_templates"])
app.include_router(stack_infrastructure_templates_router.router,
                   prefix="/stack_infrastructure_templates",
                   tags=["stack_infrastructure_templates"])
app.include_router(configurator_router.router,
                   prefix="/configurator",
                   tags=["configurator"])
app.include_router(configurator_router.router,
                   prefix="/agents",
                   tags=["agents"])
app.include_router(about_router.router, prefix="/about", tags=["about"])


def use_route_names_as_operation_ids(application: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in application.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(app)
