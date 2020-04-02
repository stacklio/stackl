from abc import ABC, abstractmethod


class MessageChannel(ABC):

    def __init__(self):
        self.started = False

    @abstractmethod
    def start(self, task_handler, subscribe_channels):
        pass

    @abstractmethod
    def start_pubsub(self, subscribe_channels):
        pass

    @abstractmethod
    def publish(self, task):
        pass

    # iterations -1 is infitinte loop
    @abstractmethod
    def listen_permanent(self, channels):
        pass

    @abstractmethod
    def listen(self, channel, wait_time=5):
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
