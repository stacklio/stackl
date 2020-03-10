import json
import os
import random
import string
import time

import kubernetes.client
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class AnsibleHandler:
    def __init__(self):
        config.load_incluster_config()
        self.configuration = kubernetes.client.Configuration()
        self.api_instance = kubernetes.client.BatchV1Api(kubernetes.client.ApiClient(self.configuration))
        self.api_instance_core = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(self.configuration))

    def create_config_map(self, name, namespace, stack_instance):
        cm = client.V1ConfigMap()
        cm.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        cm.data = {"stackl.yml": json.dumps({"plugin": "stackl", "host": "http://" + os.environ['stackl_host'],
                                             "stack_instance": stack_instance})}
        return cm

    def create_job_object(self, name, container_image, stack_instance, service, namespace="stackl",
                          container_name="jobcontainer"):
        body = client.V1Job(api_version="batch/v1", kind="Job")
        body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        body.status = client.V1JobStatus()
        template = client.V1PodTemplate()
        template.template = client.V1PodTemplateSpec()
        volumes = []
        vol = client.V1Volume(name="inventory")
        inventory_config_map = client.V1ConfigMapVolumeSource()
        inventory_config_map.name = name
        vol.config_map = inventory_config_map

        volume_mounts = []
        volume_mount = client.V1VolumeMount(name="inventory", mount_path="/ansible/playbooks/inventory/stackl.yml",
                                            sub_path="stackl.yml")
        volume_mounts.append(volume_mount)

        volumes.append(vol)
        env_list = [client.V1EnvVar(name="ANSIBLE_INVENTORY_PLUGINS", value="/ansible/playbooks")]
        container = client.V1Container(name=container_name, image=container_image, env=env_list,
                                       image_pull_policy="Always",
                                       volume_mounts=volume_mounts,
                                       command=["ansible-playbook"],
                                       args=["main.yml", "-i", "inventory/stackl.yml", "-e",
                                             "stackl_stack_instance=" + stack_instance,
                                             "-e", "stackl_service=" + service, "-e",
                                             "stackl_host=" + os.environ['stackl_host']])
        secrets = [client.V1LocalObjectReference(name="dome-nexus")]
        template.template.spec = client.V1PodSpec(containers=[container], restart_policy='Never',
                                                  image_pull_secrets=secrets, volumes=volumes)
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600, template=template.template, backoff_limit=1)
        return body

    def delete_job_object(self, name, container_image, stack_instance, service, namespace="stackl",
                          container_name="jobcontainer"):
        body = client.V1Job(api_version="batch/v1", kind="Job")
        body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        body.status = client.V1JobStatus()
        template = client.V1PodTemplate()
        template.template = client.V1PodTemplateSpec()
        volumes = []
        vol = client.V1Volume(name="inventory")
        inventory_config_map = client.V1ConfigMapVolumeSource()
        inventory_config_map.name = name
        vol.config_map = inventory_config_map

        volume_mounts = []
        volume_mount = client.V1VolumeMount(name="inventory", mount_path="/ansible/playbooks/inventory/stackl.yml",
                                            sub_path="stackl.yml")
        volume_mounts.append(volume_mount)

        volumes.append(vol)
        env_list = [client.V1EnvVar(name="ANSIBLE_INVENTORY_PLUGINS", value="/ansible/playbooks")]
        container = client.V1Container(name=container_name, image=container_image, env=env_list,
                                       volume_mounts=volume_mounts,
                                       command=["ansible-playbook"],
                                       args=["main.yml", "-i", "inventory/stackl.yml",
                                             "-e", "stackl_stack_instance=" + stack_instance,
                                             "-e", "stackl_service=" + service,
                                             "-e", "stackl_host=" + os.environ['stackl_host'],
                                             "-e", "state=absent"])
        secrets = [client.V1LocalObjectReference(name="dome-nexus")]
        template.template.spec = client.V1PodSpec(containers=[container], restart_policy='Never',
                                                  image_pull_secrets=secrets, volumes=volumes)
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600, template=template.template, backoff_limit=1)
        return body

    def id_generator(self, size=12, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def wait_for_job(self, job_name, namespace):
        ready = False
        api_response = None
        while not ready:
            time.sleep(5)
            api_response = self.api_instance.read_namespaced_job(job_name, namespace)
            if api_response.status.failed != 0 or api_response.status.succeeded != 0:
                ready = True
        return api_response

    def handle(self, invocation, action):
        print(invocation)
        stackl_namespace = os.environ['stackl_namespace']
        container_image = invocation.image
        name = "stackl-job-" + self.id_generator()
        print("create cm")
        config_map = self.create_config_map(name, stackl_namespace, invocation.stack_instance)
        if action == "create" or action == "update":
            print("create object")
            body = self.create_job_object(name, container_image, invocation.stack_instance, invocation.service,
                                          namespace=stackl_namespace)
        else:
            body = self.delete_job_object(name, container_image, invocation.stack_instance, invocation.service,
                                          namespace=stackl_namespace)
        try:
            api_response = self.api_instance_core.create_namespaced_config_map(stackl_namespace, config_map)
            print(api_response)
            api_response = self.api_instance.create_namespaced_job(stackl_namespace, body, pretty=True)
            print(api_response)
        except ApiException as e:
            print("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)
        api_response = self.wait_for_job(name, stackl_namespace)
        if api_response.status.failed == 1:
            return 1, "Still need proper output", None
        else:
            return 0, "", None
