from utils.stackl_singleton import Singleton
from .merge_strategy import SimpleMergeStrategy, DeepMergeStrategy

#TODO WIP for future use
class StrategyFactory(metaclass=Singleton):

    @staticmethod
    def create_merge_strategy(base_object=None):
        merge_strategy = base_object.get('merge_strategy', 'simple')
        if merge_strategy == 'deep':
            return DeepMergeStrategy()
        else:
            return SimpleMergeStrategy()
