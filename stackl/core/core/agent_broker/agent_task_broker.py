"""
Module for handling the delivery and results of automation jobs
"""

import asyncio

from loguru import logger

from core import config
from core.handler.stack_handler import delete_services
from core.manager.stackl_manager import get_snapshot_manager, get_document_manager
from core.models.items.stack_instance_model import StackInstance
from core.opa_broker.opa_broker_factory import OPABrokerFactory


async def create_service(action, redis, stack_instance, to_be_deleted,
                         force_delete, service_name, service, index):
    opa_broker_factory = OPABrokerFactory()
    opa_broker = opa_broker_factory.get_opa_broker()
    success = True
    document_manager = get_document_manager()
    service_doc = document_manager.get_service(service_name)

    if service_doc.service_policies:
        logger.debug(f"Evaluating service policies: {service_doc.service_policies}")
        for svc_policy in service_doc.service_policies:
            logger.debug(f"Evaluating service policy: {svc_policy}")
            opa_data = {}
            opa_data['inputs'] = svc_policy['inputs']
            opa_data['functional_requirements'] = service_doc.functional_requirements
            opa_data['infrastructure_target'] = service.infrastructure_target
            opa_data['service'] = service_name
            opa_data['stack_instance'] = stack_instance.dict()
            policy = document_manager.get_policy_template(svc_policy['name'])
            # Make sure the policy is in OPA
            opa_broker.add_policy(policy.name, policy.policy)
            opa_result = opa_broker.ask_opa_policy_decision(
                        svc_policy['name'], "filter", opa_data)
            logger.debug(f"OPA result for service policy {svc_policy}: {opa_result}")
            functional_requirements = opa_result['result']
    else:
        functional_requirements = service_doc.functional_requirements
    if action == "delete":
        functional_requirements = reversed(functional_requirements)
    for fr in functional_requirements:
        stack_instance = document_manager.get_stack_instance(stack_instance.name)
        service = stack_instance.services[service_name][index]
        logger.debug(
            f"Debug for service'{service}'")
        fr_doc = document_manager.get_functional_requirement(fr)
        fr_jobs = []
        infrastructure_target = service.infrastructure_target
        cloud_provider = service.cloud_provider
        logger.debug(
            f"Retrieved fr '{fr_doc}' from service_doc '{service_doc}'")
        invoc = {}
        invoc['action'] = action
        invoc['functional_requirement'] = fr
        if cloud_provider in fr_doc.invocation:
            pass
        elif "generic" in fr_doc.invocation:
            cloud_provider = "generic"
        else:
            automation_result = {}
            automation_result["functional_requirement"] = fr
            automation_result["infrastructure_target"] = infrastructure_target
            automation_result["service"] = service_name
            automation_result["error_message"] = "No cloud provider for this invocation"
            automation_result["status"] = "Failed"
            await update_status(automation_result, stack_instance, action,
                                to_be_deleted)
            return False
        invoc['image'] = fr_doc.invocation[cloud_provider].image
        invoc['before_command'] = fr_doc.invocation[
            cloud_provider].before_command
        invoc['infrastructure_target'] = infrastructure_target
        invoc['stack_instance'] = stack_instance.name
        tool = fr_doc.invocation[cloud_provider].tool
        invoc['tool'] = tool
        if tool.lower() == "ansible":
            if fr_doc.invocation[cloud_provider].playbook_path is not None:
                invoc['playbook_path'] = fr_doc.invocation[
                    cloud_provider].playbook_path
            if fr_doc.invocation[cloud_provider].serial:
                invoc['serial'] = fr_doc.invocation[cloud_provider].serial
            if fr_doc.invocation[cloud_provider].ansible_role:
                invoc['ansible_role'] = fr_doc.invocation[cloud_provider].ansible_role
            if fr_doc.invocation[cloud_provider].connection:
                invoc['connection'] = fr_doc.invocation[cloud_provider].connection
            if fr_doc.invocation[cloud_provider].wait_for_port:
                invoc['wait_for_port'] = fr_doc.invocation[cloud_provider].wait_for_port
            invoc['gather_facts'] = fr_doc.invocation[cloud_provider].gather_facts
        invoc['service'] = service_name
        invoc["hosts"] = service.hosts
        logger.debug("Appending job")
        job = await redis.enqueue_job("invoke_automation",
                                      invoc,
                                      _queue_name=service.agent)
        fr_jobs.append(asyncio.create_task(job.result(timeout=7200)))
        if fr_doc.as_group:
            logger.debug("running as group")
            break
        for fr_job in asyncio.as_completed(fr_jobs):
            automation_result = await fr_job
            await update_status(automation_result, stack_instance, action,
                                to_be_deleted)
            if automation_result["status"] == "FAILED":
                success = False
        if not force_delete and not success:
            logger.debug("Not all fr's succeeded, stopping execution")
            break
        logger.debug("tasks executed")
    return success


