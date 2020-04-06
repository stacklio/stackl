from kubernetes import client, config
from kubernetes.client.rest import ApiException
from string import ascii_lowercase, digits
from time import sleep
import stackl_client
import os
import random
import json
from abc import ABC, abstractmethod
from typing import List, Dict
import logging.config

from handlers.vault_secret_handler import VaultSecretHandler

logger = logging.getLogger("STACKL_LOGGER")
level = os.environ.get("LOGLEVEL", "INFO").upper()
logger.setLevel(level)
ch = logging.StreamHandler()
ch.setLevel(level)
formatter = logging.Formatter(
    "{'time':'%(asctime)s', 'level': '%(levelname)s', 'message': '%(message)s'}"
)
ch.setFormatter(formatter)
logger.addHandler(ch)


def create_job_object(
        name,
        container_image,
        env_list: dict,
        command: List[str],
        command_args: List[str],
        volumes: List[Dict],
        image_pull_secrets: List[str],
        init_containers: List[Dict],
        namespace="stackl",
        container_name="jobcontainer",
        kind="Job",
        api_version="batch/v1",
        image_pull_policy="Always",
        ttl_seconds_after_finished=600,
        restart_policy="Never",
        backoff_limit=0,
        service_account="stackl-agent-stackl-agent") -> client.V1Job:
    id_job = id_generator()
    name = name + "-" + id_job
    body = client.V1Job(api_version=api_version, kind=kind)
    body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
    body.status = client.V1JobStatus()
    template = client.V1PodTemplate()
    template.template = client.V1PodTemplateSpec()
    k8s_volumes = []

    cms = []

    print("volumes: %s" % volumes)
    # create a volume for each element in volumes
    for vol in volumes:
        vol_name = name + "-" + vol["name"]
        k8s_volume = client.V1Volume(name=vol_name)
        if vol["type"] == "config_map":
            config_map = client.V1ConfigMapVolumeSource()
            config_map.name = vol_name
            k8s_volume.config_map = config_map
            cms.append(create_cm(vol_name, namespace, vol['data']))
            vol['name'] = vol_name
        if vol["type"] == "empty_dir":
            k8s_volume.empty_dir = client.V1EmptyDirVolumeSource(
                medium="Memory")
            vol['name'] = vol_name
        k8s_volumes.append(k8s_volume)

    logger.debug("Volumes created for job %s: %s" % (name, k8s_volumes))

    # create a volume mount for each element in volumes
    k8s_volume_mounts = []
    for vol in volumes:
        if vol["mount_path"]:
            volume_mount = client.V1VolumeMount(name=vol["name"],
                                                mount_path=vol["mount_path"])
            if hasattr(vol, "sub_path"):
                volume_mount.sub_path = vol["sub_path"]
            k8s_volume_mounts.append(volume_mount)

    logger.debug("Volume mounts created for job %s: %s" %
                 (name, k8s_volume_mounts))

    # create an environment list
    k8s_env_list = []

    print("env_list: %s" % env_list)
    if env_list:
        for key, value in env_list.items():
            k8s_env = client.V1EnvVar(name=key, value=value)
            k8s_env_list.append(k8s_env)

    logger.debug("Environment list created for job %s: %s" %
                 (name, k8s_env_list))

    container = client.V1Container(name=container_name,
                                   image=container_image,
                                   env=k8s_env_list,
                                   volume_mounts=k8s_volume_mounts,
                                   image_pull_policy=image_pull_policy,
                                   command=command,
                                   args=command_args)

    k8s_init_containers = []

    print("init_containers: %s" % init_containers)
    for c in init_containers:
        k8s_c = client.V1Container(name=c['name'],
                                   image=c['image'],
                                   args=c['args'],
                                   volume_mounts=k8s_volume_mounts,
                                   env=k8s_env_list)
        k8s_init_containers.append(k8s_c)

    k8s_secrets = []
    for secret in image_pull_secrets:
        k8s_secrets.append(client.V1LocalObjectReference(name=secret))

    logger.debug("Secret list created for job %s: %s" % (name, k8s_secrets))

    template.template.spec = client.V1PodSpec(
        containers=[container],
        restart_policy=restart_policy,
        image_pull_secrets=k8s_secrets,
        volumes=k8s_volumes,
        init_containers=k8s_init_containers,
        service_account_name=service_account)
    body.spec = client.V1JobSpec(
        ttl_seconds_after_finished=ttl_seconds_after_finished,
        template=template.template,
        backoff_limit=backoff_limit)

    return body, cms


