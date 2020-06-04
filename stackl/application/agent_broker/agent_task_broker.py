import json
import logging

from redis import StrictRedis

logger = logging.getLogger("STACKL_LOGGER")


class AgentTaskBroker:
    def __init__(self, redis: StrictRedis):
        self.redis = redis

    def get_agent_for_job(self, target):
        agents = self._get_agents()
        for agent, selector in agents.items():
            targets = target.split('.')
            agent_targets = selector.split('.')
            if targets[0] != agent_targets[0] and agent_targets[0] != "*":
                continue
            if targets[1] != agent_targets[1] and agent_targets[1] != "*":
                continue
            if targets[2] != agent_targets[2] and agent_targets[2] != "*":
                continue
            logger.debug(
                f"[AgentBroker] found agent for target {target}: {agent}")
            return agent
        # If no agents are available for this job right now we put it on agent_unavailable
        return "agent_unavailable"

    def create_job_for_agent(self, stack_instance, action, document_manager):
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
            infrastructure_target = stack_instance.services[
                service_name].infrastructure_target
            agent = self.get_agent_for_job(infrastructure_target)
            for fr in service_doc["functional_requirements"]:
                fr_doc = document_manager.get_document(
                    type="functional_requirement", name=fr)
                logger.debug(
                    f"[AgentTaskBroker] create_job_for_agent. Retrieved fr '{fr_doc}' from service_doc '{service_doc}'"
                )
                invoc = {}
                invoc['action'] = action
                invoc['functional_requirement'] = fr
                invoc['image'] = fr_doc['invocation']['image']
                invoc['infrastructure_target'] = infrastructure_target
                invoc['stack_instance'] = stack_instance.name
                invoc['tool'] = fr_doc['invocation']['tool']
                invoc['service'] = service_name

                self.redis.publish(agent, json.dumps(invoc))

    def _get_agents(self):
        agents = {}
        for key in self.redis.scan_iter('agents/*'):
            logger.debug(f"key {key}")
            agents[key.decode("utf-8").split('/')[1]] = self.redis.get(
                key).decode("utf-8")
        return agents
