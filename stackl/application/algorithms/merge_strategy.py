import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("STACKL_LOGGER")


#TODO WIP for future use
class MergeStrategy(ABC):
    @abstractmethod
    def merge(self, source_object, merge_object):
        pass


class SimpleMergeStrategy(MergeStrategy):
    def __init__(self):
        super(SimpleMergeStrategy, self).__init__('SimpleMergeStrategy')

    def merge(self, source_object, merge_object):
        source_object.update(merge_object)
        return source_object


class DeepMergeStrategy(MergeStrategy):
    def __init__(self):
        super(DeepMergeStrategy, self).__init__('DeepMergeStrategy')
        self.primitive_array = [int, bool, list, str, float]

    def merge(self, source_object, merge_object):
        return self._merge_dict(source_object, merge_object)

    def _merge_dict(self, source_object, merge_object):
        for key in merge_object:
            if key in source_object:
                source_val = source_object[key]
                merge_val = merge_object[key]
                if type(source_val) != type(merge_val):
                    raise Exception(
                        "Deep merge error: types of values in merge did not match!"
                    )
                if type(merge_val) == dict:
                    source_object[key] = self._merge_dict(
                        source_val, merge_val)
                elif type(merge_val) == list:
                    # Check if all values in the list are dicts
                    if (all(type(n) is dict for n in source_val)
                            and all(type(n) is dict for n in merge_val)):
                        # Merge both arrays
                        merged_list = source_val + merge_val
                        # Filter duplicate dicts
                        source_object[key] = [
                            dict(t)
                            for t in {tuple(d.items())
                                      for d in merged_list}
                        ]
                    # Check if all values in the list are primitive types
                    elif (all(
                            type(n) in self.primitive_array
                            for n in source_val) and all(
                                type(n) in self.primitive_array
                                for n in merge_val)):
                        source_object[key] = list(set(source_val + merge_val))
                    else:
                        raise Exception(
                            "Deep merge error: Cannot merge arrays with different types!"
                        )
                else:
                    source_object[key] = merge_val
            else:
                source_object[key] = merge_object[key]
        return source_object
