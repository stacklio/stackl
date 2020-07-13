import asyncio

from loguru import logger

from stackl.models.items.stack_instance_status_model import StackInstanceStatus


async def create_job_for_agent(stack_instance, action, document_manager,
                               redis):
    logger.debug(
        f"[AgentTaskBroker] create_job_for_agent. For stack_instance '{stack_instance}' and action '{action}'"
    )
    for service in stack_instance.services:
        service_name = service
        logger.debug(f"[AgentTaskBroker] service name: '{service_name}")
        service_doc = document_manager.get_document(type="service",
                                                    name=service_name)
        logger.debug(f"[AgentTaskBroker] service doc: '{service_doc}")

        # infrastructure target and agent are the same for each service, make sure we use the same agent for
        # each invocation of a service
        for fr in service_doc["functional_requirements"]:
            fr_doc = document_manager.get_functional_requirement(fr)
            fr_jobs = []
            for service_definition in stack_instance.services[service_name]:
                infrastructure_target = service_definition.infrastructure_target
                cloud_provider = service_definition.cloud_provider

                logger.debug(
                    f"[AgentTaskBroker] create_job_for_agent. Retrieved fr '{fr_doc}' from service_doc '{service_doc}'"
                )
                invoc = {}
                invoc['action'] = action
                invoc['functional_requirement'] = fr
                invoc['image'] = fr_doc.invocation[cloud_provider].image
                invoc['infrastructure_target'] = infrastructure_target
                invoc['stack_instance'] = stack_instance.name
                invoc['tool'] = fr_doc.invocation[cloud_provider].tool
                invoc['service'] = service_name

                logger.debug("Appending job")
                job = await redis.enqueue_job(
                    "invoke_automation",
                    invoc,
                    _queue_name=service_definition.agent)
                fr_jobs.append(asyncio.create_task(job.result(timeout=3600)))

                if fr_doc.invocation[cloud_provider].as_group:
                    logger.debug("running as group")
                    break

            for fr_job in asyncio.as_completed(fr_jobs):
                automation_result = await fr_job
                stack_instance_status = StackInstanceStatus()
                stack_instance_status.service = automation_result["service"]
                stack_instance_status.functional_requirement = automation_result[
                    "functional_requirement"]
                stack_instance_status.infrastructure_target = automation_result[
                    "infrastructure_target"]

                if 'error_message' in automation_result:
                    error_message = automation_result.error_message
                else:
                    error_message = ""

                stack_instance_status.status = automation_result["status"]
                stack_instance_status.error_message = error_message

                changed = False
                for i, status in enumerate(stack_instance.status):
                    if status.functional_requirement == automation_result[
                            "functional_requirement"] and status.infrastructure_target == automation_result[
                                "infrastructure_target"] and status.service == automation_result[
                                    "service"]:
                        stack_instance.status[i] = stack_instance_status
                        changed = True
                        break

                if not changed:
                    stack_instance.status.append(stack_instance_status)

                document_manager.write_stack_instance(stack_instance)
            logger.debug(f"tasks executed")
