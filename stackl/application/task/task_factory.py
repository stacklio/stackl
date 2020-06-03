import json

from enums.task_topic import TaskTopic


class TaskFactory:
    @staticmethod
    def create_task(task_data):
        if isinstance(task_data, bytes) or isinstance(task_data, str):
            task_data = json.loads(task_data)
        elif not isinstance(task_data, dict):
            raise Exception("[TaskFactory] task_data must be string or dict")
        task_topic = task_data.get('topic', 'unknown')
        try:
            task = TaskTopic[task_topic].value
            return task(task_data)
        except Exception:
            raise Exception(f"[TaskFactory] Invalid task_topic: {task_topic}")
