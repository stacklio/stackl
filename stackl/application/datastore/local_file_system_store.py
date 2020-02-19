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
                document_key = self.datastore_url + keys.get("category") + '/' + keys.get("document_name") + ".json"
            else:
                document_key = self.datastore_url + keys.get("category") + '/' + keys.get("type") + '_' + keys.get(
                    "document_name") + ".json"
            if not os.path.exists(document_key):
                return self._create_store_response(status_code=StatusCode.NOT_FOUND, content="File is not found")
        else:  # This means we need to get all the documents of the type
            get_all = True
            document_key = self.datastore_url + keys.get("category") + '/'

        logger.debug("[LocalFileSystemStore] get on key '{0}'".format(document_key))

        content = []
        try:
            if get_all:
                for dirpath, _, filenames in os.walk(document_key):
                    for file in filenames:
                        logger.debug(
                            "[LocalFileSystemStore] get_all. Looking at file '{0}' for type {1}".format(file, keys.get(
                                "type")))
                        if file.startswith(keys.get("type")):
                            with open(dirpath + file) as file_to_get:
                                content.append(json.load(file_to_get))
                            logger.debug(
                                "[LocalFileSystemStore] get_all. File found. Added to content. len(content): '{0}'".format(
                                    len(content)))
                response = self._create_store_response(status_code=StatusCode.OK, content=content)
            else:
                with open(document_key) as file_to_get:
                    content = json.load(file_to_get)
                response = self._create_store_response(status_code=StatusCode.OK, content=content)
        except Exception as e:
            response = self._create_store_response(status_code=StatusCode.INTERNAL_ERROR,
                                                   content="Error getting file. Error '{}'".format(e))
        logger.debug("[LocalFileSystemStore] StoreResponse for get: " + str(response))
        return response

    def put(self, file):
        if file.get("type") in file.get("name"):
            document_key = self.datastore_url + file.get("category") + '/' + file.get("name") + ".json"
        else:
            document_key = self.datastore_url + file.get("category") + '/' + file.get("type") + '_' + file[
                "name"] + ".json"

        logger.debug("[LocalFileSystemStore] put on '{0}' with file {1}".format(document_key, str(file)))

        with open(document_key, 'w+') as outfile:
            json.dump(file, outfile, sort_keys=True, indent=4, separators=(',', ': '))

        with open(document_key, 'r') as storedfile:
            response = self._create_store_response(status_code=StatusCode.CREATED, content=json.load(storedfile))

        logger.debug("[LocalFileSystemStore] StoreResponse for put: " + str(response))
        return response

    def delete(self, **keys):
        if keys.get("type") in keys.get("document_name"):
            document_key = self.datastore_url + keys.get("category") + '/' + keys.get("document_name") + ".json"
        else:
            document_key = self.datastore_url + keys.get("category") + '/' + keys.get("type") + '_' + keys.get(
                "document_name") + ".json"

        logger.debug("[LocalFileSystemStore] delete on '{0}'".format(document_key))
        if os.path.isfile(document_key):
            os.remove(document_key)
            if not os.path.isfile(document_key):
                result = "Success. File was deleted"
            else:
                result = "Fail. File was not succesfully deleted"
        else:  # Show an error ##
            result = "Fail. File is not present"

        response = self._create_store_response(200, result, result)

        logger.debug("[LocalFileSystemStore] StoreResponse for delete: " + str(response))
        return response

    def _check_datastore_exists(self, datastore):
        pass
