import sys


from .merge_strategy import SimpleMergeStrategy, DeepMergeStrategy
from logger import Logger
from utils.stackl_singleton import Singleton

class StrategyFactory(metaclass=Singleton):

    @staticmethod
    def create_merge_strategy(base_object={}):
        merge_strategy = base_object.get('merge_strategy', 'simple')
        if merge_strategy == 'deep':
            return DeepMergeStrategy()
        else:
            return SimpleMergeStrategy()
