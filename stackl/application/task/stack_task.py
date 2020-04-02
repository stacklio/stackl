from task import Task, logger


class StackTask(Task):

    @property
    def valid_subtasks(self):
        return [
            "CREATE",
            "UPDATE",
            "DELETE",
        ]

    def _load_json_object(self, json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'stack_task'
        self.requester_auth = json_obj.get('requester_auth', None)
        self.json_data = json_obj.get('json_data', None)
        self.send_channel = "agent"
        given_subtasks_list = json_obj.get('subtasks', [None])
        if all(subtasks in self.valid_subtasks for subtasks in given_subtasks_list):
            self.subtasks = given_subtasks_list
        else:
            logger.info("[StackTask] The given StackTask contains invalid tasks")
            raise Exception("The given StackTask contains invalid tasks")
