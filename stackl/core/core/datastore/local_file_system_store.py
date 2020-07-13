import json
import logging
import os

from .datastore import DataStore
from stackl.enums.stackl_codes import StatusCode

from loguru import logger


class LocalFileSystemStore(DataStore):
    def __init__(self, root):
        super(LocalFileSystemStore, self).__init__()
        self.file_system_root = root

    @property
    def datastore_url(self):
        return self.file_system_root + os.sep

    def get(self, **keys):
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

    def get_all(self, category, type, wildcard_prefix=None):
        document_key = self.datastore_url + category + '/'
        logger.debug(
            f"[LocalFileSystemStore] get_all in '{document_key}' for type '{type}'"
        )

        content = []
        try:
            for dirpath, _, filenames in os.walk(document_key):
                for file in filenames:
                    logger.debug(
                        f"[LocalFileSystemStore] get_all. Looking at files '{file}' that have type '{type}'"
                    )
                    if type in file and file.endswith(".json"):
                        if wildcard_prefix is not None and wildcard_prefix not in file:
                            logger.debug(
                                f"[LocalFileSystemStore] {wildcard_prefix} not in {file}"
                            )
                            continue
                        with open(dirpath + file) as file_to_get:
                            content.append(json.load(file_to_get))
                        logger.debug(
                            f"[LocalFileSystemStore] get_all. File found. Added to content. len(content): '{len(content)}'"
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
