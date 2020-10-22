"""Module for using Local File System as datastore"""
import json
import os

from loguru import logger

from core.enums.stackl_codes import StatusCode
from .datastore import DataStore


class LocalFileSystemStore(DataStore):
    """Implementation of LocalFileSystemStore"""

    def __init__(self, root):
        super().__init__()
        self.file_system_root = root

    @property
    def datastore_url(self):
        """Returns the datastore url including seperator of the os"""
        return self.file_system_root + os.sep

    def get(self, **keys):
        """Gets a document from the filesystem"""
        if keys.get("type") in keys.get("name"):
            document_key = self.datastore_url + keys.get(
                "category") + '/' + keys.get("name") + ".json"
        else:
            document_key = self.datastore_url + keys.get(
                "category") + '/' + keys.get("type") + '_' + keys.get(
                "name") + ".json"
        if not os.path.exists(document_key):
            return self._create_store_response(
                status_code=StatusCode.NOT_FOUND, content="File is not found")
        logger.debug(f"[LocalFileSystemStore] get on key '{document_key}'")
        try:
            with open(document_key) as file_to_get:
                content = json.load(file_to_get)
            response = self._create_store_response(status_code=StatusCode.OK,
                                                   content=content)
        except OSError as err:
            response = self._create_store_response(
                status_code=StatusCode.INTERNAL_ERROR,
                content=f"Error getting file. Error '{err}'")
        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for get: {response}")
        return response

    def get_all(self, category, document_type, wildcard_prefix=None):
        """Get all documents of a type from filesystem"""
        document_key = self.datastore_url + category + '/'
        logger.debug(
            f"[LocalFileSystemStore] get_all in '{document_key}' for type '{document_type}'"
        )

        content = []
        try:
            for dirpath, _, filenames in os.walk(document_key):
                for file in filenames:
                    logger.debug(
                        f"Looking at files '{file}' that have type '{document_type}'"
                    )
                    if document_type in file and file.endswith(".json"):
                        if wildcard_prefix is not None and wildcard_prefix not in file:
                            logger.debug(
                                f"{wildcard_prefix} not in {file}"
                            )
                            continue
                        with open(dirpath + file) as file_to_get:
                            content.append(json.load(file_to_get))
                        logger.debug(
                            f"File found. Added to content. len(content): '{len(content)}'"
                        )
            response = self._create_store_response(status_code=StatusCode.OK,
                                                   content=content)
        except OSError as err:
            response = self._create_store_response(
                status_code=StatusCode.INTERNAL_ERROR,
                content=f"Error getting file. Error '{err}'")
        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for get_all: {response}")
        return response

    def put(self, file):
        """Update a document from filestore"""
        if file.get("type") in file.get("name"):
            document_key = self.datastore_url + file.get(
                "category") + '/' + file.get("name") + ".json"
        else:
            document_key = self.datastore_url + file.get(
                "category") + '/' + file.get(
                "type") + '_' + file["name"] + ".json"
        logger.debug(
            f"[LocalFileSystemStore] put on '{document_key}' with file {file}")
        try:
            with open(document_key, 'w+') as outfile:
                json.dump(file,
                          outfile,
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': '))
            with open(document_key, 'r') as storedfile:
                response = self._create_store_response(
                    status_code=StatusCode.CREATED,
                    content=json.load(storedfile))
        except OSError as err:
            response = self._create_store_response(
                status_code=StatusCode.INTERNAL_ERROR,
                content=f"Error getting file. Error '{err}'")
        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for put: {response}")
        return response

    def delete(self, **keys):
        """Delete a document from filestore"""
        if keys.get("type") in keys.get("name"):
            document_key = self.datastore_url + keys.get(
                "category") + '/' + keys.get("name") + ".json"
        else:
            document_key = self.datastore_url + keys.get(
                "category") + '/' + keys.get("type") + '_' + keys.get(
                "name") + ".json"
        logger.debug(f"[LocalFileSystemStore] delete on '{document_key}'")
        try:
            if os.path.isfile(document_key):
                os.remove(document_key)
                if not os.path.isfile(document_key):
                    result = "Success. File was deleted"
                else:
                    raise FileExistsError(
                        "Fail. File was not succesfully deleted")
        except OSError as err:
            response = self._create_store_response(
                status_code=StatusCode.INTERNAL_ERROR,
                content=f"Error deleting file. Error '{err}'")
        response = self._create_store_response(StatusCode.OK, result, result)
        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for delete: {response}")
        return response
