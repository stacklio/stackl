import json
import sys
import threading

sys.path.append("/etc/stackl_src/")
from handler import Handler
from logger import Logger


class ItemHandler(Handler):
    def __init__(self, manager_factory):
        super(ItemHandler, self).__init__(manager_factory)
        self.logger = Logger("ItemHandler")

        self.document_manager = manager_factory.get_document_manager()
        self.stack_manager = manager_factory.get_stack_manager()
        self.item_manager = manager_factory.get_item_manager()

    def process(self, item):
        self.logger.log("[ItemHandler] process. Item to process: {0}".format(str(item)))
        item = item["doc"]["name"]
        action = item["action"]
        automation_invocation_enabled = self.get_automation_invocation_enabled(item)
        stack_instances = None
        if "stack_instance" in item["doc"]:
            stack_instances = item["doc"]["stack_instance"]
        # check if updating is needed
        if action == "update":
            update_dict = item["updates"].copy()
            del update_dict["_rev"]
            if "state" in update_dict:
                del update_dict["state"]
            # if dict length of update is zero, no additional changes are needed to just put it to done
            if len(update_dict) == 0 and stack_instances:
                self.logger.log(
                    "[ItemHandler] Only STATE or REV were updated, IGNORING UPDATE change!"
                )
                self.flag_item_request_state_stack_instance(
                    item, stack_instances, "done"
                )
                return
            else:
                self.logger.log(
                    "[ItemHandler] Other updates were performed..... UPDATING!"
                )
        # check if invocation is required...
        if automation_invocation_enabled:
            if stack_instances:
                self.logger.log(
                    "[ItemHandler] State should change to 'create' for: " + item
                )
                self.flag_item_request_state_stack_instance(
                    item, stack_instances, action
                )
            # multiple processors (ansible, python,... are needed)
            self.invoke_websocket(item)
        else:
            # no invocation -> put straight to done state
            self.logger.log(
                "[ItemHandler] Setting state to done since invocation was false for: " + item)
            self.flag_item_request_state_stack_instance(item, stack_instances, "done")
        if action == "delete":
            if automation_invocation_enabled == False:
                self.logger.log(
                    "[ItemHandler] Removing items directly because invocation was false"
                )
                self.delete_item_stack_instance(item, stack_instances)

    def handle(self, item):
        self.logger.log("[ItemHandler] handle. Item to handle: {0}".format(str(item)))
        try:
            action = item["action"]
            self.logger.log(
                "[ItemHandler] The change action for the item was '{0}'".format(action)
            )
            if action == "create" or action == "update":
                if action == "update" and "deleting" in item["doc"]:
                    self.logger.log(
                        "[ItemHandler] Received update statement but contained deleting... Part of deletion assignment? Dropping...."
                    )
                else:
                    thread = threading.Thread(target=self.process, args=[item])
                    thread.run()
            elif action == "delete":
                if "item_deletion" in item:
                    self.logger.log(
                        "[ItemHandler] Received item deletion via stack handler... processing...."
                    )
                    thread = threading.Thread(target=self.process, args=[item])
                    thread.run()
                else:
                    self.logger.log(
                        "[ItemHandler] Received DOCUMENT item deletion... dropping...."
                    )
            elif action == "waiting" or action == "failed":
                stack_instances = None
                if "stack_instance" in item["doc"]:
                    stack_instances = item["doc"]["stack_instance"]
                    self.flag_item_request_state_stack_instance(item["doc"]["name"], stack_instances, action)
            elif action == "report":
                message = "Report received in ItemHandler: {0}".format(
                    str(json.dumps(item))
                )
                self.logger.info(message)
                # check automation_run present
                automation_run = item.get("automation_run", None)
                if automation_run:
                    try:
                        automation_run_obj = {
                            "type": "automation-run",
                            "name": item["item"],
                            "automation_run": automation_run,
                        }
                        self.logger.info(
                            "[ItemHandler] Posting automation_run document"
                        )
                        self.document_manager.write_document(
                            document_name=item["item"],
                            subcategory="automation-run",
                            file=automation_run_obj,
                            description="",
                            category="types",
                        )
                    except Exception as e:
                        self.logger.error(
                            "[ItemHandler] Error automation_run document: " + str(e)
                        )
                if item["request"]["action"] == "delete":
                    self.delete_item_stack_instance(
                        item["item"], item["request"]["all_variables"]["stack_instance"]
                    )
                else:
                    self.flag_item_request_state_stack_instance(
                        item["item"],
                        item["request"]["item_doc"]["stackInstance"],
                        item["result"],
                    )
        except Exception as e:
            self.logger.error(
                "[ItemHandler] !!!ERROR ERROR!!! in handle: "
                + str(e)
                + " for obj: "
                + str(item)
            )

    def load_item_variables_delete(self, item):
        self.logger.log("[ItemHandler] load_item_variables_delete. For item: {0}".format(str(item)))

        hierarchy = self.item_manager.get_item_hierarchy()
        merged_doc = {}
        for element in hierarchy:
            self.logger.log("[ItemHandler] element: " + str(element))
            if element[0] == "common":
                doc_name = element[1]
            else:
                doc_name = item[element[1]]
            doc_obj = self.document_manager.get_document(type=element[0], document_name=doc_name)
            if doc_obj == None:
                self.logger.info(
                    "[ItemHandler] document "
                    + str(doc_name)
                    + " not found for role "
                    + element[0]
                )
            else:
                merged_doc.update(doc_obj)
        merged_doc.update(item)
        return merged_doc

    def delete_item_stack_instance(self, item, stack_instances_names):
        self.logger.log("[ItemHandler] delete_item_stack_instance. deleting " + item)
        self.document_manager.remove_document(
            document_name=item, subcategory="item"
        )
        self.logger.log("[ItemHandler] stack_instances " + str(stack_instances_names))
        # loop over stack instances listed in the item
        if stack_instances_names is not None:
            self.logger.log(
                "[ItemHandler] stack_instances is not None... Looping over them"
            )
            for stack_instance_name in stack_instances_names:
                self.logger.log(
                    "[ItemHandler] Current stack instance " + stack_instance_name
                )
                # lookup the stack instance document
                stack_instance_obj = self.document_manager.get_document(
                    category="stacks",
                    subcategory="instances",
                    document_name=stack_instance_name,
                )
                # loop over the item
                if stack_instance_obj is not None:
                    if stack_instance_obj["deleting"]:
                        self.logger.log(
                            "[ItemHandler] Not deleting item from stackinstance since the stackinstance is being removed"
                        )
                        self.flag_item_request_state_stack_instance(
                            item, [stack_instance_name], "deleted"
                        )
                        self.stack_manager.process_stack_instance_delete_item(
                            item, stack_instance_name
                        )
                        continue
                    to_delete_service = None
                    for service_name in stack_instance_obj["services"]:
                        if item == service_name:
                            to_delete_service = service_name
                    if to_delete_service:
                        del stack_instance_obj['services'][to_delete_service][item]
                        self.document_manager.write_document(document_name=stack_instance_name, type="stack_instance",
                                                             file=stack_instance_obj,
                                                             description='Stack instance ' + stack_instance_name)
                else:
                    self.logger.log(
                        "[ItemHandler] stack_instance_obj "
                        + stack_instance_name
                        + " was None for item "
                        + item
                    )

    def invoke_websocket(self, item):
        self.logger.log(
            "[ItemHandler] invoke_websocket. Item: {0}".format(item)
        )
        action = item["action"]
        item = item["doc"]["name"]
        extra_vars = {}
        if "parameters" in item:
            extra_vars = item["parameters"]
        if action == "delete":
            extra_vars["all_variables"] = self.load_item_variables_delete(item["doc"])
        else:
            extra_vars["item_doc"] = item["doc"]
        extra_vars["type"] = item["type"]
        extra_vars["action"] = action
        extra_vars["playbook"] = item["doc"]["role"] + ".yaml"
        extra_vars["item"] = item
        extra_vars["automation_handler"] = self.item_manager.get(item, "automation_handler")
        extra_vars["host"] = self.item_manager.get(item, "stacklAnsibleFqdn")
        extra_vars["port"] = self.item_manager.get(item, "ansible_port")
        extra_vars["user"] = self.item_manager.get(item, "ansible_user")
        extra_vars["dynamic_inventory_path"] = self.item_manager.get(item, "ansible_dynamic_inventory_path")
        extra_vars["playbook_path"] = self.item_manager.get(item, "ansible_playbook_path")
        self.logger.log("[ItemHandler] invoke_websocket. extra_vars for websocket: {0}".format(extra_vars))
        # self.logger.log("[ItemHandler] change_obj[websocket]: "+ str(change_obj['websocket']))
        # change_obj['websocket'].write_message(extra_vars)

    def flag_item_request_state_stack_instance(self, item, stack_instances_names, action):
        self.flag_item_request_state(item, stack_instances_names, action)

    def flag_item_request_state(self, item_to_be_flagged, parent_item_names, action, parent_item_view_category="types",
                                parent_item_view_type="stack_instance"):
        self.logger.log(
            "[ItemHandler] flag_item_request_state. Flagging state of '{0}' to state '{1}'".format(item_to_be_flagged,
                                                                                                   action
                                                                                                   )
        )
        # loop over stack instances listed in the resource_object
        if parent_item_names is None:
            self.logger.log("[ItemHandler] No parent_item_names. Returning.")
            return
        else:
            self.logger.log("[ItemHandler] parent_item_names '{}'. Starting loop.".format(parent_item_names))
        for parent_item_name in parent_item_names:
            self.logger.log("[ItemHandler] Current parent resource to modify '{}'".format(parent_item_name))
            self.logger.log("[ItemHandler] Trying to modify.... " + parent_item_name)
            tries = 100
            stop = False
            while stop == False and tries > 0:
                self.logger.log(
                    "[ItemHandler] stop '{0}' tries '{1}'".format(stop, tries)
                )
                self.logger.info("[ItemHandler] Lookup the stack instance document")
                item = self.document_manager.get_document(
                    category=parent_item_view_category,
                    subcategory=parent_item_view_type,
                    document_name=parent_item_name,
                )
                # loop over the resources
                self.logger.log("[ItemHandler] Item: " + str(item))
                # Deprecated. See old code and redo if still needed
                # if item is not None:
                #     item_found = False
                #     for service in item["services"]:
                #         self.logger.log("[ItemHandler] Checking if service '{0}' is item_to_be_flagged '{1}'".format(service, item_to_be_flagged))
                #         if item_to_be_flagged == service:
                #             item_found = True
                #             #DEPRECATE
                #     #         self.logger.log("[ItemHandler] Adding state '{0}' to resource entry '{1}' for instance '{2}'".format(
                #     #             action, item_to_be_flagged, parent_resource_name))
                #     #         service['resources'][service] = {"state": action}
                #     #         status_code = self.document_manager.write_document(tenant, document_name = parent_resource_name, category = parent_resource_view_category,
                #     #                                                 subcategory = resource_obj['type'], file = resource_obj, description = parent_resource_name,)
                #     #         self.logger.log("[ItemHandler] Writing status flag status code: '{}'".format(status_code))
                #     #         if tries <= 0 or status_code != 409:
                #     #             self.logger.log("[ItemHandler] Stopping. Tries <= 0 or status_code not 409")
                #     #             stop = True
                #     #         else:
                #     #             tries = tries - 1
                #     #             self.logger.log("[ItemHandler] Tries left: "+ str(tries))
                #     #             time.sleep(randint(0,5))
                #     # if item_found == False:
                #     #     self.logger.log("[ItemHandler] Stop try to flag action '{0}' for resource '{1}'. Not found in resource list '{2}'".format(
                #     #                         action, resource_to_be_flagged, parent_resource_view_type))
                #     #     stop = True
                #     # item_found = False
                # else:
                #     #tries = tries - 1
                #     self.logger.log("[ItemHandler] item not found. Breaking loop and continuing with other instances...")
                #     time.sleep(2)
                #     break

    def get_automation_invocation_enabled(self, item_name):
        self.logger.info("[ItemHandler] get_automation_invocation_enabled. Item_name '{0}'".format(str(item_name)))
        automation_invocation_enabled = self.item_manager.get(item_name, "automation_invocation_enabled")
        if automation_invocation_enabled == {}:
            self.logger.info(
                "[ItemHandler] Empty object returned.... returning automation_invocation_enabled True"
            )
            return True
        elif isinstance(automation_invocation_enabled, bool):
            self.logger.info("[ItemHandler] automation_invocation_enabled was bool... returning "
                             + str(automation_invocation_enabled)
                             )
            return automation_invocation_enabled
        elif str(automation_invocation_enabled).lower() == "true":
            self.logger.info("[ItemHandler] Automation_invocation_enabled was 'True'... returning True'")
            return True
        elif str(automation_invocation_enabled).lower() == "false":
            self.logger.info("[ItemHandler] Automation_invocation_enabled was 'False'... returning False'")
            return False
        else:
            self.logger.info("[ItemHandler] Default case... automation_invocation_enabled returning True")
            return True
