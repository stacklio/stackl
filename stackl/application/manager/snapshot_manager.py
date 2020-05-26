import logging

logger = logging.getLogger("STACKL_LOGGER")

from enums.cast_type import CastType
from enums.stackl_codes import StatusCode
from task_broker.task_broker_factory import TaskBrokerFactory
from message_channel.message_channel_factory import MessageChannelFactory
from manager import Manager
from utils.general_utils import get_timestamp
from task.result_task import ResultTask
from task.snapshot_task import SnapshotTask


class SnapshotManager(Manager):
    def __init__(self):
        super(SnapshotManager, self).__init__()

        task_broker_factory = TaskBrokerFactory()
        self.task_broker = task_broker_factory.get_task_broker()
        message_channel_factory = MessageChannelFactory()
        self.message_channel = message_channel_factory.get_message_channel()

        self.document_manager = None  #To be given after initalisation by manager_factory

    def handle_task(self, snapshot_task):
        logger.debug(
            f"[SnapshotManager] handling snapshot_task {snapshot_task}")
        if snapshot_task["subtype"] == "GET_SNAPSHOT":
            (type_doc, name_doc, snapshot_nb) = snapshot_task["args"]
            return_result = self.get_snapshot(type_doc, name_doc, snapshot_nb)
        elif snapshot_task["subtype"] == "LIST_SNAPSHOT":
            (type_doc, name_doc) = snapshot_task["args"]
            return_result = self.list_snapshots(type_doc, name_doc)
        elif snapshot_task["subtype"] == "CREATE_SNAPSHOT":
            (type_name, name) = snapshot_task["args"]
            return_result = self.create_snapshot(type_name, name)
        elif snapshot_task["subtype"] == "RESTORE_SNAPSHOT":
            (type_doc, name_doc, snapshot_nb) = snapshot_task["args"]
            return_result = self.restore_snapshot(type_doc, name_doc,
                                                  snapshot_nb)
        elif snapshot_task["subtype"] == "DELETE_SNAPSHOT":
            (type_doc, name_doc, snapshot_nb) = snapshot_task["args"]
            return_result = self.delete_snapshot(type_doc, name_doc,
                                                 snapshot_nb)
        logger.debug(
            f"[SnapshotManager] Succesfully handled snapshot task. Creating ResultTask."
        )
        resultTask = ResultTask({
            'channel': snapshot_task['return_channel'],
            'result_msg':
            f"Document with type '{snapshot_task['subtype']}' was handled",
            'return_result': return_result,
            'result_code': StatusCode.OK,
            'cast_type': CastType.BROADCAST.value,
            'source_task': snapshot_task
        })
        self.message_channel.publish(resultTask)

    def rollback_task(self, task):
        pass

    def get_snapshot(self, type_doc, name_doc, snapshot_nb):
        logger.debug(
            f"[SnapshotManager] get_snapshot.  Get the {snapshot_nb} most recent snapshot for doc with type and name '{type_doc}' and '{name_doc}'"
        )
        results = self.list_snapshots(type_doc, name_doc)
        logger.debug(
            f"[SnapshotManager] get_snapshot.  Selecting nb '{snapshot_nb}' from the retrieved list of snapshots: '{results}'"
        )
        if (snapshot_nb - 1) < len(results):
            return results[snapshot_nb - 1][1]
        else:
            return {}

    def list_snapshots(self, type_doc, name_doc):
        logger.debug(
            f"[SnapshotManager] list_snapshots.  Get all snapshots for doc with type and name '{type_doc}' and '{name_doc}'"
        )
        result = self.document_manager.collect_documents(
            "snapshot_" + type_doc, name_doc)
        result = sorted(result, reverse=True, key=lambda item: item[0][-25:-5])
        return result

    def create_snapshot(self, type_name, name):
        logger.debug(
            f"[SnapshotManager] create_snapshot.  Creating snapshot for document with type '{type_name}' and name '{name}'"
        )
        snapshot_document = {}
        document = self.document_manager.get_document(type=type_name,
                                                      name=name)
        snapshot_document['category'] = "history"
        snapshot_document['type'] = "snapshot"
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

    def restore_snapshot(self,
                         type_doc_to_restore,
                         name_doc_to_restore,
                         snapshot_nb=1):
        logger.debug(
            f"[SnapshotManager] snapshot_to_restore.  Type and name doc to restore: '{type_doc_to_restore}' and '{name_doc_to_restore}'. Number most recent snapshot to restore to: '{snapshot_nb}'"
        )
        snapshot_document = self.get_snapshot(type_doc_to_restore,
                                              name_doc_to_restore, snapshot_nb)
        logger.debug(
            f"[SnapshotManager] snapshot_to_restore.  Snapshot to restore to: '{snapshot_document}'"
        )
        if snapshot_document == {}:
            return StatusCode.NOT_FOUND
        result = self.document_manager.write_document(
            snapshot_document["snapshot"], overwrite=True, make_snapshot=False)
        return result

    def delete_snapshot(self, type_doc_to_delete, name_doc_to_delete,
                        snapshot_nb):
        logger.debug(
            f"[SnapshotManager] snapshot_to_delete.  Snapshot to delete for type and name doc: '{type_doc_to_delete}' and '{name_doc_to_delete}. Number most recent snapshot to delete: '{snapshot_nb}'"
        )
        snapshot_document = self.get_snapshot(type_doc_to_delete,
                                              name_doc_to_delete, snapshot_nb)
        logger.debug(
            f"[SnapshotManager] snapshot_to_delete.  Snapshot to delete: '{snapshot_document}'"
        )

        result = self.document_manager.delete_document(
            type=snapshot_document['type'], name=snapshot_document['name'])
        return result