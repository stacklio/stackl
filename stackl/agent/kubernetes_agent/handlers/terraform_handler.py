import os
import random
import string
import time

import kubernetes.client
import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class TerraformHandler:
    def __init__(self):
        config.load_incluster_config()
        self.configuration = kubernetes.client.Configuration()
        self.api_instance = kubernetes.client.BatchV1Api(kubernetes.client.ApiClient(self.configuration))
        self.api_instance_core = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(self.configuration))

    def create_job_object(self, name, container_image, stack_instance, service, namespace="stackl",
                          container_name="jobcontainer"):
        body = client.V1Job(api_version="batch/v1", kind="Job")
        body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        body.status = client.V1JobStatus()
        template = client.V1PodTemplate()
        template.template = client.V1PodTemplateSpec()
        env_list = [client.V1EnvVar(name="TF_VAR_stackl_stack_instance", value=stack_instance),
                    client.V1EnvVar(name="TF_VAR_stackl_service", value=service),
                    client.V1EnvVar(name="TF_VAR_stackl_host", value=os.environ['stackl_host'])]
        container = client.V1Container(name=container_name, image=container_image, env=env_list,
                                       command=["/bin/sh", "-c"],
                                       args=["terraform init -backend-config=address=http://"
                                             + os.environ['stackl_host']
                                             + "/terraform/" + stack_instance +
                                             " && terraform apply --auto-approve"])
        secrets = [client.V1LocalObjectReference(name="dome-nexus")]
        template.template.spec = client.V1PodSpec(containers=[container], restart_policy='Never',
                                                  image_pull_secrets=secrets)
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600, template=template.template, backoff_limit=1)
        return body

    def delete_job_object(self, name, container_image, stack_instance, service, namespace="stackl",
                          container_name="jobcontainer"):
        body = client.V1Job(api_version="batch/v1", kind="Job")
        body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        body.status = client.V1JobStatus()
        template = client.V1PodTemplate()
        template.template = client.V1PodTemplateSpec()
        env_list = [client.V1EnvVar(name="TF_VAR_stackl_stack_instance", value=stack_instance),
                    client.V1EnvVar(name="TF_VAR_stackl_service", value=service),
                    client.V1EnvVar(name="TF_VAR_stackl_host", value=os.environ['stackl_host'])]
        container = client.V1Container(name=container_name, image=container_image, env=env_list,
                                       command=["/bin/sh", "-c"],
                                       args=["terraform init -backend-config=address=http://"
                                             + os.environ['stackl_host']
                                             + "/terraform/" + stack_instance +
                                             " && terraform destroy --auto-approve"])
        secrets = [client.V1LocalObjectReference(name="dome-nexus")]
        template.template.spec = client.V1PodSpec(containers=[container], restart_policy='Never',
                                                  image_pull_secrets=secrets)
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600, template=template.template, backoff_limit=1)
        return body

    def id_generator(self, size=12, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def wait_for_job(self, job_name, namespace):
        ready = False
        api_response = None
        while not ready:
            time.sleep(5)
            print("check status")
            api_response = self.api_instance.read_namespaced_job(job_name, namespace)
            print(api_response)
            if api_response.status.failed is not None or api_response.status.succeeded is not None:
                ready = True
        return api_response

    def get_hosts(self, stack_instance):
        # Get the statefile
        r = requests.get('http://' + os.environ['stackl_host'] + '/terraform/' + stack_instance)
        statefile = r.json()
        return statefile["outputs"]["hosts"]["value"]

    def handle(self, invocation, action):
        print(invocation)
        stackl_namespace = os.environ['stackl_namespace']
        container_image = invocation.image
        name = "stackl-job-" + self.id_generator()
        if action == "create" or action == "update":
            body = self.create_job_object(name, container_image, invocation.stack_instance, invocation.service,
                                          namespace=stackl_namespace)
        else:
            body = self.delete_job_object(name, container_image, invocation.stack_instance, invocation.service,
                                          namespace=stackl_namespace)
        try:
            api_response = self.api_instance.create_namespaced_job(stackl_namespace, body, pretty=True)
            print(api_response)
        except ApiException as e:
            print("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)
        api_response = self.wait_for_job(name, stackl_namespace)
        if api_response.status.succeeded == 1:
            print("job succeeded")
            return 0, "", self.get_hosts(invocation.stack_instance)
        else:
            return 1, "Still need proper output", None
