import os
import random
import string
import subprocess
import requests

from configurator_handler import ConfiguratorHandler


class TerraformHandler(ConfiguratorHandler):
    def create_job_command(self, name, container_image, stack_instance,
                           service):
        command_string = "docker run"
        command_string += " -e TF_VAR_stackl_stack_instance=" + stack_instance
        command_string += " -e TF_VAR_stackl_service=" + service
        command_string += " -e TF_VAR_stackl_host=" + os.environ['STACKL_HOST']
        command_string += " --name " + name
        command_string += " --network stackl_bridge"
        command_string += " " + container_image
        return command_string

    def create_delete_command(self, name, container_image, stack_instance,
                              service):
        command_string = "docker run"
        command_string += " -e TF_VAR_stackl_stack_instance=" + stack_instance
        command_string += " -e TF_VAR_stackl_service=" + service
        command_string += " -e TF_VAR_stackl_host=" + os.environ['STACKL_HOST']
        command_string += " --name " + name
        command_string += " --network stackl_bridge"
        command_string += " " + container_image
        command_string += " " + "/bin/sh -c 'terraform init -backend-config=address=http://" + os.environ[
            'STACKL_HOST'] + "/terraform/" + stack_instance + " && terraform destroy --auto-approve'"
        return command_string

    def handle(self, invocation, action):
        print(invocation)
        container_image = invocation.image
        name = "stackl-job-" + self.id_generator()
        if action == "create" or action == "update":
            command = self.create_job_command(name, container_image,
                                              invocation.stack_instance,
                                              invocation.service)
        else:
            command = self.create_delete_command(name, container_image,
                                                 invocation.stack_instance,
                                                 invocation.service)
        print("running command: " + command)
        try:
            subprocess.check_output(command,
                                    shell=True,
                                    stderr=subprocess.STDOUT)
            return 0, "", self._get_hosts(invocation.stack_instance)
        except subprocess.CalledProcessError as e:
            return 1, e.output.decode(), None

    def _get_hosts(self, stack_instance):
        # Get the statefile
        r = requests.get('http://' + os.environ['STACKL_HOST'] +
                         '/terraform/' + stack_instance)
        statefile = r.json()
        return statefile["outputs"]["hosts"]["value"]
