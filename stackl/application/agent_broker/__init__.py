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
    def send_obj_to_agent(self, agent_connect_info, obj):
        pass

    #TODO change_obj is no longer a good name. This should be adjusted.
    @abstractmethod
    def create_change_obj(self, stack_instance, action, document_manager):
        pass
