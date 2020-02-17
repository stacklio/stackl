import logging
import time
from random import randint

from algorithms import StrategyFactory

logger = logging.getLogger(__name__)
from manager import Manager


# TODO here we manage items and still need to implement creating an item based on input documents and hierarchical lookup
class ItemManager(Manager):
    def __init__(self, manager_factory):
        super(ItemManager, self).__init__(manager_factory)

        self.document_manager = manager_factory.get_document_manager()

    def get_key_value(self, item, key):
        try:
            logger.debug("[ItemManager] get. For item '{0}' and key '{1}'".format(item, key))
            return item[key]
        except Exception as e:
            logger.error("[ItemManager] get. Exception occurred: {0}. Returning empty object".format(e))
            return {}

    def list_all_item_keys_with_values(self, item, info=False):
        all_items = self.get_all(info)
        if item in all_items:
            return all_items[item]
        else:
            return {}

    def list_all_item_keys(self):
        try:
            return self.get_all().keys()
        except Exception as e:
            logger.error(
                "[ItemManager] Exception occured in list_all_item_keys: " + str(e) + " returning empty item list")
            return list(set())

    def write_item_hierarchy(self, item_hierarchy):
        tries = 10
        while True:
            logger.debug("[ItemManager] write_item_hierarchy. Getting existing hierarchy.")
            conf_obj = self.document_manager.get_document(category='types', subcategory='configuration',
                                                          document_name='hierarchy')
            conf_obj['hierarchy'] = item_hierarchy
            logger.debug("[ItemManager] Trying to write new tree")
            status_code = self.document_manager.write_document(document_name='hierarchy', subcategory="configuration", \
                                                               file=conf_obj, description=conf_obj['description'],
                                                               category='types')
            logger.debug("[ItemManager] Writing status flag status code: " + str(status_code))
            if status_code != 409:
                logger.debug("[ItemManager] New Hierarchy written!")
                break
            elif tries < 0:
                raise Exception("[ItemManager] Rewriting Hierarchy timed out... no more tries left")
            else:
                tries = tries - 1
                logger.debug("[ItemManager] Tries left: " + str(tries))
                time.sleep(randint(0, 5))

    def get_item_hierarchy(self):
        logger.debug("[ItemManager] get_item_hierarchy.")
        config_obj = self.document_manager.get_document(category='types', subcategory='configuration',
                                                        document_name='hierarchy')
        config_hierarchy_obj = config_obj['hierarchy']
        hierarchy = []
        for index in range(len(config_hierarchy_obj)):
            element_special_characters = config_hierarchy_obj[index]
            element_special_characters_first = element_special_characters.replace("%{", '')
            element = element_special_characters_first.replace("}", '')
            splitted = element.split('/')
            if splitted[len(splitted) - 2] != 'item':
                hierarchy.append((splitted[len(splitted) - 2], splitted[len(splitted) - 1]))
        return list(reversed(hierarchy))

    # Filter should be form of {"type:" "common", "name":"common"}
    def get_all(self, info=False, filter_item=None, item_name=None):
        logger.debug(
            "[ItemManager] get_all. For info '{0}', filter_item '{1}' and item_name '{2}'".format(info, filter_item,
                                                                                                  item_name))
        # get all items #TODO Distinction item/database/...
        all_items = self.document_manager.get_document(category='types', subcategory='item', document_name=item_name)
        if all_items is None:
            return {item_name: {}}  # TODO Added this here. Unsure if it is supposed to ever be null
        if all_items and type(all_items) != list:
            all_items = [all_items]
        hierarchy = self.get_item_hierarchy()
        logger.debug("[ItemManager] get_all. Hierarchy '{0}'".format(hierarchy))
        # got hierarchy
        push = True
        merge = True
        document_cache = {}
        return_doc = {}
        for item in all_items:
            merged_doc = {}
            item_name = item['name']
            for element in hierarchy:
                # find document type and document name
                if element[0] == 'common':
                    doc_name = element[1]
                else:
                    doc_name = item.get(element[1], None)
                    if doc_name == None:
                        merge = False
                        merged_doc = self._create_hiera_error_object(item_name, str(element[1]) + " not found in item")
                        break
                # check if document was already called before. if not, call
                if element[0] in document_cache and doc_name in document_cache[element[0]]:
                    doc_obj = document_cache[element[0]][doc_name]
                else:
                    try:
                        doc_obj = self.hiera_document_inheritance("types", element[0], doc_name, document_cache)
                    except Exception as e:
                        merge = False
                        merged_doc = self._create_hiera_error_object(item_name, e)
                        break
                if filter_item:
                    if filter_item['type'] == element[0] and filter_item['name'] != doc_name:
                        push = False
                if doc_obj == None:
                    # Do not call exception but exclude element from list and continue
                    logger.error(
                        "[ItemManager] get_all. Error!!! document {0} not found for role {1}! Ignoring and excluding from Hiera call!".format(
                            str(doc_name), element[0]))
                    merge = False
                    merged_doc = self._create_hiera_error_object(item_name,
                                                                 'Document ' + str(doc_name) + ' not found for role ' +
                                                                 element[0])
                    break
                if info:
                    doc_obj = self._add_hiera_info(doc_obj)
                merged_doc.update(doc_obj)
            if push:
                if info:
                    item = self._add_hiera_info(item)
                if merge:
                    merged_doc.update(item)
                return_doc[item_name] = merged_doc
            merge = True
            push = True
        return return_doc

    # TODO Legacy code underneath - needs to be updated
    def _add_hiera_info(self, doc_obj):
        info_obj = {}
        for key in doc_obj:
            info_obj[key] = {'value': doc_obj[key], 'source_name': doc_obj['name'], 'source_type': doc_obj['type']}
        return info_obj

    def hiera_document_inheritance(self, viewCategory, viewName, documentKey, document_cache):
        returnObj = {}
        self.hiera_document_inheritance_helper(viewCategory, viewName, documentKey, returnObj, document_cache)
        document_cache[viewName] = {}
        document_cache[viewName][documentKey] = returnObj
        return returnObj

    def hiera_document_inheritance_helper(self, viewCategory, viewName, documentKey, recurseObject, document_cache):
        if viewName in document_cache and documentKey in document_cache[viewName]:
            # logger.debug("if document_cache check: "+ str(element))
            documentObj = document_cache[viewName][documentKey]
        else:
            documentObj = self.document_manager.get_document(category=viewCategory, subcategory=viewName,
                                                             document_name=documentKey)
            if viewName not in document_cache:
                document_cache[viewName] = {}
            document_cache[viewName][documentKey] = documentObj
        if documentObj:
            if 'inherits' in documentObj:
                self.hiera_document_inheritance_helper(viewCategory, viewName, documentObj['inherits'], recurseObject,
                                                       document_cache)
            strategy = StrategyFactory.create_merge_strategy(documentObj)
            recurseObject = strategy.merge(recurseObject, documentObj)
        else:
            raise Exception('Document ' + str(documentKey) + ' for type ' + str(viewName) + ' not found')

    def _create_hiera_error_object(self, resource_object_obj_name, error):
        return {
            "name": resource_object_obj_name,
            'error': str(error)
        }
