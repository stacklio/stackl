import json

from enums.task_topic import TaskTopic


class TaskFactory:
    @staticmethod
    def create_task(task_data):
        if type(task_data) == bytes or type(
                task_data
        ) == str:  # changed from python2 to python3, str are now bytes
            task_data = json.loads(task_data)
        elif type(task_data) != dict:
            raise Exception("[TaskFactory] task_data must be string or dict")
        task_topic = task_data.get('topic', 'unknown')
        try:
            task = TaskTopic[task_topic].value
            return task(task_data)
        except Exception:
            raise Exception("[TaskFactory] Invalid task_topic: " +
                            str(task_topic))
