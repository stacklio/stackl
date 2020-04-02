from enums.cast_type import CastType
from task import Task

class ReportTask(Task):
    @property
    def valid_subtasks(self):
        return [
            "TBD"
        ]

    def _load_json_object(self, json_obj):
        super()._load_json_object(json_obj)
        self.topic = 'report'
        self.function = json_obj.get('function', None)
        self.args = json_obj.get('args', [])
        self.attribute = json_obj.get('attribute', None)
        self.cast_type = json_obj.get('cast_type', CastType.BROADCAST.value)
        if self.function is None and self.attribute is None:
            raise Exception('function or attrbute must be set in ReportTask')
