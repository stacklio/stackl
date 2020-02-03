import sys

from task import Task

class PingTask(Task):

    @property
    def valid_subtasks(self):
        return [ 
        "PING"
    ] 

    def __init__(self, task_data):
        super(PingTask, self).__init__(task_data)

    def _load_json_object(self,json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'ping'
