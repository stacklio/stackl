from .task import Task


class ResultTask(Task):
    topic: str = "result"
    result_msg: str = None
    return_result: str = None
    result_code: str = None
    subtype: str = "RESULT"
    source_task: Task = None
    status: str = None
