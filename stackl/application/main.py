#!/usr/local/bin/python

import logging
import os
import threading

from fastapi import FastAPI
from fastapi.routing import APIRoute

import globals
from agent_broker.agent_broker_factory import AgentBrokerFactory
from manager.manager_factory import ManagerFactory
from routers import documents, stack_instances, functional_requirements, services, stack_application_templates, \
    stack_infrastructure_templates, about, terraform, policies
from task_broker.task_broker_factory import TaskBrokerFactory
from opa_broker.opa_broker_factory import OPABrokerFactory
from utils.general_utils import get_hostname

# Logger stuff
logger = logging.getLogger("STACKL_LOGGER")
level = os.environ.get("LOGLEVEL", "INFO").upper()
logger.setLevel(level)
ch = logging.StreamHandler()
ch.setLevel(level)
formatter = logging.Formatter('[[[%(asctime)s|%(message)s', "%d.%m.%y|%H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Start initialisation of Application Logic
globals.initialize()

manager_factory = ManagerFactory()
task_broker_factory = TaskBrokerFactory()
agent_broker_factory = AgentBrokerFactory()
opa_broker_factory = OPABrokerFactory()

agent_broker = agent_broker_factory.agent_broker
task_broker = task_broker_factory.get_task_broker()
opa_broker = opa_broker_factory.get_opa_broker()

agent_broker_thread = threading.Thread(name="Agent Broker Thread", target=agent_broker.start, args=[])
agent_broker_thread.daemon = True
agent_broker_thread.start()

task_broker_thread = threading.Thread(name="Task Broker Thread", target=task_broker.start_stackl,
                                      kwargs={"subscribe_channels": ['all', get_hostname(), 'rest'],
                                              "agent_broker": agent_broker})
task_broker_thread.daemon = True
task_broker_thread.start()

opa_broker.start()

logger.info("___________________ STARTING STACKL_API ____________________")

# Add routes
app = FastAPI(
    title="STACKL",
    description="stackl",)

app.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)
app.include_router(
    policies.router,
    prefix="/policies",
    tags=["policies"]
)
app.include_router(
    stack_instances.router,
    prefix="/stack_instances",
    tags=["stack_instances"]
)
app.include_router(
    functional_requirements.router,
    prefix="/functional_requirements",
    tags=["functional_requirements"]
)
app.include_router(
    services.router,
    prefix="/services",
    tags=["services"]
)
app.include_router(
    stack_application_templates.router,
    prefix="/stack_application_templates",
    tags=["stack_application_templates"]
)
app.include_router(
    stack_infrastructure_templates.router,
    prefix="/stack_infrastructure_templates",
    tags=["stack_infrastructure_templates"]
)
#TODO Technological dependency
app.include_router(
    terraform.router,
    prefix="/terraform",
    tags=["terraform"]
)
app.include_router(
    about.router,
    prefix="/about",
    tags=["about"]
)

def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(app)
