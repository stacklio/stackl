from enum import Enum

from task.document_task import DocumentTask
from task.ping_task import PingTask
from task.report_task import ReportTask
from task.result_task import ResultTask


class TaskTopic(Enum):
    report = ReportTask
    ping = PingTask
    result = ResultTask
    document = DocumentTask
