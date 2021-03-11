"""
Module containing all logic for creating and updating Stack instances
"""

from collections import OrderedDict

from loguru import logger

from core.enums.stackl_codes import StatusCode
from core.models.configs.stack_infrastructure_template_model import \
    StackInfrastructureTemplate
from core.models.items.stack_infrastructure_target_model import \
    StackInfrastructureTarget
from core.models.items.stack_instance_model import StackInstance
from core.models.items.stack_instance_service_model import StackInstanceService
from core.models.items.stack_instance_status_model import StackInstanceStatus
from core.models.api.stack_instance import StackInstanceUpdate
from core.utils.general_utils import get_timestamp, tree

from ..opa_broker.opa_broker import convert_sit_to_opa_data
from .handler import Handler


def process_service_targets(attributes,
                            new_result,
                            service_targets,
                            opa_service_params,
                            outputs=None):
    """
    This function makes sure only targets chosen by the policies will be
    considered when creating a stack instance
    """
    service = attributes['service']
    st = service_targets[service]
    new_targets = []
    for t in st['targets']:
        if outputs is not None:
            for tt in new_result['targets']:
                if tt['target'] == t:
                    new_targets.append(t)
                for output in outputs:
                    opa_service_params[service][
                        tt['target']][output] = tt[output]
        elif t in new_result['targets']:
            new_targets.append(t)
    service_targets[service]['targets'] = new_targets


def delete_services(to_be_deleted, stack_instance):
    for service in to_be_deleted:
        for key, _ in service.items():
            del stack_instance.services[key]


