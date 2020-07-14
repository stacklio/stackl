from core.manager.document_manager import DocumentManager
from loguru import logger
import time

from stackl.enums.stackl_codes import StatusCode
from stackl.tasks.stack_task import StackTask
from stackl.utils.general_utils import get_timestamp
from .manager import Manager


class SnapshotManager(Manager):
    def __init__(self):
        super(SnapshotManager, self).__init__()
        self.document_manager = DocumentManager()

    def rollback_task(self, task):
        pass

    def get_snapshot(self, name):
        result = self.document_manager.get_document(type="snapshot", name=name)

        return result

    def get_snapshots(self, type_doc, name_doc):
        logger.debug(
            f"[SnapshotManager] get_snapshot. Get the snapshots for doc with type '{type_doc}' and name '{name_doc}'"
        )
        iter_key = f"{type_doc}_{name_doc}"
        results = self.document_manager.get_snapshots("snapshot", iter_key)

        return results

    def create_snapshot(self, type_name, name):
        logger.debug(
            f"[SnapshotManager] create_snapshot. Creating snapshot for document with type '{type_name}' and name '{name}'"
        )
        snapshot_document = {}
        document = self.document_manager.get_document(type=type_name,
                                                      name=name)
        snapshot_document['category'] = "history"
        snapshot_document['type'] = "snapshot"
        snapshot_document['time'] = time.time()
        if type_name not in name:
            snapshot_document['name'] = type_name + "_" + name + "_" + str(
                get_timestamp(spaces=False))
        else:
            snapshot_document['name'] = name + "_" + str(
                get_timestamp(spaces=False))
        snapshot_document['description'] = snapshot_document.get("description")
        snapshot_document["snapshot"] = document
        result = self.document_manager.write_document(snapshot_document)
        return result

    def restore_snapshot(self, snapshot_name):
        logger.debug(
            f"[SnapshotManager] snapshot_to_restore. name doc: '{snapshot_name}'"
        )
        snapshot_document = self.get_snapshot(snapshot_name)
        logger.debug(
            f"[SnapshotManager] snapshot_to_restore. Snapshot to restore to: '{snapshot_document}'"
        )
        if snapshot_document == {}:
            return StatusCode.NOT_FOUND
        result = self.document_manager.write_document(
            snapshot_document['snapshot'], overwrite=True, make_snapshot=False)
        if snapshot_document['snapshot']["type"] == "stack_instance":
            invocation = {
                "stack_instance_name": snapshot_document.snapshot["name"],
                "disable_invocation": False,
                "params": {},
                "secrets": {}
            }
            task = StackTask.parse_obj({
                'channel': 'worker',
                'json_data': invocation,
                'subtype': "UPDATE_STACK",
            })
            logger.info(
                f"[StackInstances PUT] Giving StackTask '{task}' to task_broker"
            )

        return result

    def restore_latest_snapshot(self, type_doc, name_doc):
        snapshots = self.get_snapshots(type_doc, name_doc)
        latest_snapshot = {"time": 0}
        for snapshot in snapshots:
            if snapshot['time'] > latest_snapshot['time']:
                latest_snapshot = snapshot

        self.restore_snapshot(latest_snapshot['name'])

    def delete_snapshot(self, name_doc_to_delete):
        logger.debug(
            f"[SnapshotManager] snapshot_to_delete. name doc to delete:  '{name_doc_to_delete}'"
        )
        snapshot_document = self.get_snapshot(name_doc_to_delete)
        logger.debug(
            f"[SnapshotManager] snapshot_to_delete. Snapshot to delete: '{snapshot_document}'"
        )
        result = self.document_manager.delete_snapshot(
            name=snapshot_document['name'])
        return result
