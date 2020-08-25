#!/usr/local/bin/python

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
# Logger stuff
from loguru import logger

from .routers import functional_requirements_router, infrastructure_base_router, policy_templates_router, \
    snapshots_router, stack_instances_router, services_router, stack_application_templates_router, \
    stack_infrastructure_templates_router, about_router

logger.info(
    "___________________ STARTING STACKL API SERVER ____________________")

# Add routes
app = FastAPI(
    title="STACKL",
    description="stackl",
    version="0.2.2dev"
)

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
    uvicorn.run(app, host="0.0.0.0", port=8080)
