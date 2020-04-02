from abc import ABC, abstractmethod

class AgentBroker(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def get_agent_for_task(self, task):
        pass

    @abstractmethod
    def send_job_to_agent(self, agent_connect_info, job):
        pass

    @abstractmethod
    def create_job_for_agent(self, stack_instance, action, document_manager):
        pass
