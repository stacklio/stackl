"""
Entrypoint for Stackl Agent
"""

import asyncio
from dataclasses import dataclass
from typing import List

from arq.connections import RedisSettings

from agent import config
from agent.kubernetes.kubernetes_tool_factory import KubernetesToolFactory
from agent.mock.mock_tool_factory import MockToolFactory

if config.settings.agent_type == "kubernetes":
    tool_factory = KubernetesToolFactory()
elif config.settings.agent_type == "mock":
    tool_factory = MockToolFactory()


@dataclass(frozen=True)
class Invocation:
    # pylint: disable=too-many-instance-attributes
    # Normal to have more because all the data is needed
    """
    Invocation class with all fields needed for deploying a stack instance
    """
    action: str
    functional_requirement: str
    service: str
    stack_instance: str
    infrastructure_target: str
    before_command: str
    image: str
    tool: str
    hosts: List
    playbook_path: str = None
    serial: int = 10


async def run_in_executor(func, *args):
    """
    Helper function for async automations
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


async def invoke_automation(ctx, invoc):
    # pylint: disable=unused-argument
    """
    Method that will handle invocations from Stackl Core
    """
    print(invoc)
    invocation = Invocation(**invoc)
    handler = tool_factory.get_handler(invocation)
    try:
        result, error_message = await run_in_executor(handler.handle)
    except asyncio.TimeoutError:
        result = 1
        error_message = "timeout in invoked job"
    print(result)
    print(error_message)
    automation_result = invoc
    if result == 0:
        automation_result['status'] = "READY"
    else:
        automation_result['status'] = "FAILED"
        automation_result['error_message'] = error_message

    print("Handle done")
    return automation_result


class AgentSettings:
    """
    Settings used by arq, for more info see: https://arq-docs.helpmanual.io/
    """
    functions = [invoke_automation]
    queue_name = config.settings.agent_name
    job_timeout = config.settings.job_timeout
    max_jobs = config.settings.max_jobs
    redis_settings = RedisSettings(host=config.settings.redis_host,
                                   port=config.settings.redis_port,
                                   password=config.settings.redis_password)
