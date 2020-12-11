"""
Main entrypoint for stackl core
"""
try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata

import logging
import sys

import uvicorn
from elasticapm.contrib.starlette import ElasticAPM, make_apm_client
from fastapi import FastAPI
from fastapi.routing import APIRoute
# Logger stuff
from loguru import logger

from core import config
from core.migrations.upgrade2to3 import upgrade

from .routers import (about_router, functional_requirements_router,
                      infrastructure_base_router, outputs_router,
                      policy_templates_router, services_router,
                      snapshots_router, stack_application_templates_router,
                      stack_infrastructure_templates_router,
                      stack_instances_router)

logging.getLogger().handlers = [config.InterceptHandler()]
logging.getLogger("uvicorn.access").handlers = [config.InterceptHandler()]

logger.configure(handlers=[{"sink": sys.stderr, "level": config.settings.log_level}])

logger.info(
    "___________________ STARTING STACKL API SERVER ____________________")

# Add routes
app = FastAPI(title="STACKL",
              description="stackl",
              version=metadata.version('core'))

# Migrations
upgrade()

if config.settings.elastic_apm_enabled:
    logger.debug("Elastic APM Enabled")
    apm = make_apm_client(config={})
    app.add_middleware(ElasticAPM, client=apm)

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
app.include_router(outputs_router.router, prefix="/outputs", tags=["outputs"])
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
