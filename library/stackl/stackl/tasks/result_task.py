from typing import Any

from .task import Task


class ResultTask(Task):
    topic: str = "result_task"
    result_msg: str = None
    return_result: Any = None
    result_code: int = None
    subtype: str = "RESULT"
    source_task: Task = None
    status: str = None
    source_task_id: str = None
