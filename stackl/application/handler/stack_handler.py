import copy
import logging

from enums.stackl_codes import StatusCode
from handler import Handler

logger = logging.getLogger("STACKL_LOGGER")
from model.items.functional_requirement_status import FunctionalRequirementStatus, Status
from model.items.stack_instance import StackInstance
from model.items.stack_instance_service import StackInstanceService
from utils.general_utils import get_timestamp


class StackHandler(Handler):

    def __init__(self, manager_factory):
        super(StackHandler, self).__init__(manager_factory)

        self.document_manager = manager_factory.get_document_manager()
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

    def _create_stack_instance(self, item, merged_sit_sat):
        stack_instance_doc = StackInstance(name=item['stack_instance_name'])
        services = {}
        for svc in merged_sit_sat:
            svc_doc = self.document_manager.get_service(svc)
            service_definition = StackInstanceService()
            service_definition_status = []
            for infra_target in merged_sit_sat[svc]:
                service_definition.infrastructure_target = infra_target
                merged_capabilities = {**merged_sit_sat[svc][infra_target], **svc_doc.params}
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

    def _handle_create(self, item):
        logger.debug("[StackHandler] _handle_create received with item: {0}".format(item))
        stack_infr_template = self.document_manager.get_stack_infrastructure_template(
            item['stack_infrastructure_template'])
        stack_app_template = self.document_manager.get_stack_application_template(item['stack_application_template'])

        stack_infr = self._update_infr_capabilities(stack_infr_template, "yes")
        logger.debug("[StackHandler] _handle_create. stack_infr: {0}".format(stack_infr))

        # TODO fix again
        # if "infrastructure_target" in item:
        #     logger.debug("[StackHandler] _handle_create. target specified so no need for constraint processing")
        #     stack_instance_doc = {}
        #     stack_instance_doc['name'] = item['stack_instance_name']
        #     stack_instance_doc['type'] = "stack_instance"
        #     infra_capabilities = stack_infr.infrastructure_capabilities[item["infrastructure_target"]]
        #     services = {}
        #     for svc in stack_app_template.services:
        #         svc_doc = self.document_manager.get_document(
        #                                 type='service',
        #                                 document_name=svc)
        #         service_definition = {}
        #         service_definition['infrastructure_target'] = item['infrastructure_target']
        #         merged_capabilities = {**infra_capabilities, **svc_doc['params']}
        #         for fr in svc_doc['functional_requirements']:
        #             fr_doc = self.document_manager.get_document(
        #                 type='functional_requirement',
        #                 document_name=fr)
        #             merged_capabilities = {**merged_capabilities, **fr_doc['params']}
        #         service_definition['provisioning_parameters'] = {**merged_capabilities, **item['params']}
        #         services[svc] = service_definition
        #     stack_instance_doc['services'] = services
        #     return stack_instance_doc, 200

        # Create a single list of requirements per service
        logger.debug(
            "[StackHandler] _handle_create. Constraint solving. Each service in the application should have a list of potential infr_targets. If not the case, the given SIT cannot satisfy the SAT.")

        should_restart = True
        first_run = True
        new_sat = None
        while should_restart:
            if should_restart and not first_run:
                logger.debug("[StackHandler] _handle_create. Constraint solving was restarted")
                stack_app_template = new_sat
            should_restart = False
            first_run = False
            merged_app_infr = {}
            list_of_req_serv = []
            list_of_req_matching_zones = []
            for service in stack_app_template.services:
                # Get service document
                svc_doc = self.document_manager.get_service(service)
                merged_app_infr.update({service: {}})
                serv_req = {}
                serv_req.update({"config": svc_doc.functional_requirements})
                serv_req.update(svc_doc.non_functional_requirements)
                serv_req.update(stack_app_template.extra_functional_requirements)
                logger.debug("[StackHandler] _handle_create. Serv_req {0}".format(serv_req))
                # determine possible infra targets for the service
                for infr_target in stack_infr.infrastructure_capabilities:
                    capabilities = stack_infr.infrastructure_capabilities[infr_target]
                    # TODO: an intelligent system needs to be put here so that the infrastructure capabilities can be matched with the service requirements. Something that allows to determine that, for instance, AWS servers can host a certain set of functional dependencies. At the moment this is hardcoded in _update_infr_capabilities and we only check some service requirements.
                    logger.debug(
                        "[StackHandler] _handle_create. Constraint solving. infr_target {0} and capabilities  '{1}'".format(
                            infr_target, capabilities))

                    potential_target = True
                    for req in list(serv_req.keys()):
                        logger.debug("[StackHandler] _handle_create. Constraint solving for serv_req {}".format(req))
                        if req == "config":
                            if not all(config_req in capabilities["config"] for config_req in serv_req["config"]):
                                logger.debug(
                                    "[StackHandler] _handle_create. Constraint solving. serv_req[config] '{0}' not in capabilities[config] '{1}'".format(
                                        serv_req["config"], capabilities["config"]))
                                potential_target = False
                                break
                        elif req == "count":
                            logger.debug(
                                "[StackHandler] _handle_create. Constraint solving. resolving count as individually named services")
                            new_sat = copy.deepcopy(stack_app_template)
                            new_service = copy.deepcopy(svc_doc)
                            del new_sat.services[service]
                            del new_service.extra_functional_dependencies["count"]
                            logger.debug(
                                "[StackHandler] _handle_create. Constraint solving. resolving count. Deleted original service group '{0}' results in new sat'{1}' and created new service params '{2}' ".format(
                                    service, new_sat, new_service))
                            for i in range(serv_req[req]):
                                new_sat.services.update({service + str(i): new_service})
                            logger.debug(
                                "[StackHandler] _handle_create. Constraint solving. new_sat with filled in service group {0}. Restarting loop".format(
                                    new_sat))
                            should_restart = True
                            break
                        elif req == "zone":
                            logger.debug("[StackHandler] _handle_create. Constraint solving. Adding zone req")
                            list_of_req_matching_zones.append((service, serv_req["zone"]))
                        elif req == "service":
                            logger.debug("[StackHandler] _handle_create. Constraint solving. Adding service req")
                            list_of_req_serv.append(serv_req["service"])
                        elif req in ["CPU", "RAM"]:
                            if not serv_req[req] <= capabilities[req]:
                                logger.debug(
                                    "[StackHandler] _handle_create. Constraint solving. not {0}{2} serv_req[req] <= {1}{2} capabilities[req]".format(
                                        serv_req[req], capabilities[req], req))
                                potential_target = False
                                break
                        else:  # ATM we just allow all other requirements
                            pass
                    if should_restart:
                        logger.debug(
                            "[StackHandler] _handle_create. Constraint solving. Should restart. Exiting for infr_target in stack_infr loop")
                        break
                    if potential_target:
                        logger.debug(
                            "[StackHandler] _handle_create. Constraint solving. For service '{0}' adding potential target '{1}'".format(
                                service, infr_target))
                        merged_app_infr[service].update({infr_target: capabilities})
                    else:
                        logger.debug(
                            "[StackHandler] _handle_create. Constraint solving. infr_target {0} NOT a potential target".format(
                                infr_target))
                if should_restart:
                    logger.debug(
                        "[StackHandler] _handle_create. Constraint solving. Should restart. Exiting for service in stack_app_template loop")
                    break

        logger.debug(
            "[StackHandler] _handle_create. Constraint solving. Per-service done. merged_app_infr '{0}'. list_of_req_serv '{1}'. list_of_req_matching_zones '{2}'".format(
                merged_app_infr, list_of_req_serv, list_of_req_matching_zones))
        # Now we check if the merge satisfies all services and cross-services dependencies as well
        merged_filtered_app_infr = self._filter_zones_req_application(list_of_req_matching_zones, merged_app_infr)
        logger.debug("[StackHandler] _handle_create. Constraint solving. merged_filtered_app_infr '{0}'".format(
            merged_filtered_app_infr))
        if isinstance(merged_filtered_app_infr, str):
            logger.debug(
                "[StackHandler] _handle_create. Constraint solving failed. String was returned '{0}'".format(
                    merged_filtered_app_infr))
            return (merged_filtered_app_infr, 400)
        if not all(False if merged_app_infr[service] == {} else True for service in list(merged_app_infr.keys())):
            logger.debug("[StackHandler] _handle_create. Constraint solving failed. service with no target")
            return "The given SIT cannot satisfy the SAT: there is an unsatisfied service with no infrastructure target", 400
        if not all(req_serv in list(merged_app_infr.keys()) for req_serv in list_of_req_serv):
            logger.debug(
                "[StackHandler] _handle_create. Constraint solving failed. service with unresolved service dependency")
            return "The given SIT cannot satisfy the SAT: there is an unsatisfied service with an unresolved service dependency", 400
        logger.debug(
            "[StackHandler] _handle_create. Constraint solving finished. merged_filtered_app_infr is realisible!'")
        return self._create_stack_instance(item, merged_filtered_app_infr), 200

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

    def _update_infr_capabilities(self, stack_infr_template, update="auto"):
        infr_targets = stack_infr_template.infrastructure_targets
        prev_infr_capabilities = stack_infr_template.infrastructure_capabilities

        if update is "no":
            logger.debug("[StackHandler] _update_infr_capabilities. update is '{0}', returning.".format(update))
            return stack_infr_template
        elif update is "auto":
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
