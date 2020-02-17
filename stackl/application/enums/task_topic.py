from enum import Enum

from task.document_task import DocumentTask
from task.ping_task import PingTask
from task.query_task import QueryTask
from task.result_task import ResultTask


class TaskTopic(Enum):
    query = QueryTask
    ping = PingTask
    result = ResultTask
    document = DocumentTask
