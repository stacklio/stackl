import os
import random
import string
import subprocess

from configurator_handler import ConfiguratorHandler


class PackerHandler(ConfiguratorHandler):
    def create_job_command(self, name, container_image, stack_instance,
                           service):
        pass

    # TODO Implement this
    def create_delete_command(self, name, container_image, stack_instance,
                              service):
        pass

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
            subprocess.check_output(command.split(' '),
                                    stderr=subprocess.STDOUT)
            return 0, "", None
        except subprocess.CalledProcessError as e:
            return 1, e.output.decode(), None
