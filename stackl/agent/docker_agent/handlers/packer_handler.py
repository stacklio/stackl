import os
import random
import string
import subprocess


class PackerHandler:

    def create_job_command(self, name, container_image, stack_instance, service):
        pass

    # TODO Implement this
    def create_delete_command(self, name, container_image, stack_instance, service):
        pass

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
            subprocess.check_output(command.split(' '), stderr=subprocess.STDOUT)
            return 0, "", None
        except subprocess.CalledProcessError as e:
            return 1, e.output.decode(), None
