import logging

logger = logging.getLogger("STACKL_LOGGER")

from enums.cast_type import CastType
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
        try:
            if snapshot_task["subtype"] == "GET_SNAPSHOT":
                (document_name, snapshot_nb) = snapshot_task["args"]
                result = self.get_snapshot(document_name, snapshot_nb)
            elif snapshot_task["subtype"] == "LIST_SNAPSHOT":
                document_name = snapshot_task["args"]
                result = self.list_snapshots(document_name)
            elif snapshot_task["subtype"] == "CREATE_SNAPSHOT":
                (type_name, name) = snapshot_task["args"]
                result = self.create_snapshot(type_name, name)
            elif snapshot_task["subtype"] == "RESTORE_SNAPSHOT":
                (document_name, snapshot_nb) = snapshot_task["args"]
                result = self.restore_snapshot(document_name, snapshot_nb)
            elif snapshot_task["subtype"] == "DELETE_SNAPSHOT":
                (document_name, snapshot_nb) = snapshot_task["args"]
                result = self.delete_snapshot(document_name, snapshot_nb)
            logger.debug(
                f"[SnapshotManager] Succesfully handled snapshot task. Creating ResultTask."
            )
            resultTask = ResultTask({
                'channel': snapshot_task['return_channel'],
                'result_msg':
                f"Document with type '{snapshot_task['subtype']}' was handled",
                'result': result,
                'cast_type': CastType.BROADCAST.value,
                'source_task': snapshot_task
            })

            self.message_channel.publish(resultTask)
            # )  # this way the STACKL broker is notified of the result and wheter he should remove the task from the task queue
        except Exception as e:  #TODO improve the Exception system in STACKL. TBD as part of Task rework
            logger.error(
                f"[SnapshotManager] Error with processing task. Error: '{e}'")

    def get_snapshot(self, document_name, snapshot_nb):
        logger.debug(
            f"[SnapshotManager] get_snapshot.  Get the {snapshot_nb} most recent snapshot for '{document_name}'"
        )
        results = self.list_snapshots(document_name)
        # sorted(results, key=lambda filename: filename[0])
        logger.debug(
            f"[SnapshotManager] get_snapshot.  Selecting nb '{snapshot_nb}' from the retrieved list of snapshots: '{results}'"
        )
        return results[snapshot_nb - 1][1]

    def list_snapshots(self, document_name):
        logger.debug(
            f"[SnapshotManager] list_snapshots.  Get all snapshots for '{document_name}'"
        )
        result = self.document_manager.collect_documents(
            "snapshot", document_name)
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

    def restore_snapshot(self, document_to_restore, snapshot_nb):
        logger.debug(
            f"[SnapshotManager] snapshot_to_restore.  Document to restore: '{document_to_restore}'. Number most recent snapshot to restore to: '{snapshot_nb}'"
        )
        snapshot_document = self.get_snapshot(document_to_restore, snapshot_nb)
        logger.debug(
            f"[SnapshotManager] snapshot_to_restore.  Snapshot to restore to: '{snapshot_document}'"
        )

        result = self.document_manager.write_document(
            snapshot_document["snapshot"], overwrite=True, make_snapshot=False)
        return result

    def delete_snapshot(self, snapshot_to_delete, snapshot_nb):
        logger.debug(
            f"[SnapshotManager] snapshot_to_delete.  Snapshot to delete: '{snapshot_to_delete}'. Number most recent snapshot to delete: '{snapshot_nb}'"
        )
        snapshot_document = self.get_snapshot(snapshot_to_delete, snapshot_nb)
        logger.debug(
            f"[SnapshotManager] snapshot_to_delete.  Snapshot to delete: '{snapshot_document}'"
        )

        result = self.document_manager.delete_document(
            type=snapshot_document['type'], name=snapshot_document['name'])
        return result