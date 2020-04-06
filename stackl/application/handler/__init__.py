from abc import ABC, abstractmethod


class Handler(ABC):
    def __init__(self, manager_factory):
        if manager_factory:
            self.manager_factory = manager_factory

    @abstractmethod
    def handle(self, handle_obj):
        return None
