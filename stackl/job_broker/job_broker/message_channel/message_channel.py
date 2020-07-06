from abc import ABC, abstractmethod


class MessageChannel(ABC):
    @abstractmethod
    def register_agent(self, name, selector):
        pass

    @abstractmethod
    def unregister_agent(self):
        pass

    @abstractmethod
    def listen_for_jobs(self, callback_function):
        pass

    @abstractmethod
    def give_task_and_get_result(self, task):
        pass