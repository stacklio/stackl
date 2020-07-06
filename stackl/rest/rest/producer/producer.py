from abc import ABC, abstractmethod

from stackl.tasks.task import Task


class Producer(ABC):
    @abstractmethod
    def give_task_and_get_result(self, task: Task):
        pass
