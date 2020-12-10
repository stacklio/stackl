"""
StackInstanceService model
"""
import re
from typing import Any, Dict, List

from pydantic import BaseModel
from redis import Redis

from core import config

# TODO get_redis in the future? doesnt work for now
redis =  Redis(host=config.settings.stackl_redis_host,
                      port=config.settings.stackl_redis_port,
                      password=config.settings.stackl_redis_password)
class StackInstanceService(BaseModel):
    """
    StackInstanceService model
    """
    infrastructure_target: str = None
    provisioning_parameters: Dict[str, Any] = None
    cloud_provider: str = "generic"
    secrets: Dict[str, Any] = None
    hosts: List[str] = None
    resources: Dict[str, str] = None
    service: str = None
    agent: str = ""
    opa_outputs: Dict[str, Any] = {}
    outputs: Dict[str, Any] = {}
    packages: List[str] = None
    tags: Dict[str, str] = None
    service: str = None

    def template_hosts(self, stackl_hostname, instances, infra_target_counter):
        """Templates the host field in a stack instance"""
        # Clear previous machine names
        self.hosts = []
        self.provisioning_parameters['machine_names'] = []
        counter_match = re.match(r'.*{ *counter\((\w+) *, *(\d+) *\) *}.*', stackl_hostname)
        if counter_match:
            variable_name = counter_match.group(1)
            default_counter = int(counter_match.group(2))
            if redis.get(variable_name):
                value = redis.incr(variable_name)
            else:
                value = redis.incr(variable_name, default_counter)
            stackl_hostname = re.sub(r'{ *counter\(\w+ *, \d+ *\) *}', str(value), stackl_hostname)
        if instances:
            for i in range(self.provisioning_parameters["instances"]):
                replaced_hostname = stackl_hostname \
                    .replace('{ri}', "{:02d}".format(infra_target_counter)) \
                    .replace('{hi}', "{:02d}".format(i + 1))
                self.hosts.append(replaced_hostname)
                self.provisioning_parameters['machine_names'].append(
                    replaced_hostname)
        else:
            replaced_hostname = stackl_hostname \
                .replace('{ri}', "{:02d}".format(infra_target_counter)) \
                .replace('{hi}', "01")
            self.hosts.append(replaced_hostname)
            self.provisioning_parameters['machine_names'].append(
                replaced_hostname)
