from abc import ABC, abstractmethod


class Handler(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def handle(self, handle_obj):
        return None
