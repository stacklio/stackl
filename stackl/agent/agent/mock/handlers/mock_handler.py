import time

from ..configurator_handler import ConfiguratorHandler


class MockHandler(ConfiguratorHandler):
    def __init__(self, invoc):
        self._invoc = invoc

    def create_job_command(self, handle_obj):
        return None

    def create_delete_command(self, handle_obj):
        return None

    def handle(self):
        print(self._invoc)
        print(
            "This is a fake handler, nothing is actually provisioned, sleeping 5 seconds"
        )
        time.sleep(5)
        print("fake provisioning done")
        return 0, "mock fake"