def id_generator(size=12, chars=ascii_lowercase + digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_cm(name, namespace, data):
    cm = client.V1ConfigMap()
    cm.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
    cm.data = data
    return cm


# def create_variables_cm(name, namespace, stack_instance, service,
#                         variables_config):
#     cm = client.V1ConfigMap()
#     cm.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
#     stack_instance = self.stack_instance_api.get_stack_instance(stack_instance)
#     variables = {}
#     for key, value in stack_instance.services[
#             service].provisioning_parameters.items():
#         variables[key] = value
#     if variables_config["format"] == "json":
#         cm.data = {variables_config["filename"]: json.dumps(variables)}
#     return cm


class Handler(ABC):
    def __init__(self):
        config.load_incluster_config()
        self.configuration = client.Configuration()
        self.api_instance = client.BatchV1Api(
            client.ApiClient(self.configuration))
        self.api_instance_core = client.CoreV1Api(
            client.ApiClient(self.configuration))
        configuration = stackl_client.Configuration()
        configuration.host = "http://" + os.environ['stackl_host']
        api_client = stackl_client.ApiClient(configuration=configuration)
        self.stack_instance_api = stackl_client.StackInstancesApi(
            api_client=api_client)
        self.stack_instance = None
        self.service = None

    def wait_for_job(self, job_name, namespace):
        ready = False
        api_response = None
        while not ready:
            sleep(5)
            print("check status")
            api_response = self.api_instance.read_namespaced_job(
                job_name, namespace)
            print(api_response)
            if api_response.status.failed is not None or api_response.status.succeeded is not None:
                ready = True
        return api_response

    def handle(self, invocation, action):
        self.stack_instance = self.stack_instance_api.get_stack_instance(
            invocation.stack_instance)
        self.service = invocation.service
        logger.info("Invocation received: %s" % invocation)
        logger.info("Action received: %s" % action)
        stackl_namespace = os.environ['stackl_namespace']
        env_list, volumes, command, command_args, init_containers = self.get_k8s_objects(
            action)
        print("env_listje: %s" % env_list)
        container_image = invocation.image
        name = "stackl-job"
        image_pull_secrets = ["dome-nexus"]
        # config_map = self.create_config_map(name, stackl_namespace, invocation.stack_instance, invocation.service)
        body, cms = create_job_object(name, container_image, env_list, command,
                                      command_args, volumes,
                                      image_pull_secrets, init_containers)
        print("body: %s" % body)
        try:
            for cm in cms:
                api_response = self.api_instance_core.create_namespaced_config_map(
                    stackl_namespace, cm)
                print(api_response)
            print("trying to create job")
            api_response = self.api_instance.create_namespaced_job(
                stackl_namespace, body, pretty=True)
            print("api_responseke: %s" % api_response)
        except ApiException as e:
            print(
                "Exception when calling BatchV1Api->create_namespaced_job: %s\n"
                % e)
        print("job created")
        api_response = self.wait_for_job(body.metadata.name, stackl_namespace)
        if api_response.status.succeeded == 1:
            print("job succeeded")
            return 0, "", None
        else:
            return 1, "Still need proper output", None

    def get_k8s_objects(self, action):
        env_list = {
            **self.get_env_list(),
            **self.secret_handler.get_env_list()
        }
        volumes = self.get_volumes() + self.secret_handler.get_volumes()
        init_containers = self.secret_handler.get_init_containers()
        command = self.get_command()
        command_args = self.get_command_args(action)

        return env_list, volumes, command, command_args, init_containers

    @abstractmethod
    def parse_secrets(self, secrets):
        pass

    @abstractmethod
    def get_env_list(self):
        pass

    @abstractmethod
    def get_volumes(self):
        pass

    @abstractmethod
    def get_command(self):
        pass

    @abstractmethod
    def get_command_args(self, action):
        pass
