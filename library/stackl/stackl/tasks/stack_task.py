from .task import Task, logger


class StackTask(Task):
    @property
    def valid_subtypes(self):
        return [
            "GET_STACK",
            "GET_ALL_STACKS",
            "CREATE_STACK",
            "UPDATE_STACK",
            "DELETE_STACK",
        ]

    def _load_json_object(self, json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'stack_task'
        self.json_data = json_obj.get('json_data', None)
        self.send_channel = "agent"
        subtype = json_obj.get('subtype', [None])
        if subtype in self.valid_subtypes:
            self.subtype = subtype
        else:
            logger.info(
                "[StackTask] The given StackTask has an invalid subtype")
            raise Exception("The given StackTask has an invalid subtype")
