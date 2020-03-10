import os
import random
import string
import subprocess


class AnsibleHandler:

    def create_job_command(self, name, container_image, stack_instance, service):
        with open('/tmp/stackl.yml', 'w') as inventory:
            inventory.write(
                'plugin: stackl\nhost: http://' + os.environ['STACKL_HOST'] + '\nstack_instance: ' + stack_instance)
        command_string = "docker run"
        command_string += " --name " + name
        command_string += " --network stackl_bridge"
        command_string += " -v /tmp/stackl.yml:/ansible/playbooks/stackl.yml"
        command_string += " -e ANSIBLE_INVENTORY_PLUGINS=/ansible/playbooks"
        command_string += " " + container_image
        command_string += " ansible-playbook main.yml -i stackl.yml"
        command_string += " -e stackl_stack_instance=" + stack_instance
        command_string += " -e stackl_service=" + service
        command_string += " -e stackl_host=" + os.environ['STACKL_HOST']
        return command_string

    # TODO Implement this
    def create_delete_command(self, name, container_image, stack_instance, service):
        command_string = "docker run"
        command_string += " --name " + name
        command_string += " --network stackl_bridge"
        command_string += " -v /tmp/stackl.yml:/tmp/stackl.yml"
        command_string += " " + container_image
        command_string += " echo delete not yet supported"
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
            subprocess.check_output(command.split(' '), stderr=subprocess.STDOUT)
            return 0, "", None
        except subprocess.CalledProcessError as e:
            return 1, e.output.decode(), None
