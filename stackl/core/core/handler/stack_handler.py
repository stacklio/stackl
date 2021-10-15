"""
Module containing all logic for creating and updating Stack instances
"""

from collections import OrderedDict
from typing import Any, Dict, List, TypedDict

from loguru import logger
import random

from core.enums.stackl_codes import StatusCode
from core.manager.document_manager import DocumentManager
from core.models.api.stack_instance import StackInstanceUpdate
from core.models.configs.infrastructure_base_document import PolicyDefinition
from core.models.configs.stack_application_template_model import \
    StackApplicationTemplate
from core.models.configs.stack_infrastructure_template_model import \
    StackInfrastructureTemplate
from core.models.items.stack_infrastructure_target_model import \
    StackInfrastructureTarget
from core.models.items.stack_instance_model import StackInstance
from core.models.items.stack_instance_service_model import StackInstanceService
from core.models.items.stack_instance_status_model import StackInstanceStatus
from core.utils.general_utils import get_timestamp, tree

from core.opa_broker.opa_broker import OPABroker, convert_sit_to_opa_data
from core.models.configs.infrastructure_target_model import InfrastructureTarget
from .handler import Handler


class OpaDecisionResult(TypedDict):
    target: InfrastructureTarget
    params: Dict[str, Any]


def concat_infra_target(target: InfrastructureTarget) -> str:
    return f"{target.environment}.{target.location}.{target.zone}"

def delete_services(to_be_deleted, stack_instance):
    for service in to_be_deleted:
        for key, _ in service.items():
            del stack_instance.services[key]

