from pydantic import validator

from .task import Task


class SnapshotTask(Task):
    topic: str = "snapshot_task"
    snapshot_doc_type: str = None
    snapshot_doc_name: str = None
    subtype: str = None

    @validator('subtype')
    def valid_subtypes(cls, subtype):
        subtypes = [
            "GET_SNAPSHOT", "GET_SNAPSHOTS", "CREATE_SNAPSHOT",
            "RESTORE_SNAPSHOT", "DELETE_SNAPSHOT"
        ]
        if subtype not in subtypes:
            raise ValueError("subtype for SnapshotTask not valid")
        return subtype
