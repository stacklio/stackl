from abc import ABC, abstractmethod


class MessageChannel(ABC):
    @abstractmethod
    def publish(self, task):
        pass

    @abstractmethod
    def push(self, name, *values):
        pass

    @abstractmethod
    def pop(self, name):
        pass

    @abstractmethod
    def _pubsub_channels(self, pubsub, channels, action='subscribe'):
        pass
