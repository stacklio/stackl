from enum import Enum

from .agent_task import AgentTask
from .document_task import DocumentTask
from .report_task import ReportTask
from .result_task import ResultTask
from .snapshot_task import SnapshotTask
from .stack_task import StackTask


class TaskTopic(Enum):
    agent = AgentTask
    report = ReportTask
    result = ResultTask
    document = DocumentTask
    snapshot = SnapshotTask
    stack = StackTask
