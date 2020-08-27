import subprocess

from ..configurator_handler import ConfiguratorHandler
from ... import config


class TerraformHandler(ConfiguratorHandler):
    def create_job_command(self, name, container_image, stack_instance,
                           service):
        command_string = "docker run"
        command_string += " -e TF_VAR_stackl_stack_instance=" + stack_instance
        command_string += " -e TF_VAR_stackl_service=" + service
        command_string += " -e TF_VAR_stackl_host=" + config.settings.stackl_host
        command_string += " --name " + name
        command_string += " --network stackl_bridge"
        command_string += " " + container_image
        return command_string

    def create_delete_command(self, name, container_image, stack_instance,
                              service):
        command_string = "docker run"
        command_string += " -e TF_VAR_stackl_stack_instance=" + stack_instance
        command_string += " -e TF_VAR_stackl_service=" + service
        command_string += " -e TF_VAR_stackl_host=" + config.settings.stackl_host
        command_string += " --name " + name
        command_string += " --network stackl_bridge"
        command_string += " " + container_image
        command_string += " " + "/bin/sh -c 'terraform init -backend-config=address=" + config.settings.stackl_host +\
                          "/terraform/" + stack_instance + " && terraform destroy --auto-approve'"
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
            return 0, ""
        except subprocess.CalledProcessError as e:
            return 1, e.output.decode()
