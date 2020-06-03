from task import Task, logger


class SnapshotTask(Task):
    @property
    def valid_subtypes(self):
        return [
            "GET_SNAPSHOT",
            "LIST_SNAPSHOT",
            "CREATE_SNAPSHOT",
            "RESTORE_SNAPSHOT",
            "DELETE_SNAPSHOT"
        ]

    def _load_json_object(self, json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'snapshot_task'
        self.snapshot_doc_type = json_obj.get('snapshot_doc_type', None)
        self.snapshot_doc_name = json_obj.get('snapshot_doc_name', None)
        subtype = json_obj.get('subtype', [None])
        if subtype in self.valid_subtypes:
            self.subtype = subtype
        else:
            logger.info(
                "[SnapshotTask] The given SnapshotTask has an invalid subtype")
            raise Exception("The given SnapshotTask has an invalid subtype")
