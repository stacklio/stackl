import logging

from agent_broker.agent_broker_factory import AgentBrokerFactory
from enums.cast_type import CastType
from enums.stackl_codes import StatusCode
from handler.stack_handler import StackHandler

logger = logging.getLogger(__name__)
from manager import Manager
from task.result_task import ResultTask
from task_broker.task_broker_factory import TaskBrokerFactory


class StackManager(Manager):

    def __init__(self, manager_factory):
        super(StackManager, self).__init__(manager_factory)

        self.document_manager = manager_factory.get_document_manager()

        self.agent_broker_factory = AgentBrokerFactory()
        self.agent_broker = self.agent_broker_factory.get_agent_broker()

        self.task_broker_factory = TaskBrokerFactory()
        self.task_broker = self.task_broker_factory.get_task_broker()

    def handle_task(self, task):
        logger.debug("[StackManager] handling subtasks in task {0}".format(task))
        try:
            stack_instance = None
            for subtask in task["subtasks"]:
                logger.debug("[StackManager] handling subtask '{0}'".format(subtask))
                if subtask == "CREATE":
                    (stack_instance, status_code) = self.process_stack_request(task["json_data"], "create")
                    change_obj = self.agent_broker.create_change_obj(stack_instance, "create", self.document_manager)
                    self.document_manager.write_stack_instance(stack_instance)
                elif subtask == "UPDATE":
                    (stack_instance, status_code) = self.process_stack_request(task["json_data"], "update")
                    change_obj = self.agent_broker.create_change_obj(stack_instance, "update", self.document_manager)
                    self.document_manager.write_stack_instance(stack_instance)
                elif subtask == "DELETE":
                    (stack_instance, status_code) = self.process_stack_request(task["json_data"], "delete")
                    change_obj = self.agent_broker.create_change_obj(stack_instance, "delete", self.document_manager)
                    stack_instance.deleted = True
                    self.document_manager.write_stack_instance(stack_instance)
                else:
                    status_code = StatusCode.BAD_REQUEST
                if status_code in [StatusCode.OK, StatusCode.CREATED, StatusCode.ACCEPTED]:
                    agent_connect_info = task["send_channel"]
                    logger.debug(
                        "[StackManager] Processing subtask succeeded. Sending to agent with connect_info '{0}' the stack_instance '{1}'".format(
                            agent_connect_info, change_obj))
                    result = self.agent_broker.send_to_agent(agent_connect_info, change_obj)
                    self.agent_broker.process_result(stack_instance, result, self.document_manager)
                    logger.debug("[StackManager] Sent to agent. Result '{0}'".format(result))
                else:
                    raise Exception("[StackManager] Processing subtask failed. Status_code '{0}'".format(status_code))

            logger.debug("[StackManager] Succesfully handled task_attr. Notifying task broker.")
            self.task_broker.give_task(ResultTask({
                'channel': task.get('return_channel'),
                'cast_type': CastType.BROADCAST.value,
                'result': "success",
                'source_task': task
            }))  # this way the broker is notified of the result and whether he should remove the task from the task queue
        except Exception as e:
            logger.error("[StackManager] Error with processing task. Error: '{0}'".format(e))

    def process_stack_request(self, instance_data, stack_action):
        # create new object with the action and document in it
        logger.debug("[StackManager] converting instance data to change wrapper object")
        change_obj = {}
        change_obj['action'] = stack_action
        change_obj['document'] = instance_data
        change_obj['type'] = 'stack_instance'
        handler = StackHandler(self.manager_factory)
        merged_sat_sit_obj, status_code = handler.handle(change_obj)
        logger.debug("[StackManager] Handle complete. status_code '{0}'. merged_sat_sit_obj '{1}' ".format(status_code,
                                                                                                           merged_sat_sit_obj))
        return (merged_sat_sit_obj, status_code)

    def get_stack_object_state(self, category, subcategory, stack_object_id,
                               state_type='short'):  # TODO Kept but not updated since we will need to have some introspection capability later on
        stack_instance_obj = self.document_manager.get_document(category=category, subcategory=subcategory,
                                                                document_name=stack_object_id)
        if not stack_instance_obj:
            return "[StackManager] Stack instance '{0}' not found.".format(stack_object_id)
        resources = stack_instance_obj['resources']
        # return all resources
        if state_type == 'long':
            stack_instance_obj = self.document_manager.get_document(category='stacks', subcategory='instances',
                                                                    document_name=stack_object_id)
            return resources
        else:
            state_list = []
            state = 'Done'
            for resource in resources:
                for resource_element in resources[resource]:
                    if resources[resource][resource_element]['state'] != 'done' and \
                            resources[resource][resource_element]['state'] != 'failed' and \
                            resources[resource][resource_element]['state'] != 'interrupted':
                        return 'In progress'
                    state_list.append(resources[resource][resource_element]['state'])
            if 'failed' in state_list or 'interrupted' in state_list:
                return 'Failed'
            return state

    def get_stack_instance_resource_state(self, stack_instance_id,
                                          resource_name):  # TODO Kept but not updated since we will need to have some introspection capability later on
        stack_instance_obj = self.document_manager.get_document(category='stacks', subcategory='instances',
                                                                document_name=stack_instance_id)
        if not stack_instance_obj:
            return 'Does not exist'
        resources = stack_instance_obj['resources']
        state = 'unknown'
        for resource in resources:
            for resource_element in resources[resource]:
                if resource_element == resource_name:
                    return resources[resource][resource_element]['state']
        return state
