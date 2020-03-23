import logging

from enums.stackl_codes import StatusCode
from handler import Handler
from model.configs.stack_infrastructure_template_model import StackInfrastructureTemplate
from model.items.functional_requirement_status_model import FunctionalRequirementStatus, Status
from model.items.stack_instance_model import StackInstance
from model.items.stack_instance_service_model import StackInstanceService
from utils.general_utils import get_timestamp

logger = logging.getLogger("STACKL_LOGGER")


class NoOpaResultException(Exception):
    pass


class StackHandler(Handler):

    def __init__(self, manager_factory, opa_broker):
        super(StackHandler, self).__init__(manager_factory)
        self.document_manager = manager_factory.get_document_manager()
        self.opa_broker = opa_broker
        self.hiera = manager_factory.get_item_manager()

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

    def _create_stack_instance(self, item, opa_decision, stack_infrastructure_template: StackInfrastructureTemplate):
        stack_instance_doc = StackInstance(name=item['stack_instance_name'])
        services = {}
        for svc, targets in opa_decision.items():
            # if a svc doesnt have a result raise an error cause we cant resolve it
            if len(targets) == 0:
                raise NoOpaResultException
            svc_doc = self.document_manager.get_service(svc)
            service_definition = StackInstanceService()
            service_definition_status = []
            # TODO take first target in list if multiple, maybe we should let opa always only return one?
            infra_target = targets[0]
            service_definition.infrastructure_target = infra_target
            capabilities_of_target = stack_infrastructure_template.infrastructure_capabilities[infra_target]
            merged_capabilities = {**capabilities_of_target, **svc_doc.params}
            for fr in svc_doc.functional_requirements:
                fr_status = FunctionalRequirementStatus(
                    functional_requirement=fr,
                    status=Status.in_progress,
                    error_message=""
                )
                service_definition_status.append(fr_status)
                fr_doc = self.document_manager.get_functional_requirement(fr)
                merged_capabilities = {**merged_capabilities, **fr_doc.params}
            service_definition.provisioning_parameters = {**merged_capabilities, **item['params']}
            service_definition.status = service_definition_status
            service_definition.connection_credentials = item['connection_credentials']
            services[svc] = service_definition
            stack_instance_doc.services = services
        return stack_instance_doc

    def merge_capabilities(self, stack_infr_template, stack_instance, item):
        """This method takes a stack_infr_template, a stack instance and an item which contains the extra parameters"""
        for svc in stack_instance.services:
            infra_capabilities = stack_infr_template.infrastructure_capabilities[
                stack_instance.services[svc].infrastructure_target]
            svc_doc = self.document_manager.get_service(svc)
            merged_capabilities = {**infra_capabilities, **svc_doc.params}
            for fr in svc_doc.functional_requirements:
                fr_doc = self.document_manager.get_functional_requirement(fr)
                merged_capabilities = {**merged_capabilities, **fr_doc.params}
            stack_instance.services[svc].provisioning_parameters = {**merged_capabilities, **item['params']}
            stack_instance.services[svc].connection_credentials = item['connection_credentials']
        return stack_instance

    ##TODO so this code needs to be rescoped in terms of the OPA. We don't do the constrint solving ourselves anymore
    def _handle_create(self, item):
        logger.debug("[StackHandler] _handle_create received with item: {0}".format(item))
        stack_infr_template = self.document_manager.get_stack_infrastructure_template(
            item['stack_infrastructure_template'])
        stack_app_template = self.document_manager.get_stack_application_template(item['stack_application_template'])

        stack_infr = self._update_infr_capabilities(stack_infr_template, "yes")
        logger.debug("[StackHandler] _handle_create. stack_infr: {0}".format(stack_infr))

        # Transform to OPA format
        sit_as_opa_data = self.opa_broker.convert_sit_to_opa_data(stack_infr)
        services = []
        for s in stack_app_template.services:
            services.append(self.document_manager.get_service(s))
        sat_as_opa_data = self.opa_broker.convert_sat_to_opa_data(stack_app_template, services)
        opa_data = {**sat_as_opa_data, **sit_as_opa_data}

        logger.debug("[StackHandler] _handle_create. performing opa query with data: {0}".format(opa_data))

        # TODO Define queries here for now only one
        opa_result = self.opa_broker.ask_opa_policy_decision("orchestration", "all_solutions", opa_data)
        logger.debug("[StackHandler] _handle_create. opa_result: {0}".format(opa_result['result']))

        try:
            return self._create_stack_instance(item, opa_result['result'], stack_infr), 200
        except NoOpaResultException:
            return None, StatusCode.FORBIDDEN



    ##TODO Deprecate in the future once OPA is up
    def _filter_zones_req_application(self, matching_zones_app_req, app_infr):
        logger.debug(
            "[StackHandler] _filter__filter_zones_req_applicationzones_req_services. Filtering for zones '{0}' and app_infr '{1}'".format(
                matching_zones_app_req, app_infr))
        for (service, zone) in matching_zones_app_req:
            list_of_same_zone_services = [other_service for (other_service, other_zone) in matching_zones_app_req if
                                          (zone == other_zone)]
            for other_service in list_of_same_zone_services:
                poss_targets_intersection = list(set(app_infr[service].keys()) & set(app_infr[other_service].keys()))
                logger.debug(
                    "[StackHandler] _filter_zones_req_application. Filtering for intersection '{0}' of services zones '{0}' for service {1} and other_service {2}".format(
                        poss_targets_intersection, service, other_service))
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
    def _update_infr_capabilities(self, stack_infr_template, update="auto") -> StackInfrastructureTemplate:
        infr_targets = stack_infr_template.infrastructure_targets
        prev_infr_capabilities = stack_infr_template.infrastructure_capabilities

        if update == "no":
            logger.debug("[StackHandler] _update_infr_capabilities. update is '{0}', returning.".format(update))
            return stack_infr_template
        elif update == "auto":
            # TODO Implement. update (partly) when and if necessary: nothing is there yet or some time out value occured
            logger.debug(
                "[StackHandler] _update_infr_capabilities. update is '{0}', evaluating condition.".format(update))
            if all((len(prev_infr_capabilities[prev_infr_capability]) > 3) for prev_infr_capability in
                   prev_infr_capabilities):
                return stack_infr_template

        logger.debug("[StackHandler] _update_infr_capabilities. update is '{0}', doing update.".format(update))
        infr_targets_capabilities = {}
        for infr_target in infr_targets:
            environment = self.document_manager.get_environment(infr_target.environment)
            location = self.document_manager.get_location(infr_target.location)
            zone = self.document_manager.get_zone(infr_target.zone)
            infr_target_capability = {**environment.params, **location.params, **zone.params}
            infr_target_key = ".".join([environment.name, location.name, zone.name])
            infr_targets_capabilities[infr_target_key] = infr_target_capability
        stack_infr_template.infrastructure_capabilities = infr_targets_capabilities
        stack_infr_template.description = "SIT updated at {}".format(get_timestamp())
        self.document_manager.write_stack_infrastructure_template(stack_infr_template)
        return stack_infr_template

    # TODO Lets remove this since we are going to use OPA
    # def _post_processing_capability(self, infr_target_capability):
    #     #TODO: an intelligent system needs to be put here so that the infrastructure capabilities can be matched with the service requirements. Something that allows to determine that, for instance, AWS servers can host a certain set of functional dependencies. At the moment this is hardcoded in _update_infr_capabilities and we only check some service requirements.
    #     if "aws" in infr_target_capability["name"]:
    #         infr_target_capability.update({"config": ["Ubuntu", "Alpine", "DatabaseConfig"]})
    #         infr_target_capability.update({"CPU": "2GHz", "RAM": "2GB"})
    #     if "vmw" in infr_target_capability["name"]:
    #         infr_target_capability.update({"config": ["linux", "nginx"]})
    #         infr_target_capability.update({"CPU": "4GHz", "RAM": "4GB"})
    #     return

    def _handle_update(self, item):
        logger.debug("[StackHandler] _handle_update received with item: {0}.".format(item))
        stack_infr_template = self.document_manager.get_stack_infrastructure_template(
            item['stack_infrastructure_template'])

        stack_infr = self._update_infr_capabilities(stack_infr_template, "yes")
        stack_instance = self.document_manager.get_stack_instance(item['stack_instance_name'])
        stack_instance = self.merge_capabilities(stack_infr, stack_instance, item)
        return stack_instance, 200

    def _handle_delete(self, item):
        logger.debug("[StackHandler] _handle_delete received with item: {0}.".format(item))
        stack_instance = self.document_manager.get_stack_instance(item['stack_instance_name'])
        return stack_instance, 200
