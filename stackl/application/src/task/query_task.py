import json
import sys

from enums.cast_type import CastType
from task import Task

class QueryTask(Task):
    @property
    def valid_tasks(self):
        return [ 
        "TBD"  
    ] 

    def __init__(self,task_data):
        super(QueryTask, self).__init__(task_data)

    def _load_json_object(self,json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'query'
        self.function = json_obj.get('function',None)
        self.args = json_obj.get('args',[])
        self.attribute = json_obj.get('attribute',None)
        self.cast_type = json_obj.get('cast_type', CastType.BROADCAST.value)
        if self.function is None and self.attribute is None:
            raise Exception('function or attrbute must be set in QueryTask')
