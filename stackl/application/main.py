#!/usr/local/bin/python

import logging
import os
import threading

from fastapi import FastAPI

import globals
from agent_broker.agent_broker_factory import AgentBrokerFactory
from manager.manager_factory import ManagerFactory
from task_broker.task_broker_factory import TaskBrokerFactory
from utils.general_utils import get_hostname

from routers import documents, stacks, functional_requirements, services, stack_application_templates, \
    stack_infrastructure_templates

# Logger stuff
logger = logging.getLogger(__name__)
level = os.environ.get("LOGLEVEL", "INFO").upper()
logger.setLevel(level)
ch = logging.StreamHandler()
ch.setLevel(level)
formatter = logging.Formatter(
    "{'time':'%(asctime)s', 'level': '%(levelname)s', 'message': '%(message)s'}")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Start initialisation of Application Logic
globals.initialize()

manager_factory = ManagerFactory()
task_broker_factory = TaskBrokerFactory()

agent_broker_factory = AgentBrokerFactory()
agent_broker = agent_broker_factory.agent_broker
task_broker = task_broker_factory.get_task_broker()

agent_broker_thread = threading.Thread(name="Agent Broker Thread", target=agent_broker.start, args=[])
agent_broker_thread.daemon = True
agent_broker_thread.start()

task_broker_thread = threading.Thread(name="Task Broker Thread", target=task_broker.start_stackl,
                                      kwargs={"subscribe_channels": ['all', get_hostname(), 'rest'],
                                              "agent_broker": agent_broker})
task_broker_thread.daemon = True
task_broker_thread.start()

logger.info("___________________ STARTING STACKL_API ____________________")

# Add routes
app = FastAPI()

app.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)
app.include_router(
    stacks.router,
    prefix="/stacks",
    tags=["stacks"]
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

