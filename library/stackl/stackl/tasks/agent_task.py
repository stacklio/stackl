from .task import Task


class AgentTask(Task):
    topic: str = "agent_task"
    invocation: dict = None
