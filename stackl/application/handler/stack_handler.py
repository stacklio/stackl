import logging

from enums.stackl_codes import StatusCode
from handler import Handler
from model.configs.stack_infrastructure_template_model import StackInfrastructureTemplate
from model.items.functional_requirement_status_model import FunctionalRequirementStatus, Status
from model.items.stack_instance_model import StackInstance
from model.items.stack_instance_service_model import StackInstanceService
from model.items.stack_instance_status_model import StackInstanceStatus
from utils.general_utils import get_timestamp
from utils.stackl_exceptions import NoOpaResultException

logger = logging.getLogger("STACKL_LOGGER")


class StackHandler(Handler):
    def __init__(self, document_manager, opa_broker):
        super(StackHandler, self).__init__()
        self.document_manager = document_manager
        self.opa_broker = opa_broker
        self.opa_broker.document_manager = self.document_manager

    def handle(self, item):
        action = item['action']
        if action == 'create':
            logger.debug("[StackHandler] handle. received create task")
            return self._handle_create(item['document'])
        if action == 'update':
            logger.debug("[StackHandler] handle. received update task")
            return self._handle_update(item['document'])
        if action == 'delete':
            logger.debug("[StackHandler] handle. received delete task")
            return self._handle_delete(item['document'])
        return StatusCode.BAD_REQUEST

    def _create_stack_instance(
        self, item, opa_decision,
        stack_infrastructure_template: StackInfrastructureTemplate):
        stack_instance_doc = StackInstance(
            name=item['stack_instance_name'],
            stack_infrastructure_template=item[
                'stack_infrastructure_template'],
            stack_application_template=item['stack_application_template'])
        stack_instance_doc.instance_params = item['params']
        stack_instance_doc.instance_secrets = item['secrets']
        services = {}
        stack_instance_statuses = []
        for svc, targets in opa_decision.items():
            # if a svc doesnt have a result raise an error cause we cant resolve it
            svc_doc = self.document_manager.get_service(svc)

            # TODO take first target in list if multiple, maybe we should let opa always only return one?
            service_definitions = []
            for infra_target in targets:
                service_definition = StackInstanceService()
                service_definition.infrastructure_target = infra_target

                service_definition_status = []
                capabilities_of_target = stack_infrastructure_template.infrastructure_capabilities[
                    infra_target]["provisioning_parameters"]
                secrets_of_target = stack_infrastructure_template.infrastructure_capabilities[
                    infra_target]["secrets"]
                merged_capabilities = {
                    **capabilities_of_target,
                    **svc_doc.params
                }
                merged_secrets = {**secrets_of_target, **svc_doc.secrets}
                for fr in svc_doc.functional_requirements:
                    stack_instance_status = StackInstanceStatus(
                        functional_requirement=fr,
                        service=svc,
                        infrastructure_target=infra_target,
                        status=Status.PROGRESS,
                        error_message="")
                    stack_instance_statuses.append(stack_instance_status)
                    fr_doc = self.document_manager.get_functional_requirement(
                        fr)
                    merged_capabilities = {
                        **merged_capabilities,
                        **fr_doc.params
                    }
                    merged_secrets = {**merged_secrets, **fr_doc.secrets}
                service_definition.provisioning_parameters = {
                    **merged_capabilities,
                    **item['params']
                }
                service_definition.secrets = {
                    **merged_secrets,
                    **item['secrets']
                }
                service_definitions.append(service_definition)
            services[svc] = service_definitions
        stack_instance_doc.services = services
        stack_instance_doc.status = stack_instance_statuses
        return stack_instance_doc

    def _update_stack_instance(self, stack_instance: StackInstance, item):
        """This method takes a stack instance and an item which contains the extra parameters and secrets"""
        stack_infr_template = self.document_manager.get_stack_infrastructure_template(
            stack_instance.stack_infrastructure_template)
        stack_infrastructure_template = self._update_infr_capabilities(
            stack_infr_template, "yes")
        stack_instance.instance_params = {
            **stack_instance.instance_params,
            **item['params']
        }
        stack_instance.instance_secrets = {
            **stack_instance.instance_secrets,
            **item['secrets']
        }

        stack_instance_statuses = []
        for svc, service_definitions in stack_instance.services.items():
            for count, service_definition in enumerate(service_definitions):
                svc_doc = self.document_manager.get_service(svc)
                capabilities_of_target = stack_infrastructure_template.infrastructure_capabilities[
                    service_definition.
                    infrastructure_target]["provisioning_parameters"]
                secrets_of_target = stack_infrastructure_template.infrastructure_capabilities[
                    service_definition.infrastructure_target]["secrets"]
                merged_capabilities = {
                    **capabilities_of_target,
                    **svc_doc.params
                }
                merged_secrets = {**secrets_of_target, **svc_doc.secrets}
                for fr in svc_doc.functional_requirements:
                    if not item["disable_invocation"]:
                        stack_instance_status = StackInstanceStatus(
                            functional_requirement=fr,
                            service=svc,
                            infrastructure_target=service_definition.
                            infrastructure_target,
                            status=Status.PROGRESS,
                            error_message="")
                        stack_instance_statuses.append(stack_instance_status)
                    fr_doc = self.document_manager.get_functional_requirement(
                        fr)
                    merged_capabilities = {
                        **merged_capabilities,
                        **fr_doc.params
                    }
                    merged_secrets = {**merged_secrets, **fr_doc.secrets}
                service_definition.provisioning_parameters = {
                    **merged_capabilities,
                    **stack_instance.instance_params
                }
                service_definition.secrets = {
                    **merged_secrets,
                    **stack_instance.instance_secrets
                }
                stack_instance.services[svc][count] = service_definition
        stack_instance.status = stack_instance_statuses
        return stack_instance

    def _handle_create(self, item):
        logger.debug(
            "[StackHandler] _handle_create received with item: {0}".format(
                item))
        stack_infr_template = self.document_manager.get_stack_infrastructure_template(
            item['stack_infrastructure_template'])
        stack_app_template = self.document_manager.get_stack_application_template(
            item['stack_application_template'])

        stack_infr = self._update_infr_capabilities(stack_infr_template, "yes")

        # Transform to OPA format
        opa_data = self.transform_opa_data(item, stack_app_template,
                                           stack_infr)

        opa_solution = self.evaluate_orchestration_policy(opa_data)

        if not opa_solution['fulfilled']:
            logger.error(
                f"[StackHandler]: Opa result message: {opa_solution['msg']}")
            return None, StatusCode.BAD_REQUEST

        service_targets = opa_solution['services']

        # Verify the SAT policies
        for policy_name, attributes in stack_app_template.policies.items():
            for policy_params in attributes:
                new_result = self.evaluate_sat_policy(policy_params, opa_data,
                                                      policy_name)

                if not new_result['fulfilled']:
                    logger.error(
                        f"[StackHandler]: Opa result message: {new_result['msg']}"
                    )
                    return None, StatusCode.BAD_REQUEST

                self.process_service_targets(policy_params, new_result,
                                             service_targets)

        service_targets = self.evaluate_replica_policy(item, service_targets)
        if not service_targets['result']['fulfilled']:
            logger.error(
                f"[StackHandler] _handle_create. replica_policy not satisfied: {service_targets['result']['msg']}"
            )
            return None, StatusCode.BAD_REQUEST

        # Verify that each of the SIT policies doesn't violate

        infringment_messages = self.evaluate_sit_policies(
            opa_data, service_targets, stack_infr)

        if infringment_messages:
            logger.error(
                f"[StackHandler] _handle_create. sit policies not satisfied {infringment_messages}"
            )
            return None, StatusCode.BAD_REQUEST

        try:
            return self._create_stack_instance(
                item, service_targets['result']['services'], stack_infr), 200
        except NoOpaResultException:
            return None, StatusCode.BAD_REQUEST

    def evaluate_sit_policies(self, opa_data, service_targets, stack_infr):
        infringment_messages = []
        for service, targets in service_targets['result']['services'].items():
            for t in targets:
                policies = stack_infr.infrastructure_capabilities[t][
                    'policies']

                for policy_name, policy_attributes in policies.items():
                    policy = self.document_manager.get_policy_template(
                        policy_name)

                    # Make sure the policy is in OPA
                    self.opa_broker.add_policy(policy.name, policy.policy)

                    policy_input = {"parameters": policy_attributes}

                    opa_data_with_inputs = {**opa_data, **policy_input}
                    # evaluate
                    opa_result = self.opa_broker.ask_opa_policy_decision(
                        policy.name, "infringement", opa_data_with_inputs)
                    infringment_messages.extend(opa_result['result'])
        return infringment_messages

    def evaluate_replica_policy(self, item, service_targets):
        parameters = {}
        services_just_one = {}
        for svc in service_targets:
            services_just_one[svc] = 1
        if 'replicas' in item:
            #TODO verwijder dit
            logger.debug("hij steekt erin")
            replicas = item['replicas']
            parameters["parameters"] = {}
            parameters["parameters"]["services"] = {
                **services_just_one,
                **replicas
            }
        else:
            parameters["parameters"] = {}
            parameters["parameters"]["services"] = services_just_one
        services = {"services": service_targets}
        replica_input = {**parameters, **services}
        # And verify it
        service_targets = self.opa_broker.ask_opa_policy_decision(
            "replicas", "solutions", replica_input)
        logger.debug(
            f"[StackHandler] _handle_create. opa_result for replicas policy: {service_targets['result']}"
        )
        return service_targets

    def process_service_targets(self, attributes, new_result, service_targets):
        service = attributes['service']
        st = service_targets[service]
        new_targets = []
        for t in st:
            if t in new_result['targets']:
                new_targets.append(t)
        service_targets[service] = new_targets

    def evaluate_sat_policy(self, attributes, opa_data, policy_name):
        policy_input = {}
        policy = self.document_manager.get_policy_template(policy_name)
        policy_input["parameters"] = attributes
        opa_data_with_inputs = {**opa_data, **policy_input}
        # Make sure the policy is in OPA
        self.opa_broker.add_policy(policy.name, policy.policy)
        # And verify it
        new_solution = self.opa_broker.ask_opa_policy_decision(
            policy.name, "solutions", opa_data_with_inputs)
        logger.debug(
            f"[StackHandler] _handle_create. opa_result for policy {policy.name}: {new_solution['result']}"
        )
        new_result = new_solution['result']
        return new_result

    def evaluate_orchestration_policy(self, opa_data):
        logger.debug(
            "[StackHandler] _handle_create. performing opa query with data: {0}"
            .format(opa_data))

        opa_result = self.opa_broker.ask_opa_policy_decision(
            "orchestration", "solutions", opa_data)
        logger.debug("[StackHandler] _handle_create. opa_result: {0}".format(
            opa_result['result']))
        opa_solution = opa_result['result']
        return opa_solution

    def transform_opa_data(self, item, stack_app_template, stack_infr):
        sit_as_opa_data = self.opa_broker.convert_sit_to_opa_data(stack_infr)
        services = []
        for s in stack_app_template.services:
            services.append(self.document_manager.get_service(s))
        sat_as_opa_data = self.opa_broker.convert_sat_to_opa_data(
            stack_app_template, services)
        required_tags = {}
        required_tags["required_tags"] = item["tags"]
        opa_data = {**required_tags, **sat_as_opa_data, **sit_as_opa_data}
        return opa_data

    ##TODO Deprecate in the future once OPA is up
    def _filter_zones_req_application(self, matching_zones_app_req, app_infr):
        logger.debug(
            "[StackHandler] _filter__filter_zones_req_applicationzones_req_services. Filtering for zones '{0}' and app_infr '{1}'"
            .format(matching_zones_app_req, app_infr))
        for (service, zone) in matching_zones_app_req:
            list_of_same_zone_services = [
                other_service
                for (other_service, other_zone) in matching_zones_app_req
                if (zone == other_zone)
            ]
            for other_service in list_of_same_zone_services:
                poss_targets_intersection = list(
                    set(app_infr[service].keys())
                    & set(app_infr[other_service].keys()))
                logger.debug(
                    "[StackHandler] _filter_zones_req_application. Filtering for intersection '{0}' of services zones '{0}' for service {1} and other_service {2}"
                    .format(poss_targets_intersection, service, other_service))
                if poss_targets_intersection is []:
                    return "The given SIT cannot satisfy the SAT: there are services that need to share zones but cannot"
                else:
                    for poss_target in app_infr[service].keys():
                        if poss_target not in poss_targets_intersection:
                            del app_infr[service][poss_target]
                    for poss_target in app_infr[other_service].keys():
                        if poss_target not in poss_targets_intersection:
                            del app_infr[other_service][poss_target]
        return app_infr

    ##TODO can probably be offloaded to OPA and doesn't belong here in any case I think
    def _update_infr_capabilities(
            self,
            stack_infr_template,
            update="auto") -> StackInfrastructureTemplate:
        infr_targets = stack_infr_template.infrastructure_targets
        prev_infr_capabilities = stack_infr_template.infrastructure_capabilities

        if update == "no":
            logger.debug(
                "[StackHandler] _update_infr_capabilities. update is '{0}', returning."
                .format(update))
            return stack_infr_template
        elif update == "auto":
            # TODO Implement. update (partly) when and if necessary: nothing is there yet or some time out value occured
            logger.debug(
                "[StackHandler] _update_infr_capabilities. update is '{0}', evaluating condition."
                .format(update))
            if all((len(prev_infr_capabilities[prev_infr_capability]) > 3)
                   for prev_infr_capability in prev_infr_capabilities):
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
            infr_target_packages = environment.packages + location.packages + zone.packages
            infr_target_key = ".".join(
                [environment.name, location.name, zone.name])
            infr_targets_capabilities[infr_target_key] = {}
            infr_targets_capabilities[infr_target_key][
                "provisioning_parameters"] = infr_target_capability
            infr_targets_capabilities[infr_target_key][
                "tags"] = infr_target_tags
            infr_targets_capabilities[infr_target_key][
                "packages"] = infr_target_packages
            infr_targets_capabilities[infr_target_key][
                "resources"] = infr_target_resources
            infr_targets_capabilities[infr_target_key][
                "secrets"] = infr_target_secrets
            infr_targets_capabilities[infr_target_key][
                "policies"] = infr_target_policies
        stack_infr_template.infrastructure_capabilities = infr_targets_capabilities
        stack_infr_template.description = "SIT updated at {}".format(
            get_timestamp())
        self.document_manager.write_stack_infrastructure_template(
            stack_infr_template)
        return stack_infr_template

    def _handle_update(self, item):
        logger.debug(
            "[StackHandler] _handle_update received with item: {0}.".format(
                item))
        stack_instance = self.document_manager.get_stack_instance(
            item['stack_instance_name'])
        stack_instance = self._update_stack_instance(stack_instance, item)
        return stack_instance, 200

    def _handle_delete(self, item):
        logger.debug(
            "[StackHandler] _handle_delete received with item: {0}.".format(
                item))
        stack_instance = self.document_manager.get_stack_instance(
            item['stack_instance_name'])
        stack_instance.deleted = True
        return stack_instance, 200
