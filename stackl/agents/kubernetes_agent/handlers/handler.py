import json
import os
import random
import string
import time

import kubernetes.client
import stackl_client
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

vault_agent_config = """
exit_after_auth = false
pid_file = "/home/vault/pidfile"
auto_auth {
    method "kubernetes" {
        mount_path = "auth/kubernetes"
        config = {
            role = "stackl"
        }
    }
    sink "file" {
        config = {
            path = "/home/vault/.vault-token"
        }
    }
}

template {
  content = "{0}"
  destination = "{1}"
}
"""


class Handler:

    def __init__(self):
        with open('/etc/stackl-agent/stackl-agent-config.yaml') as file:
            self.stackl_configuration = yaml.load(file, Loader=yaml.FullLoader)
            print(self.stackl_configuration)
        config.load_incluster_config()
        self.configuration = kubernetes.client.Configuration()
        self.api_instance = kubernetes.client.BatchV1Api(kubernetes.client.ApiClient(self.configuration))
        self.api_instance_core = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(self.configuration))
        configuration = stackl_client.Configuration()
        configuration.host = "http://" + os.environ['stackl_host']
        api_client = stackl_client.ApiClient(configuration=configuration)
        self.stack_instance_api = stackl_client.StackInstancesApi(api_client=api_client)

    def create_variables_cm(self, name, namespace, stack_instance, service, variables_config):
        cm = client.V1ConfigMap()
        cm.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        stack_instance = self.stack_instance_api.get_stack_instance(stack_instance)
        variables = {}
        for key, value in stack_instance.services[service].provisioning_parameters.items():
            variables[key] = value
        if variables_config["format"] == "json":
            cm.data = {variables_config["filename"]: json.dumps(variables)}
        return cm

    def create_agent_cm(self, name, namespace, cm_data):
        cm = client.V1ConfigMap()
        cm.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        cm.data = {"vault-agent-config.hcl": cm_data}

    def create_job_object(self, name, container_image, stack_instance, service, cmd, args, namespace="stackl",
                          container_name="jobcontainer", pull_secrets=[]):
        body = self.create_kubernetes_job(args, cmd, container_image, container_name, name, namespace, pull_secrets)
        return body

    def add_vault_agent_init_container(self, body: client.V1Job, vault_config):
        vault_agent_env_list = [client.V1EnvVar(name="VAULT_ADDR", value=vault_config["address"])]

        templated_vault_config = vault_agent_config.format(vault_config["content"], vault_config["destination"])
        cm = self.create_agent_cm(body.metadata.name + "-vault-agent", body.metadata.namespace, templated_vault_config)

        volumes = []

        vault_variables_vol = client.V1Volume(name="vault-variables")
        empty_dir = client.V1EmptyDirVolumeSource()
        empty_dir.medium = "Memory"

        vault_config_map = client.V1ConfigMapVolumeSource()
        vault_config_map.name = cm.metadata.name
        vol_vault_config = client.V1Volume(name="vault-config")
        vol_vault_config.config_map = vault_config_map

        volume_mounts = []

        volume_vault_config_mount = client.V1VolumeMount(name="vault-config", mount_path="/etc/vault-config")
        volume_vault_variables_mount = client.V1VolumeMount(name="vault-variables", mount_path="/etc/vault-variables")

        volume_mounts.extend([volume_vault_config_mount, volume_vault_variables_mount])

        volumes.extend([vol_vault_config, vault_variables_vol])

        vault_agent_container = client.V1Container(name="vault-agent",
                                                   image="vault",
                                                   env=vault_agent_env_list,
                                                   volume_mounts=volume_mounts,
                                                   args=["agent",
                                                         "-config=/etc/vault-config/vault-agent-config.hcl"])

        body.spec.template.spec.containers[0].volume_mounts.append(volume_vault_variables_mount)
        body.spec.template.spec.volumes.extend(volumes)
        body.spec.template.spec.init_containers = [vault_agent_container]
        return body, cm


    def create_kubernetes_job(self, args, cmd, container_image, container_name, name, namespace, pull_secrets):
        body = client.V1Job(api_version="batch/v1", kind="Job")
        body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
        body.status = client.V1JobStatus()
        template = client.V1PodTemplate()
        template.template = client.V1PodTemplateSpec()
        volumes = []
        vol = client.V1Volume(name="stackl-variables")
        inventory_config_map = client.V1ConfigMapVolumeSource()
        inventory_config_map.name = name
        vol.config_map = inventory_config_map
        volume_mounts = []
        volume_mount = client.V1VolumeMount(name="stackl-variables", mount_path="/etc/stackl-variables")
        volume_mounts.append(volume_mount)
        volumes.append(vol)
        container = client.V1Container(name=container_name, image=container_image,
                                       volume_mounts=volume_mounts,
                                       image_pull_policy="Always",
                                       command=cmd,
                                       args=args)
        secrets = [client.V1LocalObjectReference(name=s) for s in pull_secrets]
        template.template.spec = client.V1PodSpec(containers=[container], restart_policy='Never',
                                                  image_pull_secrets=secrets, volumes=volumes)
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600, template=template.template, backoff_limit=0)
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
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=600, template=template.template, backoff_limit=0)
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

    def handle(self, invocation, action):
        print(invocation)
        # Get the config for the tool
        tool_config = self.stackl_configuration[invocation.tool]

        stackl_namespace = os.environ['stackl_namespace']
        container_image = invocation.image
        name = "stackl-job-" + self.id_generator()

        print("create cm")
        config_map = self.create_variables_cm(name, stackl_namespace, invocation.stack_instance, invocation.service,
                                              tool_config["variables"])

        if action == "create" or action == "update":
            body = self.create_job_object(name, container_image, invocation.stack_instance, invocation.service,
                                          namespace=stackl_namespace, cmd=tool_config["create_command"],
                                          args=tool_config["create_args"],
                                          pull_secrets=tool_config["image_pull_secrets"])
            if hasattr(tool_config["secrets"],'vault'):
                #add init container
                body, vault_config_map = self.add_vault_agent_init_container(body, tool_config["secrets"]["vault"])
                print("body and cm: %s\n%s" % body, vault_agent_config)
                try:
                    api_response = self.api_instance_core.create_namespaced_config_map(stackl_namespace, vault_config_map)
                except ApiException as e:
                    print("Exception when calling V1Api->create_namespaced_configmap: %s\n" % e)
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
        if api_response.status.succeeded == 1:
            print("job succeeded")
            return 0, "", None
        else:
            return 1, "Still need proper output", None
