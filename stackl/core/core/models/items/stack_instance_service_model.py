"""
StackInstanceService model
"""
from typing import Dict, Any, List

from pydantic import BaseModel  # pylint: disable=E0611 #error in pylint


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
        if instances:
            for i in range(self.provisioning_parameters["instances"]):
                replaced_hostname = stackl_hostname \
                    .replace('{ri}', "{:02d}".format(infra_target_counter)) \
                    .replace('{hi}', "{:02d}".format(i + 1))
                self.hosts.append(replaced_hostname)
                self.provisioning_parameters['machine_names'].append(replaced_hostname)
        else:
            replaced_hostname = stackl_hostname \
                .replace('{ri}', "{:02d}".format(infra_target_counter)) \
                .replace('{hi}', "01")
            self.hosts.append(replaced_hostname)
            self.provisioning_parameters['machine_names'].append(replaced_hostname)
