import asyncio
from dataclasses import dataclass

from arq.connections import RedisSettings

from agent import config
from agent.docker.docker_tool_factory import DockerToolFactory
from agent.kubernetes.kubernetes_tool_factory import KubernetesToolFactory
from agent.mock.mock_tool_factory import MockToolFactory

if config.settings.agent_type == "kubernetes":
    tool_factory = KubernetesToolFactory()
elif config.settings.agent_type == "docker":
    tool_factory = DockerToolFactory()
elif config.settings.agent_type == "mock":
    tool_factory = MockToolFactory()


@dataclass(frozen=True)
class Invocation:
    action: str
    functional_requirement: str
    service: str
    stack_instance: str
    infrastructure_target: str
    before_command: str
    image: str
    tool: str


async def run_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


async def invoke_automation(ctx, invoc):
    print(invoc)
    invocation = Invocation(**invoc)
    handler = tool_factory.get_handler(invocation)
    result, error_message = await run_in_executor(handler.handle)
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
    functions = [invoke_automation]
    queue_name = config.settings.agent_name
    redis_settings = RedisSettings(host=config.settings.redis_host,
                                   port=config.settings.redis_port)
