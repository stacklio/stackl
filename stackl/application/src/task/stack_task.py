import json
import sys

from task import Task, logger

class StackTask(Task):

    @property
    def valid_subtasks(self):
        return [ 
        "CREATE",
        "UPDATE",
        "DELETE",
        ]
    def __init__(self, task_data):
        super(StackTask, self).__init__(task_data)

    def _load_json_object(self,json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'stack_task'
        self.requester_auth = json_obj.get('requester_auth', None)     
        self.json_data = json_obj.get('json_data', None)   
        self.send_channel = "agent"
        given_subtasks_list = json_obj.get('subtasks', [None])
        if all(subtasks in self.valid_subtasks for subtasks in given_subtasks_list):
            self.subtasks = given_subtasks_list
        else:
            logger.log("[StackTask] The given StackTask contains invalid tasks")
            raise Exception("The given StackTask contains invalid tasks")
