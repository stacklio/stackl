import json
import requests

from datastore import DataStore
from logger import Logger
from utils.general_utils import get_config_key


class CouchDBStore(DataStore):

    def __init__(self):
        super(CouchDBStore, self).__init__()
        self.logger = Logger("CouchDB Store")
        self.couchdb_url = "https://" + get_config_key("couchDbAdmin") + ":" + get_config_key("couchDbPassword") + "@" \
                           + get_config_key("couchDbHostHttp") + ":" + get_config_key("couchDbPort") + "/"

    @property
    def datastore_url(self):
        if self.couchdb_url is not None:  # [Design] Optionally, if the url would ever change, here we would need to flag that
            return self.couchdb_url
        else:
            self.couchdb_url = "https://" + get_config_key("couchDbAdmin") + ":" + get_config_key(
                "couchDbPassword") + "@" \
                               + get_config_key("couchDbHostHttp") + ":" + get_config_key("couchDbPort") + "/"
            return self.couchdb_url

    def get(self, tenant="nubera", **keys):
        if keys.get("document_name"):
            document_key = tenant + "/" + "_design/" + keys.get("category") \
                           + "/_view/" + keys.get("subcategory") + "?key=%22" + keys.get("document_name") + "%22"
        else:  # This means we need to get all the documents in the category
            document_key = tenant + "/" + "_design/" + keys.get("category") \
                           + "/_view/" + keys.get("subcategory")

        self.logger.log("[CouchDBStore] Requests.get on '{0}' + '{1}'".format(self.datastore_url, document_key))
        result = requests.get(self.datastore_url + document_key, verify="/certs/ca.crt")
        result_content = result.json()

        if 'error' in result_content:
            response = self._create_store_response(400, "Error: {0}. Reason: {1}".format(result_content['error'],
                                                                                         result_content["reason"]))
        elif 'rows' in result_content and len(result_content['rows']) == 0:
            response = self._create_store_response(400, "Empty rows")
        elif 'rows' in result_content and len(result_content['rows']) == 1:
            response = self._create_store_response(result.status_code, result.reason,
                                                   result_content['rows'][0]['value'])
        elif 'rows' in result_content and len(result_content['rows']) > 1:
            return_obj = []
            for row in result_content['rows']:
                return_obj_tmp = row['value']
                return_obj.append(return_obj_tmp)
            response = self._create_store_response(result.status_code, result.reason, return_obj)
        else:
            response = self._create_store_response(400, "Undetermined")
            self.logger.log("[CouchDBStore] Something odd happened. Result Status Code: {0}. Content: {1}".format(
                result.status_code, result_content))

        self.logger.log("[CouchDBStore] StoreResponse for get: " + str(response))
        return response

    def put(self, file, tenant="nubera"):
        document_key = tenant
        self.logger.log(
            "[CouchDBStore] Requests.put on '{0}' with file {1}".format(self.datastore_url + document_key, str(file)))

        result = requests.post(self.datastore_url + document_key, json=file, verify='/certs/ca.crt')
        # self.logger.log("[CouchDBStore] Result of raw text requests.put: " + result.text.rstrip())

        response = self._create_store_response(result.status_code, result.reason, result.json())

        self.logger.log("[CouchDBStore] StoreResponse for put: " + str(response))
        return response

    def delete(self, tenant="nubera", **keys):
        doc_obj = keys.get("file")
        document_key = tenant + "/" + doc_obj['_id'] + "?rev=" + doc_obj['_rev']
        self.logger.log("[CouchDBStore] Requests.delete on '{0}' + '{1}'".format(self.datastore_url, document_key))
        result = requests.delete(self.datastore_url + document_key, verify="/certs/ca.crt")
        # self.logger.log("[CouchDBStore] Result of raw text requests.delete: " + result.text.rstrip())

        response = self._create_store_response(result.status_code, result.reason, result.json())

        self.logger.log("[CouchDBStore] StoreResponse for delete: " + str(response))
        return response

    def get_versions(self, tenant="nubera", **keys):
        self.logger.log("[CouchDBStore] get_versions on '{0}' for keys '{1}'".format(self.datastore_url, keys))

        if "doc_id" in keys:
            doc_id = keys.get("doc_id")
        else:
            initial_store_response = self.get(tenant, **keys)
            initial_doc_obj = initial_store_response.content
            doc_id = initial_doc_obj['_id']

        result_array = []
        document_key = tenant + "/" + doc_id + "?revs=true"
        if keys.get("all", False):
            document_key = document_key + "&open_revs=all"
        self.logger.log("[CouchDBStore] get_versions. document_key: " + str(document_key))
        request_result = requests.get(self.datastore_url + document_key, verify='/certs/ca.crt')
        # self.logger.log("[CouchDBStore] get_versions. Result of raw text requests.get: "+ request_result.text.rstrip())

        doc_obj = request_result.json()
        self.logger.log("[CouchDBStore] get_versions. doc_obj with revisions: " + json.dumps(doc_obj))

        if keys.get("raw", False):
            response = self._create_store_response(request_result.status_code, request_result.reason, doc_obj)
        else:
            revision_amount = doc_obj['_revisions']['start']
            for i in list(reversed(range(int(revision_amount)))):
                rev_index = revision_amount - i - 1
                key = tenant + "/" + doc_id + "?rev=" + str(i + 1) + "-" + doc_obj['_revisions']['ids'][rev_index]
                result = requests.get(self.datastore_url + key, verify="/certs/ca.crt").json()
                if 'reason' in result and (result['reason'] == 'missing') and 'error' in result and (
                        result['error'] == 'not_found'):
                    self.logger.info("[CouchDBStore] get_versions. revision not present anymore... break")
                    break
                result_array.append(result)
            response = self._create_store_response(request_result.status_code, request_result.reason,
                                                   {"result": result_array})
        self.logger.log("[CouchDBStore] StoreResponse for get_versions: " + str(response))
        return response

    def get_version_x(self, tenant="nubera", **keys):
        self.logger.log("[CouchDBStore] get_version_x on '{0}' for keys '{1}'".format(self.datastore_url, keys))

        initial_store_response = self.get_versions(tenant, **keys)
        revisions_obj = initial_store_response.content
        previous_nb = keys["previous_nb"]
        # revisions_number = revisions_obj['_revisions']['start']
        # revision_previous = str(revisions_number - previous_nb) +'-'+ revisions_obj['_revisions']['ids'][previous_nb]
        # revision_previous_url = tenant + keys["document_name"] +'?rev='+ revision_previous     
        document_version_x = revisions_obj["result"][previous_nb - 1]
        # self.logger.log("[CouchDBStore]  get_version_x. document_version_x is '{0}'".format(document_version_x))
        # self.logger.log("[CouchDBStore]  get_version_x. Determined the needed revision_previous_url '{0}'".format(revision_previous_url))
        # result  = requests.get(self.datastore_url + revision_previous_url, verify='/certs/ca.crt').json()
        response = self._create_store_response(initial_store_response.status_code, initial_store_response.reason,
                                               {"result": document_version_x})
        self.logger.log("[CouchDBStore] StoreResponse for get_version_x: " + str(response))

        return response

    def get_categories(self, tenant="nubera"):
        document_key = tenant + "/" + "_design_docs"
        self.logger.log("[CouchDBStore] get_categories. Searching for categories on key: " + document_key)
        try:
            result = requests.get(self.datastore_url + document_key, verify='/certs/ca.crt')
            self.logger.log("[CouchDBStore] get_categories. Result of request: " + result.text.rstrip())
            categories_obj = json.loads(result.text)['rows']
            return_obj = {tenant: []}
            for category in categories_obj:
                return_obj[tenant].append(str(category))
            response = self._create_store_response(result.status_code, result.reason, return_obj)
        except Exception as e:
            self.logger.error(
                "[CouchDBStore] Exception occured in get_categories: " + str(e) + ". Returning empty StoreResponse")
            response = self._create_store_response(400, str(e), {})
        self.logger.log("[CouchDBStore] StoreResponse for get_categories: " + str(response))
        return response

    def get_subcategories_for_category(self, category, tenant="nubera"):
        document_key = tenant + "/" + "_design/" + category
        self.logger.log(
            "[CouchDBStore] get_subcategories_for_category. Searching for subcategories on key: " + document_key)
        try:
            result = requests.get(self.datastore_url + document_key, verify='/certs/ca.crt')
            self.logger.log("[CouchDBStore] get_subcategories_for_category. Result of request: " + result.text.rstrip())
            categories_obj = json.loads(result.text)['views']
            return_obj = {category: []}
            for subcategory in categories_obj:
                return_obj[category].append(str(subcategory))
            response = self._create_store_response(result.status_code, result.reason, return_obj)
        except Exception as e:
            self.logger.error("[CouchDBStore] Exception occured in get_subcategories_for_category: " + str(
                e) + ". Returning empty StoreResponse")
            response = self._create_store_response(400, str(e), {})
        self.logger.log("[CouchDBStore] StoreResponse for get_subcategories_for_category: " + str(response))
        return response

    def _get_datastore_url(self, datastore):
        return self.datastore_url + datastore + "/"

    def _check_datastore_exists(self, datastore):
        response = requests.head(self.datastore_url, verify='/certs/ca.crt')
        if response and response.status_code == 200:
            return True
        return False
