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
    stack_application_templates_router, infrastructure_base_router, \
    stack_infrastructure_templates_router, about_router, configurator_router, \
    policy_agent_router, policy_templates_router, snapshots_router
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

task_broker_thread = threading.Thread(name="Task Broker Thread",
                                      target=task_broker.start_stackl,
                                      kwargs={
                                          "manager_factory":
                                          manager_factory,
                                          "subscribe_channels":
                                          ['all',
                                           get_hostname(), 'rest']
                                      })
task_broker_thread.daemon = True
task_broker_thread.start()

opa_broker.start(manager_factory)

logger.info(
    "___________________ STARTING STACKL GRPC SERVER ____________________")
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    options=[
        ('grpc.keepalive_time_ms', 10000),
        # send keepalive ping every 10 second, default is 2 hours
        ('grpc.keepalive_timeout_ms', 5000),
        # keepalive ping time out after 5 seconds, default is 20 seoncds
        ('grpc.keepalive_permit_without_calls', True),
        # allow keepalive pings when there's no gRPC calls
        ('grpc.http2.max_pings_without_data', 0),
        # allow unlimited amount of keepalive pings without data
        ('grpc.http2.min_time_between_pings_ms', 10000),
        # allow grpc pings from client every 10 seconds
        ('grpc.http2.min_ping_interval_without_data_ms', 5000),
        # allow grpc pings from client without data every 5 seconds
    ])
protos.agent_pb2_grpc.add_StacklAgentServicer_to_server(
    AutomationJobDispenser(stackl_globals.redis_cache, document_manager),
    server)
server.add_insecure_port('[::]:50051')
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
app.include_router(infrastructure_base_router.router,
                   prefix="/infrastructure_base",
                   tags=["infrastructure_base"])
app.include_router(policy_templates_router.router,
                   prefix="/policy_templates",
                   tags=["policy_templates"])
app.include_router(snapshots_router.router,
                   prefix="/snapshots",
                   tags=["snapshots"])
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
