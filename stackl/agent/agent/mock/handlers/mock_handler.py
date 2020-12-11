"""
Module used for MockHandler
"""

import time


class MockHandler:
    """
    Mockhandler will implement the create and delete commands, but won't actually do anything

    It will just fake provision something
    """
    def __init__(self, invoc):
        self._invoc = invoc

    def handle(self):
        """
        Handles the execution, in this case nothing will happen
        """
        print(self._invoc)
        print(
            "This is a fake handler, nothing is actually provisioned, sleeping 5 seconds"
        )
        time.sleep(5)
        print("fake provisioning done")
        return 0, "mock fake"
