from task import Task


class ResultTask(Task):
    @property
    def valid_subtasks(self):
        return [
            "RESULT"  # PUT: Create or Update (Overwrite) the document
        ]

    def __init__(self, task_data):
        super(ResultTask, self).__init__(task_data)

    def _load_json_object(self, json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'result'
        self.result = json_obj.get('result', None)
        self._parse_source_task(json_obj)

    def _parse_source_task(self, json_obj):
        source_task = json_obj.get('source_task', None)
        if source_task == None:
            raise Exception('source_task must be set when creating a ResultTask')
        if type(source_task) == str:
            self.source_task = str(source_task)
        elif type(source_task) == dict:
            self.source_task = str(source_task)
        elif issubclass(type(source_task), Task):
            self.source_task = source_task.as_json_string()
        else:
            raise Exception('Unsupported type for source_task: ' + str(type(source_task)))
