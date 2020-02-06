import os
import random
import string
import subprocess


class TerraformHandler:

    def create_job_command(self, name, container_image, stack_instance, service):
        command_string = "docker run"
        command_string += " -e TF_VAR_stackl_stack_instance=" + stack_instance
        command_string += " -e TF_VAR_stackl_service=" + service
        command_string += " -e TF_VAR_stackl_host=" + os.environ['STACKL_HOST']
        command_string += " --name " + name
        command_string += " --network stackl_bridge"
        command_string += " " + container_image
        return command_string

    def create_delete_command(self, name, container_image, stack_instance, service):
        command_string = "docker run"
        command_string += " -e TF_VAR_stackl_stack_instance=" + stack_instance
        command_string += " -e TF_VAR_stackl_service=" + service
        command_string += " -e TF_VAR_stackl_host=" + os.environ['STACKL_HOST']
        command_string += " --name " + name
        command_string += " --network stackl_bridge"
        command_string += " " + container_image
        command_string += " " + "destroy --auto-approve"
        return command_string

    def id_generator(self, size=12, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def handle(self, invocation, action):
        print(invocation)
        container_image = invocation.image
        name = "stackl-job-" + self.id_generator()
        if action == "create" or action == "update":
            command = self.create_job_command(name, container_image, invocation.stack_instance, invocation.service)
        else:
            command = self.create_delete_command(name, container_image, invocation.stack_instance, invocation.service)
        print("running command: " + command)
        try:
            subprocess.check_output(command.split(' '))
            return 0, ""
        except subprocess.CalledProcessError as e:
            return 1, e.output
