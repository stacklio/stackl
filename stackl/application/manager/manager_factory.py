import logging

from manager.document_manager import DocumentManager
from manager.snapshot_manager import SnapshotManager
from manager.stack_manager import StackManager
from manager.user_manager import UserManager
from utils.stackl_singleton import Singleton

logger = logging.getLogger("STACKL_LOGGER")


class ManagerFactory(metaclass=Singleton):
    def __init__(self):
        logger.info("[ManagerFactory] Creating Managers")

        # The managers need acccess to the manager factory to get access to the other managers.
        # This makes the order in which the managers are initialized important where the document manager needs to be first
        self.document_manager = DocumentManager()
        self.snapshot_manager = SnapshotManager()
        self.stack_manager = StackManager()
        self.user_manager = UserManager()

        self.document_manager.snapshot_manager = self.snapshot_manager
        self.snapshot_manager.document_manager = self.document_manager
        self.stack_manager.document_manager = self.document_manager
        self.stack_manager.snapshot_manager = self.snapshot_manager
        self.user_manager.document_manager = self.document_manager

    def get_snapshot_manager(self):
        return self.snapshot_manager

    def get_snapshot_manager(self):
        return self.snapshot_manager

    def get_document_manager(self):
        return self.document_manager

    def get_stack_manager(self):
        return self.stack_manager

    def get_user_manager(self):
        return self.user_manager
