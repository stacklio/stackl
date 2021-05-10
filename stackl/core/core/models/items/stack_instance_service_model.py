"""
StackInstanceService model
"""
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from redis import Redis

from core import config

# TODO get_redis in the future? doesnt work for now
redis = Redis(host=config.settings.stackl_redis_host,
              port=config.settings.stackl_redis_port,
              password=config.settings.stackl_redis_password)


class StackInstanceService(BaseModel):
    """
    StackInstanceService model
    """
    infrastructure_target: str = ""
    provisioning_parameters: Dict[str, Any] = {}
    cloud_provider: str = "generic"
    secrets: Dict[str, Any] = {}
    hosts: Optional[List[str]] = []
    resources: Dict[str, str] = {}
    service: str = ""
    agent: str = ""
    opa_outputs: Dict[str, Any] = {}
    outputs: Dict[str, Any] = {}
    packages: List[str] = []
    tags: Dict[str, str] = {}
    service: str = ""

    def template_hosts(self, stackl_hostname, instances, infra_target_counter):
        """Templates the host field in a stack instance"""
        # Clear previous machine names
        if not self.hosts:
            self.hosts = []
        if instances is None:
            instances = 1
        if not len(self.hosts) == instances:
            counter_match = re.match(r'.*{ *counter\((\w+) *, *(\d+) *\) *}.*',
                                     stackl_hostname)
            new_instances = instances - len(self.hosts)
            for i in range(len(self.hosts), new_instances):
                replaced_hostname = stackl_hostname
                if counter_match:
                    variable_name = counter_match.group(1)
                    default_counter = int(counter_match.group(2))
                    if redis.get(variable_name):
                        value = redis.incr(variable_name)
                    else:
                        value = redis.incr(variable_name, default_counter)
                    replaced_hostname = re.sub(r'{ *counter\(\w+ *, \d+ *\) *}',
                                             str(value), stackl_hostname)
                replaced_hostname = replaced_hostname \
                    .replace('{ri}', "{:02d}".format(infra_target_counter)) \
                    .replace('{hi}', "{:02d}".format(i + 1))
                self.hosts.append(replaced_hostname)
        self.provisioning_parameters['machine_names'] = self.hosts
        if "opa_bmv_vm_name" in self.opa_outputs and "opa_vmnameliteral" in self.opa_outputs:
            machine_name = self.hosts[0].split(".")
            self.provisioning_parameters['bmv_vm_name'] = machine_name[0]
            self.provisioning_parameters['vmnameliteral'] = machine_name[0]