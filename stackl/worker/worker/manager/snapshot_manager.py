import logging

from stackl.enums.cast_type import CastType
from stackl.enums.stackl_codes import StatusCode
from stackl.message_channel.message_channel_factory import MessageChannelFactory
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl.utils.general_utils import get_timestamp
from stackl.tasks.result_task import ResultTask

from .manager import Manager

logger = logging.getLogger("STACKL_LOGGER")


class SnapshotManager(Manager):
    def __init__(self):
        super(SnapshotManager, self).__init__()

        task_broker_factory = TaskBrokerFactory()
        self.task_broker = task_broker_factory.get_task_broker()
        message_channel_factory = MessageChannelFactory()
        self.message_channel = message_channel_factory.get_message_channel()

        self.document_manager = None  # To be given after initalisation by manager_factory

    def handle_task(self, task):
        logger.debug(f"[SnapshotManager] handling snapshot_task {task}")
        if task["subtype"] == "GET_SNAPSHOT":
            (type_doc, name_doc, snapshot_nb) = task["args"]
            return_result = self.get_snapshot(type_doc, name_doc, snapshot_nb)
        elif task["subtype"] == "LIST_SNAPSHOT":
            (type_doc, name_doc) = task["args"]
            return_result = self.list_snapshots(type_doc, name_doc)
        elif task["subtype"] == "CREATE_SNAPSHOT":
            (type_name, name) = task["args"]
            return_result = self.create_snapshot(type_name, name)
        elif task["subtype"] == "RESTORE_SNAPSHOT":
            (type_doc, name_doc, snapshot_nb) = task["args"]
            return_result = self.restore_snapshot(type_doc, name_doc,
                                                  snapshot_nb)
        elif task["subtype"] == "DELETE_SNAPSHOT":
            (type_doc, name_doc, snapshot_nb) = task["args"]
            return_result = self.delete_snapshot(type_doc, name_doc,
                                                 snapshot_nb)
        logger.debug(
            f"[SnapshotManager] Succesfully handled snapshot task. Creating ResultTask."
        )
        result_task = ResultTask.parse_obj({
            'channel': task['return_channel'],
            'result_msg':
            f"Document with type '{task['subtype']}' was handled",
            'return_result': return_result,
            'result_code': StatusCode.OK,
            'cast_type': CastType.BROADCAST.value,
            'source_task': task
        })
        self.message_channel.publish(result_task)

    def rollback_task(self, task):
        pass

    def get_snapshots(self, type_doc, name_doc, snapshot_nb=1):
        logger.debug(
            f"[SnapshotManager] get_snapshot. Get the '{snapshot_nb}' most recent snapshot for doc with type '{type_doc}' and name '{name_doc}'"
        )
        results = self.document_manager.get_snapshots(type_doc, name_doc)

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
            f"[SnapshotManager] snapshot_to_restore. Type and name doc and most recent snapshot number to restore: '{type_doc_to_restore}' - '{name_doc_to_restore}' - '{snapshot_nb}'"
        )
        snapshot_document = self.get_snapshot(type_doc_to_restore,
                                              name_doc_to_restore, snapshot_nb)
        logger.debug(
            f"[SnapshotManager] snapshot_to_restore. Snapshot to restore to: '{snapshot_document}'"
        )
        if snapshot_document == {}:
            return StatusCode.NOT_FOUND
        result = self.document_manager.write_document(
            snapshot_document["snapshot"], overwrite=True, make_snapshot=False)
        return result

    def delete_snapshot(self, type_doc_to_delete, name_doc_to_delete,
                        snapshot_nb):
        logger.debug(
            f"[SnapshotManager] snapshot_to_delete. Type and name doc and most recent snapshot number to delete: '{type_doc_to_delete}' - '{name_doc_to_delete}' - '{snapshot_nb}'"
        )
        snapshot_document = self.get_snapshot(type_doc_to_delete,
                                              name_doc_to_delete, snapshot_nb)
        logger.debug(
            f"[SnapshotManager] snapshot_to_delete. Snapshot to delete: '{snapshot_document}'"
        )
        result = self.document_manager.delete_document(
            type=snapshot_document['type'], name=snapshot_document['name'])
        return result
