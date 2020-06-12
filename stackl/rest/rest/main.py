#!/usr/local/bin/python
import logging
import os

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute

import stackl.stackl_globals as stackl_globals
from .routers import documents_router, infrastructure_base_router, policy_templates_router, snapshots_router, \
    stack_instances_router, functional_requirements_router, services_router, stack_application_templates_router, \
    stack_infrastructure_templates_router, about_router

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

logger.info(
    "___________________ STARTING STACKL API SERVER ____________________")

# initialize stackl globals
stackl_globals.initialize()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