class StackHandler(Handler):
    """Handler responsible for all actions on Stack Instances"""
    def __init__(self, document_manager: DocumentManager,
                 opa_broker: OPABroker):
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
            self, item, opa_decision: Dict[str, List[OpaDecisionResult]],
            stack_infrastructure_template: StackInfrastructureTemplate,
            stack_application_template: StackApplicationTemplate):
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
        if item.stages:
            stack_instance_doc.stages = item.stages
        else:
            stack_instance_doc.stages = stack_application_template.stages
        services = OrderedDict()
        stack_instance_statuses = []
        for svc, opa_result in opa_decision.items():
            # if a svc doesnt have a result raise an error cause we cant resolve it
            svc_doc = self.document_manager.get_service(svc)
            service_definitions = []
            for infra_target in opa_result:
                infra_target_counter = 1
                service_definition = self.add_service_definition(
                    infra_target["target"], infra_target_counter, item,
                    infra_target["params"], stack_infrastructure_template,
                    stack_instance_statuses, svc, svc_doc)
                service_definitions.append(service_definition)
                infra_target_counter += 1
            services[svc] = service_definitions
        stack_instance_doc.services = services
        stack_instance_doc.status = stack_instance_statuses
        return stack_instance_doc

    def add_service_definition(self, infra_target: InfrastructureTarget,
                               infra_target_counter, item, opa_service_params,
                               stack_infrastructure_template,
                               stack_instance_statuses, svc, svc_doc):
        """
        Function for adding a service_definition item to a stack_instance
        """
        service_definition = StackInstanceService()
        service_definition.service = svc_doc.name
        service_definition.infrastructure_target = concat_infra_target(
            infra_target)
        service_definition.opa_outputs = opa_service_params
        capabilities_of_target = stack_infrastructure_template.infrastructure_capabilities[
            f"{infra_target.environment}.{infra_target.location}.{infra_target.zone}"].provisioning_parameters
        secrets_of_target = stack_infrastructure_template.infrastructure_capabilities[
            f"{infra_target.environment}.{infra_target.location}.{infra_target.zone}"].secrets
        agent = stack_infrastructure_template.infrastructure_capabilities[
            f"{infra_target.environment}.{infra_target.location}.{infra_target.zone}"].agent
        cloud_provider = stack_infrastructure_template.infrastructure_capabilities[
            f"{infra_target.environment}.{infra_target.location}.{infra_target.zone}"].cloud_provider
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
                        infrastructure_target=concat_infra_target(
                            infra_target),
                        status="in_progress",
                        error_message="")
                    stack_instance_statuses.append(stack_instance_status)
            else:
                stack_instance_status = StackInstanceStatus(
                    functional_requirement=fr,
                    service=svc,
                    infrastructure_target=concat_infra_target(infra_target),
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
            **item.params,
            **item.service_params.get(svc, {}),
            **service_definition.opa_outputs
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
                               item: StackInstanceUpdate, possible_targets):
        """
        This method takes a stack instance and an item
        which contains the extra parameters and secrets
        """
        if item.stages:
            stack_instance.stages = item.stages
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
                found = False
                for ti in possible_targets[svc].copy():
                    if service_definition.infrastructure_target == concat_infra_target(
                            ti['target']):
                        found = True
                        service_definition = self.update_service_definition(
                            count, item, ti["params"], service_definition,
                            stack_infrastructure_template, stack_instance,
                            stack_instance_statuses, svc, svc_doc)
                        possible_targets[svc].remove(ti)
                if not found:
                    return f"Update not possible, target: {service_definition.infrastructure_target} for service {svc} is not available anymore"
                stack_instance.services[svc][count] = service_definition

            # Check if replica count increased
            svc_doc = self.document_manager.get_service(
                service_definitions[0].service)
            if svc in item.replicas and item.replicas[svc] > len(
                    service_definitions):
                if len(possible_targets[svc]
                       ) < item.replicas[svc] - len(service_definitions):
                    return "Not enough possible targets to fullfill replicas"
                while len(new_service_definitions) + len(
                        service_definitions) != item.replicas[svc]:
                    target = possible_targets[svc].pop(
                        random.randint(0,
                                       len(possible_targets[svc]) - 1))
                    service_definition = self.add_service_definition(
                        target['target'],
                        len(new_service_definitions) +
                        len(service_definitions), item, target["params"],
                        stack_infrastructure_template, stack_instance_statuses,
                        svc, svc_doc)
                    if not svc in new_service_definitions:
                        new_service_definitions[svc] = []
                    new_service_definitions[svc].append(service_definition)

        for service in item.services:
            if service.name not in stack_instance.services:
                svc_doc = self.document_manager.get_service(service.service)
                service_definition = self.add_service_definition(
                    possible_targets[service.name][0]["target"], 0, item,
                    possible_targets[service.name][0]["params"],
                    stack_infrastructure_template, stack_instance_statuses,
                    service.name, svc_doc)
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
        service_definition.opa_outputs = opa_service_params
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
            **stack_instance.instance_params,
            **stack_instance.service_params.get(svc, {}),
            **opa_outputs
        }
        service_definition.secrets = {
            **merged_secrets,
            **stack_instance.instance_secrets,
            **stack_instance.service_secrets.get(svc, {})
        }
        service_definition.agent = agent

        return service_definition

    def add_outputs(self, outputs_update):
        """
        Adds outputs on the right service definition of a stack instance
        """
        logger.debug(f"Adding outputs to stack_instance {outputs_update}")
        stack_instance = self.document_manager.get_stack_instance(
            outputs_update.stack_instance)
        stack_instance.instance_outputs = {
            **stack_instance.instance_outputs,
            **outputs_update.outputs
        }
        service = stack_instance.services[outputs_update.service]
        for service_definition in service:
            if service_definition.infrastructure_target == outputs_update.infrastructure_target:
                service_definition.outputs = {
                    **service_definition.outputs,
                    **outputs_update.outputs
                }
                if "stackl_hosts" in service_definition.outputs:
                    service_definition.hosts = service_definition.outputs[
                        "stackl_hosts"]
                break
        for _, service_list in stack_instance.services.items():
            for service_definition in service_list:
                service_definition.provisioning_parameters = {
                    **service_definition.provisioning_parameters,
                    **stack_instance.instance_outputs,
                    **service_definition.outputs
                }

        return stack_instance

    def evaluate_policies(self, services, stack_infr, item):
        possible_targets = {}
        for s in services:
            possible_targets[s.name] = [{
                "target": t,
                "params": {}
            } for t in stack_infr.infrastructure_targets]
        for infra_target in stack_infr.infrastructure_targets:
            enviroment = self.document_manager.get_environment(
                infra_target.environment)
            location = self.document_manager.get_location(
                infra_target.location)
            zone = self.document_manager.get_zone(infra_target.zone)
            policies: List[PolicyDefinition] = []
            policies += enviroment.policies + location.policies + zone.policies
            infra_target_data = {
                "infrastructure_target": {
                    "tags":
                    stack_infr.infrastructure_capabilities[
                        f"{enviroment.name}.{location.name}.{zone.name}"].tags,
                    "params":
                    stack_infr.infrastructure_capabilities[
                        f"{enviroment.name}.{location.name}.{zone.name}"].
                    provisioning_parameters
                }
            }
            for policy in policies:
                policy_doc = self.document_manager.get_policy_template(
                    policy.name)
                self.opa_broker.add_policy(policy_doc.name, policy_doc.policy)
                service_kind = policy.service_kind
                services_to_evaluate = [
                    s for s in services if service_kind in s.kinds
                ]
                for service in services_to_evaluate:
                    service_opa_data = self.opa_broker.convert_service_to_opa_data(
                        service)
                    opa_data = {
                        **infra_target_data,
                        **service_opa_data,
                        **{
                            "stack_parameters": item.params
                        },
                        **{
                            "policy_parameters": policy.parameters
                        }
                    }
                    opa_result = self.opa_broker.ask_opa_policy_decision(
                        policy.name, "resolve", opa_data)

                    logger.debug(opa_result["result"])
                    if len(
                            opa_result["result"]
                    ) == 0 or infra_target in possible_targets[service.name]:
                        for i in possible_targets[service.name].copy():
                            if i["target"] == infra_target:
                                possible_targets[service.name].remove(i)
                    else:
                        for x in possible_targets[service.name]:
                            if x["target"] == infra_target:
                                logger.debug(x['params'])
                                x['params'] = {
                                    **x["params"],
                                    **opa_result["result"][0]["params"]
                                }

        return possible_targets

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
        services = [
            self.document_manager.get_service(s.name)
            for s in stack_app_template.services
        ]
        possible_targets = self.evaluate_policies(services, stack_infr, item)
        for s in services:
            if not possible_targets[s.name]:
                return None, f"No possible target found for service {s.name}"

            choose_count = 1
            if s.name in item.replicas:
                choose_count = item.replicas[s.name]

            if len(possible_targets[s.name]) < choose_count:
                return None, f"Not enough targets for service {s.name}"

            # STACKL ROULETTE
            while len(possible_targets[s.name]) != choose_count:
                possible_targets[s.name].pop(
                    random.randint(0,
                                   len(possible_targets[s.name]) - 1))

        return self._create_stack_instance(
            item, possible_targets, stack_infr,
            stack_app_template), possible_targets

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
            infr_target_policies = [
                environment.policies, location.policies, zone.policies
            ]
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

            infr_target_key = ".".join(
                [environment.name, location.name, zone.name])
            infr_targets_capabilities[
                infr_target_key] = StackInfrastructureTarget(
                    provisioning_parameters=infr_target_capability,
                    tags=infr_target_tags,
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
        services = [
            self.document_manager.get_service(s.name)
            for s in stack_application_template.services
        ]
        possible_targets = self.evaluate_policies(services, stack_infr, item)

        stack_instance = self._update_stack_instance(stack_instance, item,
                                                     possible_targets)
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
