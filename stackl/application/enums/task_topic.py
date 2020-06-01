from enum import Enum

from task.document_task import DocumentTask
from task.report_task import ReportTask
from task.result_task import ResultTask
from task.snapshot_task import SnapshotTask
from task.stack_task import StackTask


class TaskTopic(Enum):
    report = ReportTask
    result = ResultTask
    document = DocumentTask
    snapshot = SnapshotTask
    stack = StackTask
