from enum import Enum

from task.document_task import DocumentTask
from task.report_task import ReportTask
from task.result_task import ResultTask


class TaskTopic(Enum):
    report = ReportTask
    result = ResultTask
    document = DocumentTask
