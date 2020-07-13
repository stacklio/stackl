import os

from arq.connections import RedisSettings

from agent.docker.docker_tool_factory import DockerToolFactory
from agent.kubernetes.kubernetes_tool_factory import KubernetesToolFactory
from agent.mock.mock_tool_factory import MockToolFactory

if os.environ.get("AGENT_NAME", None) == "kubernetes":
    tool_factory = KubernetesToolFactory()
elif os.environ.get("AGENT_NAME", None) == "docker":
    tool_factory = DockerToolFactory()
elif os.environ.get("AGENT_NAME", None) == "mock":
    tool_factory = MockToolFactory()


async def invoke_automation(ctx, invoc):
    handler = tool_factory.get_handler(invoc)
    result, error_message = handler.handle()
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
    queue_name = os.environ["QUEUE_NAME"]
    redis_settings = RedisSettings(host=os.environ["REDIS_HOST"],
                                   port=os.environ.get("REDIS_PORT", 6379))
