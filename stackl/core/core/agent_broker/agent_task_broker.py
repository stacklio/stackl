"""
Module for handling the delivery and results of automation jobs
"""

import asyncio

from loguru import logger

from core import config
from core.handler.stack_handler import delete_services
from core.manager.stackl_manager import get_snapshot_manager
from core.models.items.stack_instance_model import StackInstance


async def create_job_for_agent(stack_instance,
                               action,
                               document_manager,
                               redis,
                               first_run=True,
                               force_delete=False):
    """creates jobs and puts them on the right agent queue"""
    logger.debug(
        f"For stack_instance '{stack_instance}' and action '{action}'")

    success = True
    success = await create_job_per_service(stack_instance.services,
                                           document_manager, action, redis,
                                           stack_instance)

    if action == "delete" and (success or force_delete):
        document_manager.delete_stack_instance(stack_instance.name)
    elif not success and first_run and config.settings.rollback_enabled:
        snapshot_document = get_snapshot_manager().restore_latest_snapshot(
            "stack_instance", stack_instance.name)
        stack_instance = StackInstance.parse_obj(snapshot_document["snapshot"])
        await create_job_for_agent(stack_instance,
                                   action,
                                   document_manager,
                                   redis,
                                   first_run=False)


async def create_job_per_service(services,
                                 document_manager,
                                 action,
                                 redis,
                                 stack_instance,
                                 to_be_deleted=None):
    success = True
    for service_name, service_list in services.items():
        for service in service_list:
            service_doc = document_manager.get_document(type="service",
                                                        name=service.service)

            functional_requirements = service_doc["functional_requirements"]
            if action == "delete":
                functional_requirements = reversed(functional_requirements)

            for fr in functional_requirements:
                fr_doc = document_manager.get_functional_requirement(fr)
                fr_jobs = []
                infrastructure_target = service.infrastructure_target
                cloud_provider = service.cloud_provider

                logger.debug(
                    f"Retrieved fr '{fr_doc}' from service_doc '{service_doc}'"
                )

                invoc = {}
                invoc['action'] = action
                invoc['functional_requirement'] = fr
                invoc['image'] = fr_doc.invocation[cloud_provider].image
                invoc['before_command'] = fr_doc.invocation[
                    cloud_provider].before_command
                invoc['infrastructure_target'] = infrastructure_target
                invoc['stack_instance'] = stack_instance.name
                invoc['create_command'] = fr_doc.invocation[
                    cloud_provider].create_command
                invoc['delete_command'] = fr_doc.invocation[
                    cloud_provider].delete_command
                invoc['create_command_args'] = fr_doc.invocation[
                    cloud_provider].create_command_args
                invoc['delete_command_args'] = fr_doc.invocation[
                    cloud_provider].delete_command_args

                tool = fr_doc.invocation[cloud_provider].tool
                invoc['tool'] = tool
                if tool.lower() == "ansible":
                    if fr_doc.invocation[
                            cloud_provider].playbook_path is not None:
                        invoc['playbook_path'] = fr_doc.invocation[
                            cloud_provider].playbook_path
                    if fr_doc.invocation[cloud_provider].serial is not None:
                        invoc['serial'] = fr_doc.invocation[
                            cloud_provider].serial

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
                    await update_status(automation_result, document_manager,
                                        stack_instance, action, to_be_deleted)
                    if automation_result["status"] == "FAILED":
                        success = False

                if not success:
                    logger.debug("Not all fr's succeeded, stopping execution")
                    break

                logger.debug("tasks executed")

    return success


async def update_status(automation_result,
                        document_manager,
                        stack_instance,
                        action,
                        to_be_deleted=None):
    """Updates the status of a functional requirement in a stack instance"""
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
