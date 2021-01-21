"""
StackInstanceService model
"""
import re
from typing import Any, Dict, List

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
        print(f"stackl_hostname: {stackl_hostname}")
        print(f"instances: {instances}")
        print(f"infra_target_counter: {infra_target_counter}")
        print(f"self.hosts: {self.hosts}")
        print(f"self.provisioning_parameters: {self.provisioning_parameters}")
        print(f"self: {self}")
        # stackl_hostname: testje-{hi}
        # instances: 1
        # infra_target_counter: 1
        # self.hosts: ['testje-02']
        # self.provisioning_parameters: {'environment': 'development', 'domain_letters': 'dev', 'ansible_connection': 'local', 'namespace': 'old-stack-instance', 'infoblox_enabled': False, 'istio_enabled': False, 'hostname': 'postgres', 'app': 'postgres', 'microservice_port': 5432, 'image_name': 'nexus-dockerext.dome.dev/postgres', 'image_tag': 'latest', 'stackl_hostname': 'testje-{hi}', 'instances': 1, 'env': {'POSTGRES_PASSWORD': 'demo-password'}, 'livenessprobe_path': '', 'readinessprobe_path': ''}
        # Clear previous machine names
        # self: infrastructure_target='development.nossegem.k8s' provisioning_parameters={'environment': 'development', 'domain_letters': 'dev', 'ansible_connection': 'local', 'namespace': 'old-stack-instance', 'infoblox_enabled': False, 'istio_enabled': False, 'hostname': 'postgres', 'app': 'postgres', 'microservice_port': 5432, 'image_name': 'nexus-dockerext.dome.dev/postgres', 'image_tag': 'latest', 'stackl_hostname': 'testje-{hi}', 'instances': 2, 'env': {'POSTGRES_PASSWORD': 'demo-password'}, 'livenessprobe_path': '', 'readinessprobe_path': ''} cloud_provider='generic' secrets=None hosts=None resources=None service='postgres' agent='' opa_outputs=defaultdict(<function tree at 0x7fa17e37bd90>, {}) outputs={} packages=None tags=None
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