class StackHandler(Handler):
    """Handler responsible for all actions on Stack Instances"""
    def __init__(self, document_manager, opa_broker):
        super().__init__()
        self.document_manager = document_manager
        self.opa_broker = opa_broker
        self.opa_broker.document_manager = self.document_manager

    def handle(self, item):
        """
        Handle logic of the action
        """
        action = item['action']
        if action == 'create':
            logger.debug("[StackHandler] handle. Received create task")
            return self._handle_create(item['document'])
        if action == 'update':
            logger.debug("[StackHandler] handle. Received update task")
            return self._handle_update(item['document'])
        if action == 'delete':
            logger.debug("[StackHandler] handle. Received delete task")
            return self._handle_delete(item['document'])
        return StatusCode.BAD_REQUEST

    def _create_stack_instance(
            self, item, opa_decision,
            stack_infrastructure_template: StackInfrastructureTemplate,
            opa_service_params):
        """
        function for creating the stack instance object
        """
        stack_instance_doc = StackInstance(
            name=item.stack_instance_name,
            stack_infrastructure_template=item.stack_infrastructure_template,
            stack_application_template=item.stack_application_template)
        stack_instance_doc.instance_params = item.params
        stack_instance_doc.service_params = item.service_params
        stack_instance_doc.instance_secrets = item.secrets
        stack_instance_doc.service_secrets = item.service_secrets
        services = OrderedDict()
        stack_instance_statuses = []
        for svc, opa_result in opa_decision.items():
            # if a svc doesnt have a result raise an error cause we cant resolve it
            svc_doc = self.document_manager.get_service(opa_result['service'])
            service_definitions = []
            for infra_target in opa_result['targets']:
                infra_target_counter = 1
                service_definition = self.add_service_definition(
                    infra_target, infra_target_counter, item,
                    opa_service_params, stack_infrastructure_template,
                    stack_instance_statuses, svc, svc_doc)
                service_definitions.append(service_definition)
                infra_target_counter += 1
            services[svc] = service_definitions
        stack_instance_doc.services = services
        stack_instance_doc.status = stack_instance_statuses
        return stack_instance_doc

    def add_service_definition(self, infra_target, infra_target_counter, item,
                               opa_service_params,
                               stack_infrastructure_template,
                               stack_instance_statuses, svc, svc_doc):
        """
        Function for adding a service_definition item to a stack_instance
        """
        service_definition = StackInstanceService()
        service_definition.service = svc_doc.name
        service_definition.infrastructure_target = infra_target
        service_definition.opa_outputs = opa_service_params[svc][infra_target]
        capabilities_of_target = stack_infrastructure_template.infrastructure_capabilities[
            infra_target].provisioning_parameters
        secrets_of_target = stack_infrastructure_template.infrastructure_capabilities[
            infra_target].secrets
        agent = stack_infrastructure_template.infrastructure_capabilities[
            infra_target].agent
        cloud_provider = stack_infrastructure_template.infrastructure_capabilities[
            infra_target].cloud_provider
        merged_secrets = {**secrets_of_target, **svc_doc.secrets}
        fr_params = {}
        for fr in svc_doc.functional_requirements:
            fr_doc = self.document_manager.get_functional_requirement(fr)
            fr_params = {**fr_params, **fr_doc.params}
            merged_secrets = {**merged_secrets, **fr_doc.secrets}
            if fr_doc.as_group:
                # First check if the status is already available in the stack instance statuses
                status_already_available = False
                for stack_instance_status in stack_instance_statuses:
                    if stack_instance_status.service == svc and \
                        stack_instance_status.functional_requirement == fr:
                        status_already_available = True
                        # status found, add the infra target
                        stack_instance_status.infrastructure_target += f",{infra_target}"
                        break
                if not status_already_available:
                    stack_instance_status = StackInstanceStatus(
                        functional_requirement=fr,
                        service=svc,
                        infrastructure_target=infra_target,
                        status="in_progress",
                        error_message="")
                    stack_instance_statuses.append(stack_instance_status)
            else:
                stack_instance_status = StackInstanceStatus(
                    functional_requirement=fr,
                    service=svc,
                    infrastructure_target=infra_target,
                    status="in_progress",
                    error_message="")
                stack_instance_statuses.append(stack_instance_status)
        merged_capabilities = {
            **capabilities_of_target,
            **fr_params,
            **svc_doc.params
        }
        service_definition.provisioning_parameters = {
            **merged_capabilities,
            **service_definition.opa_outputs,
            **item.params,
            **item.service_params.get(svc, {})
        }
        if "stackl_hostname" in service_definition.provisioning_parameters:
            service_definition.template_hosts(
                service_definition.provisioning_parameters["stackl_hostname"],
                service_definition.provisioning_parameters.get(
                    "instances", None), infra_target_counter)

        service_definition.secrets = {
            **merged_secrets,
            **item.secrets,
            **item.service_secrets.get(svc, {})
        }
        service_definition.agent = agent
        service_definition.cloud_provider = cloud_provider
        return service_definition

    def _service_in_doc(self, service_name, item):
        for service in item.services:
            if service_name == service.name:
                return True
        return False

    def check_difference(self, item):
        # Delete old services not in stack_instance anymore
        stack_instance = self.document_manager.get_stack_instance(
            item.stack_instance_name)
        to_be_deleted = []
        sat = self.document_manager.get_stack_application_template(
            stack_instance.stack_application_template)
        for service_name, service in stack_instance.services.items():
            if not self._service_in_doc(service_name,
                                        item) and not self._service_in_doc(
                                            service_name, sat):
                # Delete service
                to_be_deleted.append({service_name: service})
        logger.info(f"Services to be deleted: {to_be_deleted}")
        return to_be_deleted

    def _update_stack_instance(self, stack_instance: StackInstance,
                               item: StackInstanceUpdate, opa_service_params,
                               service_targets):
        """
        This method takes a stack instance and an item
        which contains the extra parameters and secrets
        """
        stack_infr_template = self.document_manager.get_stack_infrastructure_template(
            stack_instance.stack_infrastructure_template)
        stack_infrastructure_template = self._update_infr_capabilities(
            stack_infr_template, "yes")
        stack_instance.instance_params = {
            **stack_instance.instance_params,
            **item.params
        }
        stack_instance.instance_secrets = {
            **stack_instance.instance_secrets,
            **item.secrets
        }
        stack_instance.service_params = {
            **stack_instance.service_params,
            **item.service_params
        }
        stack_instance.service_secrets = {
            **stack_instance.service_secrets,
            **item.service_secrets
        }

        if "stackl_groups" in item.params:
            stack_instance.groups = item.params["stackl_groups"]

        stack_instance_statuses = []
        new_service_definitions = {}
        # Create copy because we are looping over it and changing things
        stack_instances_services_copy = stack_instance.services.copy()
        for svc, service_definitions in stack_instances_services_copy.items():
            for count, service_definition in enumerate(service_definitions):
                svc_doc = self.document_manager.get_service(
                    service_definition.service)
                if svc in service_targets and not service_definition.infrastructure_target in \
                                           service_targets[svc]['targets']:
                    return "Update impossible. Target in service definition not in service_targets"
                service_definition = self.update_service_definition(
                    count, item, opa_service_params, service_definition,
                    stack_infrastructure_template, stack_instance,
                    stack_instance_statuses, svc, svc_doc)

                stack_instance.services[svc][count] = service_definition

            # Check if replica count increased
            if svc in item.replicas and item.replicas[svc] > len(
                    service_definitions):
                start_index = len(service_targets[svc]["targets"]) \
                                - len(service_definitions)
                if start_index < 1:
                    return f"Can't add more replicas cause there are not enough extra targets for {svc}"
                # Get the service doc, but I really dont like this way:
                svc_doc = self.document_manager.get_service(
                    service_definitions[0].service)
                for i in range(start_index,
                               len(service_targets[svc]["targets"])):
                    service_definition = self.add_service_definition(
                        service_targets[svc]["targets"][i], i + 1, item,
                        opa_service_params, stack_infrastructure_template,
                        stack_instance_statuses, svc, svc_doc)
                    if not svc in new_service_definitions:
                        new_service_definitions[svc] = []
                    new_service_definitions[svc].append(service_definition)

        for service in item.services:
            if service.name not in stack_instance.services:
                svc_doc = self.document_manager.get_service(service.service)
                service_definition = self.add_service_definition(
                    service_targets[service.name]["targets"][0], 0, item,
                    opa_service_params, stack_infrastructure_template,
                    stack_instance_statuses, service.name, svc_doc)
                new_service_definitions[service.name] = [service_definition]

        stack_instance.services = {
            **stack_instance.services,
            **new_service_definitions
        }

        stack_instance.status = stack_instance_statuses
        return stack_instance

    def update_service_definition(self, count, item, opa_service_params,
                                  service_definition,
                                  stack_infrastructure_template,
                                  stack_instance, stack_instance_statuses, svc,
                                  svc_doc):
        """Updates a service definition object within a stack instance"""
        capabilities_of_target = stack_infrastructure_template.infrastructure_capabilities[
            service_definition.infrastructure_target].provisioning_parameters
        secrets_of_target = stack_infrastructure_template.infrastructure_capabilities[
            service_definition.infrastructure_target].secrets
        service_definition.opa_outputs = opa_service_params[svc][
            service_definition.infrastructure_target]
        opa_outputs = service_definition.opa_outputs
        agent = stack_infrastructure_template.infrastructure_capabilities[
            service_definition.infrastructure_target].agent
        merged_secrets = {**secrets_of_target, **svc_doc.secrets}
        fr_params = {}
        for fr in svc_doc.functional_requirements:
            if not item.disable_invocation:
                stack_instance_status = StackInstanceStatus(
                    functional_requirement=fr,
                    service=svc,
                    infrastructure_target=service_definition.
                    infrastructure_target,
                    status="in_progress",
                    error_message="")
                stack_instance_statuses.append(stack_instance_status)
            fr_doc = self.document_manager.get_functional_requirement(fr)
            fr_params = {**fr_params, **fr_doc.params}
            merged_secrets = {**merged_secrets, **fr_doc.secrets}
        merged_capabilities = {
            **capabilities_of_target,
            **fr_params,
            **svc_doc.params
        }
        service_definition.provisioning_parameters = {
            **merged_capabilities,
            **opa_outputs,
            **stack_instance.instance_params,
            **stack_instance.service_params.get(svc, {})
        }
        service_definition.secrets = {
            **merged_secrets,
            **stack_instance.instance_secrets,
            **stack_instance.service_secrets.get(svc, {})
        }
        service_definition.agent = agent
        if "stackl_hostname" in service_definition.provisioning_parameters:
            service_definition.template_hosts(
                service_definition.provisioning_parameters["stackl_hostname"],
                service_definition.provisioning_parameters.get(
                    "instances", None), count + 1)
        return service_definition

    def add_outputs(self, outputs_update):
        """
        Adds outputs on the right service definition of a stack instance
        """
        logger.debug("Adding outputs to stack_instance")
        stack_instance = self.document_manager.get_stack_instance(
            outputs_update.stack_instance)
        service = stack_instance.services[outputs_update.service]
        for service_definition in service:
            if service_definition.infrastructure_target == outputs_update.infrastructure_target:
                service_definition.outputs = {
                    **service_definition.outputs,
                    **outputs_update.outputs
                }
                service_definition.provisioning_parameters = {
                    **service_definition.provisioning_parameters,
                    **service_definition.outputs
                }
                if "stackl_hostname" in service_definition.outputs:
                    service_definition.hostname = service_definition.outputs[
                        "stackl_hostname"]

        return stack_instance

    def _handle_create(self, item):
        """
        Handles the create action of a stack instance
        """
        logger.debug(
            "[StackHandler] _handle_create received with item: {0}".format(
                item))
        stack_infr_template = self.document_manager.get_stack_infrastructure_template(
            item.stack_infrastructure_template)
        stack_app_template = self.document_manager.get_stack_application_template(
            item.stack_application_template)

        stack_infr = self._update_infr_capabilities(stack_infr_template, "yes")

        # Transform to OPA format
        opa_data = self.transform_opa_data(item, stack_app_template,
                                           stack_infr, item.services)

        # Evaluate orchestration policy
        opa_solution = self.evaluate_orchestration_policy(opa_data)

        if not opa_solution['fulfilled']:
            logger.error(
                f"[StackHandler]: Opa result message: {opa_solution['msg']}")
            return None, opa_solution['msg']

        service_targets = opa_solution['services']

        opa_service_params = tree()
        # Verify the SAT policies
        if stack_app_template.policies:
            for policy_name, attributes in stack_app_template.policies.items():
                policy = self.document_manager.get_policy_template(policy_name)
                for policy_params in attributes:
                    new_result = self.evaluate_sat_policy(
                        policy_params, opa_data, policy, item.params,
                        item.replicas)

                    if not new_result['fulfilled']:
                        logger.error(
                            f"[StackHandler]: Opa result message: {new_result['msg']}"
                        )
                        return None, new_result['msg']

                    process_service_targets(policy_params,
                                            new_result,
                                            service_targets,
                                            opa_service_params,
                                            outputs=policy.outputs)

        service_targets = self.evaluate_replica_policy(item, service_targets)

        if not service_targets['result']['fulfilled']:
            logger.error(
                f"replica_policy not satisfied: {service_targets['result']['msg']}"
            )
            return None, service_targets['result']['msg']

        # Verify that each of the SIT policies doesn't violate

        infringment_messages = self.evaluate_sit_policies(
            opa_data, service_targets, stack_infr, item.params)

        if infringment_messages:
            logger.error(f"sit policies not satisfied {infringment_messages}")
            message = "\n".join([x['msg'] for x in infringment_messages])
            return None, message

        return self._create_stack_instance(
            item, service_targets['result']['services'], stack_infr,
            opa_service_params), service_targets['result']['services']

    def evaluate_sit_policies(self, opa_data, service_targets, stack_infr,
                              item_params):
        """
        Evaluates the SIT policies using the OPA broker
        """
        infringment_messages = []
        for _, service_definition in service_targets['result'][
                'services'].items():
            for t in service_definition['targets']:
                policies = stack_infr.infrastructure_capabilities[t].policies

                for policy_name, policy_attributes in policies.items():
                    policy = self.document_manager.get_policy_template(
                        policy_name)

                    # Make sure the policy is in OPA
                    if policy.policy:
                        self.opa_broker.add_policy(policy.name, policy.policy)

                    policy_input = {
                        "parameters": policy_attributes,
                        "stack_instance_params": item_params,
                        "target": t
                    }

                    opa_data_with_inputs = {**opa_data, **policy_input}
                    # evaluate
                    opa_result = self.opa_broker.ask_opa_policy_decision(
                        policy.name, "infringement", opa_data_with_inputs)
                    infringment_messages.extend(opa_result['result'])
        return infringment_messages

    def evaluate_replica_policy(self, item, service_targets):
        """
        Evaluates the replica policy
        """
        parameters = {}
        services_just_one = {}
        for svc in service_targets:
            services_just_one[svc] = 1
        replicas = item.replicas
        parameters["parameters"] = {}
        parameters["parameters"]["services"] = {
            **services_just_one,
            **replicas
        }

        services = {"services": service_targets}
        replica_input = {**parameters, **services}
        # And verify it
        service_targets = self.opa_broker.ask_opa_policy_decision(
            "replicas", "solutions", replica_input)

        logger.debug(f"opa_result for replicas policy: {service_targets}")
        return service_targets

    def evaluate_sat_policy(self, attributes, opa_data, policy, user_params,
                            replicas):
        """
        Evaluates the Stack Application Template policies using OPA
        Returns the possible targets
        """
        policy_input = {
            "parameters": attributes,
            "user_parameters": user_params,
            "replicas": replicas
        }
        opa_data_with_inputs = {**opa_data, **policy_input}
        # Make sure the policy is in OPA
        if policy.policy:
            self.opa_broker.add_policy(policy.name, policy.policy)
        # And verify it
        new_solution = self.opa_broker.ask_opa_policy_decision(
            policy.name, "solutions", opa_data_with_inputs)
        logger.debug(
            f"opa_result for policy {policy.name}: {new_solution['result']}")
        new_result = new_solution['result']
        return new_result

    def evaluate_orchestration_policy(self, opa_data):
        """
        Evaluates the default orchestration policy
        """
        logger.debug(
            "[StackHandler] _handle_create. performing opa query with data: {0}"
            .format(opa_data))

        opa_result = self.opa_broker.ask_opa_policy_decision(
            "orchestration", "solutions", opa_data)
        logger.debug("opa_result: {0}".format(opa_result['result']))
        opa_solution = opa_result['result']
        return opa_solution

    def transform_opa_data(self, item, stack_app_template, stack_infr,
                           extra_services):
        """
        Transforms the SAT en SIT data to a format that OPA understands
        and adds extra needed data so OPA can evaluate more complicated
        policies
        """
        sit_as_opa_data = convert_sit_to_opa_data(stack_infr)
        services = []
        for service in stack_app_template.services:
            services.append({
                'name':
                service.name,
                'service':
                self.document_manager.get_service(service.service)
            })
        for service in extra_services:
            services.append({
                'name':
                service.name,
                'service':
                self.document_manager.get_service(service.service)
            })
        logger.debug(f"Services transformed for OPA data: {services}")
        sat_as_opa_data = self.opa_broker.convert_sat_to_opa_data(
            stack_app_template, services)
        required_tags = {}
        required_tags["required_tags"] = item.tags
        opa_data = {**required_tags, **sat_as_opa_data, **sit_as_opa_data}
        return opa_data

    def _update_infr_capabilities(
            self,
            stack_infr_template,
            update="auto") -> StackInfrastructureTemplate:
        """
        Merges the data from environment, location and zone and saves
        it in the stack infrastructure template
        """
        infr_targets = stack_infr_template.infrastructure_targets

        if update == "no":
            logger.debug(
                "[StackHandler] _update_infr_capabilities. update is '{0}', returning."
                .format(update))
            return stack_infr_template

        logger.debug(
            "[StackHandler] _update_infr_capabilities. update is '{0}', doing update."
            .format(update))
        infr_targets_capabilities = {}
        for infr_target in infr_targets:
            environment = self.document_manager.get_environment(
                infr_target.environment)
            location = self.document_manager.get_location(infr_target.location)
            zone = self.document_manager.get_zone(infr_target.zone)
            infr_target_capability = {
                **environment.params,
                **location.params,
                **zone.params
            }
            infr_target_tags = {
                **environment.tags,
                **location.tags,
                **zone.tags
            }
            infr_target_resources = environment.resources
            infr_target_secrets = {
                **environment.secrets,
                **location.secrets,
                **zone.secrets
            }
            infr_target_policies = {
                **environment.policies,
                **location.policies,
                **zone.policies
            }
            if zone.agent != "":
                infr_target_agent = zone.agent
            elif location.agent != "":
                infr_target_agent = location.agent
            elif environment.agent != "":
                infr_target_agent = environment.agent
            else:
                infr_target_agent = "common"

            if zone.cloud_provider != "":
                infr_target_cloud_provider = zone.cloud_provider
            elif location.cloud_provider != "":
                infr_target_cloud_provider = location.cloud_provider
            elif environment.cloud_provider != "":
                infr_target_cloud_provider = environment.cloud_provider
            else:
                infr_target_cloud_provider = "generic"

            infr_target_packages = environment.packages + location.packages + zone.packages
            infr_target_key = ".".join(
                [environment.name, location.name, zone.name])
            infr_targets_capabilities[
                infr_target_key] = StackInfrastructureTarget(
                    provisioning_parameters=infr_target_capability,
                    tags=infr_target_tags,
                    packages=infr_target_packages,
                    resources=infr_target_resources,
                    secrets=infr_target_secrets,
                    policies=infr_target_policies,
                    agent=infr_target_agent,
                    cloud_provider=infr_target_cloud_provider)
        stack_infr_template.infrastructure_capabilities = infr_targets_capabilities
        stack_infr_template.description = "SIT updated at {}".format(
            get_timestamp())
        self.document_manager.write_stack_infrastructure_template(
            stack_infr_template)
        return stack_infr_template

    def _handle_update(self, item):
        """
        Handle the update action of a stack instance
        """
        logger.debug(
            f"[StackHandler] _handle_update received with item: '{item}'")
        if "name" in item:
            stack_instance = self.document_manager.get_stack_instance(
                item.name)
        else:
            stack_instance = self.document_manager.get_stack_instance(
                item.stack_instance_name)

        stack_application_template = self.document_manager.get_stack_application_template(
            stack_instance.stack_application_template)
        stack_infrastructure_template = self.document_manager.get_stack_infrastructure_template(
            stack_instance.stack_infrastructure_template)

        stack_infr = self._update_infr_capabilities(
            stack_infrastructure_template, "yes")

        # Transform to OPA format
        opa_data = self.transform_opa_data(item, stack_application_template,
                                           stack_infr, item.services)

        opa_solution = self.evaluate_orchestration_policy(opa_data)

        if not opa_solution['fulfilled']:
            logger.error(
                f"[StackHandler]: Opa result message: {opa_solution['msg']}")
            return None, opa_solution['msg']

        service_targets = opa_solution['services']

        opa_service_params = tree()
        # Verify the SAT policies
        if stack_application_template.policies:
            for policy_name, attributes in stack_application_template.policies.items(
            ):
                policy = self.document_manager.get_policy_template(policy_name)
                for policy_params in attributes:
                    new_result = self.evaluate_sat_policy(
                        policy_params, opa_data, policy, {
                            **stack_instance.instance_params,
                            **item.params
                        }, item.replicas)

                    if not new_result['fulfilled']:
                        logger.error(
                            f"[StackHandler]: Opa result message: {new_result['msg']}"
                        )
                        return None, new_result['msg']

                    process_service_targets(policy_params,
                                            new_result,
                                            service_targets,
                                            opa_service_params,
                                            outputs=policy.outputs)
        if item.replicas != {}:
            service_targets = self.evaluate_replica_policy(
                item, service_targets)
            if not service_targets['result']['fulfilled']:
                return None, "Not enough targets for extra replicas"
            service_targets = service_targets["result"]["services"]
        # else:
        #     service_targets = None

        stack_instance = self._update_stack_instance(stack_instance, item,
                                                     opa_service_params,
                                                     service_targets)
        if isinstance(stack_instance, str):
            return None, stack_instance
        return stack_instance, "Stack instance updating"

    def _handle_delete(self, item):
        """
        Handles the delete action of a stack instance
        """
        logger.debug(
            f"[StackHandler] _handle_delete received with item: '{item}'")
        if "name" in item:
            stack_instance = self.document_manager.get_stack_instance(
                item['name'])
        else:
            stack_instance = self.document_manager.get_stack_instance(
                item['stack_instance_name'])

        return stack_instance, 200
