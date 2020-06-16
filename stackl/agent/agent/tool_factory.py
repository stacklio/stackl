from abc import ABC, abstractmethod


class ToolFactory(ABC):
    @abstractmethod
    def get_handler(self, invoc):
        pass