async def create_job_for_agent(stack_instance,
                               action,
                               redis,
                               first_run=True,
                               force_delete=False):
    """creates jobs and puts them on the right agent queue"""
    logger.debug(
        f"For stack_instance '{stack_instance}' and action '{action}'")

    success = await create_job_per_service(stack_instance.services, action,
                                           redis, stack_instance, force_delete)

    document_manager = get_document_manager()
    if action == "delete" and (success or force_delete):
        document_manager.delete_stack_instance(stack_instance.name)
    elif not success and first_run and config.settings.rollback_enabled:
        snapshot_document = get_snapshot_manager().restore_latest_snapshot(
            "stack_instance", stack_instance.name)
        stack_instance = StackInstance.parse_obj(snapshot_document["snapshot"])
        await create_job_for_agent(stack_instance,
                                   action,
                                   redis,
                                   first_run=False)


async def create_job_per_service(services,
                                 action,
                                 redis,
                                 stack_instance,
                                 to_be_deleted=None,
                                 force_delete=False):
    success = True
    stage_jobs = []
    # do stages
    if stack_instance.stages:
        for stage in stack_instance.stages:
            for service_name in stage.services:
                for idx, service in enumerate(stack_instance.services[service_name]):
                    success = create_service(action, redis, stack_instance,
                                             to_be_deleted, force_delete,
                                             service_name, service, idx)
                    stage_jobs.append(asyncio.create_task(success))

            await asyncio.gather(*stage_jobs)
            stage_jobs = []

    # not using stages
    else:
        for service_name, service_list in services.items():
            for idx, service in enumerate(service_list):
                success = await create_service(action, redis, stack_instance,
                                               to_be_deleted, force_delete,
                                               service_name, service, idx)

    return success


async def update_status(automation_result,
                        stack_instance,
                        action,
                        to_be_deleted=None):
    """Updates the status of a functional requirement in a stack instance"""
    document_manager = get_document_manager()
    stack_instance = document_manager.get_stack_instance(stack_instance.name)
    status_to_be_deleted = None
    for status in stack_instance.status:
        if status.functional_requirement == automation_result[
            "functional_requirement"] and automation_result[
            "infrastructure_target"] in status.infrastructure_target \
                and status.service == automation_result["service"]:
            status.service = automation_result["service"]
            status.functional_requirement = automation_result[
                "functional_requirement"]
            if 'error_message' in automation_result:
                error_message = automation_result["error_message"]
            else:
                error_message = ""
            if action == "delete" and automation_result["status"] == "READY":
                status_to_be_deleted = status
            status.status = automation_result["status"]
            status.error_message = error_message
            break

    if action == "delete":
        if status_to_be_deleted:
            stack_instance.status.remove(status_to_be_deleted)
        if to_be_deleted:
            delete_services(to_be_deleted, stack_instance)

    document_manager.write_stack_instance(stack_instance)
