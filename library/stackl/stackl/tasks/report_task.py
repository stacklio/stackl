from typing import Any

from .task import Task


class ReportTask(Task):
    topic: str = "report"
    function: str
    args: Any = None
    attribute: Any = None

    @property
    def valid_subtypes(self):
        pass
