import json
import logging
import os

from datastore import DataStore
from enums.stackl_codes import StatusCode

logger = logging.getLogger("STACKL_LOGGER")


class LocalFileSystemStore(DataStore):
    def __init__(self, root):
        super(LocalFileSystemStore, self).__init__()
        self.file_system_root = root

    @property
    def datastore_url(self):
        return self.file_system_root + os.sep

    def get(self, **keys):
        get_all = False
        if keys.get("document_name"):
            if keys.get("type") in keys.get("document_name"):
                document_key = self.datastore_url + keys.get(
                    "category") + '/' + keys.get("document_name") + ".json"
            else:
                document_key = self.datastore_url + keys.get(
                    "category") + '/' + keys.get("type") + '_' + keys.get(
                        "document_name") + ".json"
            if not os.path.exists(document_key):
                return self._create_store_response(
                    status_code=StatusCode.NOT_FOUND,
                    content="File is not found")
        else:  # This means we need to get all the documents of the type
            get_all = True
            document_key = self.datastore_url + keys.get("category") + '/'
        logger.debug(f"[LocalFileSystemStore] get on key '{document_key}'")

        content = []
        try:
            if get_all:
                for dirpath, _, filenames in os.walk(document_key):
                    for file in filenames:
                        logger.debug(
                            f"[LocalFileSystemStore] get_all. Looking at file '{file}' for type {keys.get('type')}"
                        )
                        if file.startswith(
                                keys.get("type")) and file.endswith(".json"):
                            with open(dirpath + file) as file_to_get:
                                content.append(json.load(file_to_get))
                            logger.debug(
                                f"[LocalFileSystemStore] get_all. File found. Added to content. len(content): '{len(content)}'"
                            )
                response = self._create_store_response(
                    status_code=StatusCode.OK, content=content)
            else:
                with open(document_key) as file_to_get:
                    content = json.load(file_to_get)
                response = self._create_store_response(
                    status_code=StatusCode.OK, content=content)
        except Exception as e:  # pylint: disable=broad-except
            response = self._create_store_response(
                status_code=StatusCode.INTERNAL_ERROR,
                content=f"Error getting file. Error '{e}'")
        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for get: {response}")
        return response

    def get_configurator_file(self, configurator_file):
        document_key = self.datastore_url + 'statefiles/' + configurator_file + ".json"
        try:
            with open(document_key, 'r') as storedfile:
                response = self._create_store_response(
                    status_code=StatusCode.CREATED,
                    content=json.load(storedfile))
        except FileNotFoundError:
            response = self._create_store_response(
                status_code=StatusCode.NOT_FOUND, content={})
        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for get: {response}")
        return response

    def put_configurator_file(self, name, configurator_file):
        document_key = self.datastore_url + 'statefiles/' + name + ".json"
        with open(document_key, 'w+') as outfile:
            json.dump(configurator_file,
                      outfile,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))
        with open(document_key, 'r') as storedfile:
            response = self._create_store_response(
                status_code=StatusCode.CREATED, content=json.load(storedfile))
        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for put: {response}")
        return response

    def delete_configurator_file(self, configurator_file):
        document_key = self.datastore_url + 'statefiles/' + configurator_file + ".json"
        os.remove(document_key)
        response = self._create_store_response(status_code=200, content={})
        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for put: {response}")
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

        with open(document_key, 'w+') as outfile:
            json.dump(file,
                      outfile,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))
        with open(document_key, 'r') as storedfile:
            response = self._create_store_response(
                status_code=StatusCode.CREATED, content=json.load(storedfile))

        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for put: {response}")
        return response

    def delete(self, **keys):
        if keys.get("type") in keys.get("document_name"):
            document_key = self.datastore_url + keys.get(
                "category") + '/' + keys.get("document_name") + ".json"
        else:
            document_key = self.datastore_url + keys.get(
                "category") + '/' + keys.get("type") + '_' + keys.get(
                    "document_name") + ".json"
        logger.debug(f"[LocalFileSystemStore] delete on '{document_key}'")

        if os.path.isfile(document_key):
            os.remove(document_key)
            if not os.path.isfile(document_key):
                result = "Success. File was deleted"
            else:
                result = "Fail. File was not succesfully deleted"
        else:  # Show an error ##
            result = "Fail. File is not present"

        response = self._create_store_response(200, result, result)
        logger.debug(
            f"[LocalFileSystemStore] StoreResponse for delete: {response}")
        return response
