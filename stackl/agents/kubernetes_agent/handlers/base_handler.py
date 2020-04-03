import logging
import os
import random
from abc import ABC
from string import ascii_lowercase, digits
from time import sleep
from typing import Dict, List
import stackl_client
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from outputs.output import Output


def create_job_object(name: str,
                      container_image: str,
                      env_list: dict,
                      command: List[str],
                      command_args: List[str],
                      volumes: List[Dict],
                      image_pull_secrets: List[str],
                      init_containers: List[Dict],
                      output: Output,
                      namespace: str = "stackl",
                      container_name: str = "jobcontainer",
                      api_version: str = "batch/v1",
                      image_pull_policy: str = "Always",
                      ttl_seconds_after_finished: int = 600,
                      restart_policy: str = "Never",
                      backoff_limit: int = 0,
                      service_account: str = "stackl-agent-stackl-agent",
                      labels={}) -> client.V1Job:
    """Creates a Job object using the Kubernetes client

    :param name: Job name affix
    :type name: str
    :param container_image: automation container image
    :type container_image: str
    :param env_list: Dict with key/values for the environment inside the automation container
    :type env_list: dict
    :param command: entrypoint command
    :type command: List[str]
    :param command_args: command arguments
    :type command_args: List[str]
    :param volumes: volumes and volumemounts
    :type volumes: List[Dict]
    :param image_pull_secrets: secrets to pull images
    :type image_pull_secrets: List[str]
    :param init_containers: list with init_containers
    :type init_containers: List[Dict]
    :param output: output Object
    :type output: Output
    :param namespace: Kubernetes namespace, defaults to "stackl"
    :type namespace: str, optional
    :param container_name: name of automation container, defaults to "jobcontainer"
    :type container_name: str, optional
    :param api_version: Job api version, defaults to "batch/v1"
    :type api_version: str, optional
    :param image_pull_policy: always pull latest images, defaults to "Always"
    :type image_pull_policy: str, optional
    :param ttl_seconds_after_finished: Remove jobs after execution with ttl, defaults to 600
    :type ttl_seconds_after_finished: int, optional
    :param restart_policy: Restart the pod on the same node after failure, defaults to "Never"
    :type restart_policy: str, optional
    :param backoff_limit: Retries after failure, defaults to 0
    :type backoff_limit: int, optional
    :param service_account: Kubernetes service account, defaults to "stackl-agent-stackl-agent"
    :type service_account: str, optional
    :param labels: metadata labels, defaults to {}
    :type labels: dict, optional
    :return: automation Job object
    :rtype: client.V1Job
    """
    id_job = id_generator()
    name = name + "-" + id_job
    body = client.V1Job(api_version=api_version, kind="Job")
    body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
    body.status = client.V1JobStatus()
    template = client.V1PodTemplate()
    template.template = client.V1PodTemplateSpec()
    k8s_volumes = []

    cms = []

    logging.debug(f"volumes: {volumes}")
    # create a k8s volume for each element in volumes
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

    logging.debug(f"Volumes created for job {name}: {k8s_volumes}")

    # create a volume mount for each element in volumes
    k8s_volume_mounts = []
    for vol in volumes:
        if vol["mount_path"]:
            volume_mount = client.V1VolumeMount(name=vol["name"],
                                                mount_path=vol["mount_path"])
            if "sub_path" in vol:
                volume_mount.sub_path = vol["sub_path"]
            k8s_volume_mounts.append(volume_mount)

    logging.debug(f"Volume mounts created for job {name}: {k8s_volume_mounts}")

    # create an environment list
    k8s_env_list = []

    if env_list:
        for key, value in env_list.items():
            k8s_env = client.V1EnvVar(name=key, value=value)
            k8s_env_list.append(k8s_env)

    logging.debug(f"Environment list created for job {name}: {k8s_env_list}")
    root_hack = client.V1SecurityContext()
    root_hack.run_as_user = 0

    container = client.V1Container(name=container_name,
                                   image=container_image,
                                   env=k8s_env_list,
                                   volume_mounts=k8s_volume_mounts,
                                   image_pull_policy=image_pull_policy,
                                   command=command,
                                   args=command_args)

    k8s_init_containers = []

    logging.debug(f"Init containers for job {name}: {init_containers}")
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

    logging.debug(f"Secret list created for job {name}: {k8s_secrets}")

    containers = []
    containers.append(container)
    if output:
        output.volume_mounts = k8s_volume_mounts
        output.env = k8s_env_list
        output_containers = output.containers
        containers = containers + output_containers

    template.template.metadata = client.V1ObjectMeta(labels=labels)
    template.template.spec = client.V1PodSpec(
        containers=containers,
        restart_policy=restart_policy,
        image_pull_secrets=k8s_secrets,
        volumes=k8s_volumes,
        init_containers=k8s_init_containers,
        security_context=root_hack,
        service_account_name=service_account)
    template.template = client.V1PodTemplateSpec(
        metadata=template.template.metadata, spec=template.template.spec)
    body.spec = client.V1JobSpec(
        ttl_seconds_after_finished=ttl_seconds_after_finished,
        template=template.template,
        backoff_limit=backoff_limit)

    return body, cms


def id_generator(size=12, chars=ascii_lowercase + digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_cm(name: str, namespace: str, data: dict) -> client.V1ConfigMap:
    """Returns Kubernetes configmap object

    :param name: configmap name
    :type name: str
    :param namespace: Kubernetes namespace
    :type namespace: str
    :param data: data in configmap
    :type data: dict
    :return: configmap
    :rtype: client.V1ConfigMap
    """
    cm = client.V1ConfigMap()
    cm.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
    cm.data = data
    return cm


class Handler(ABC):
    def __init__(self, invoc):
        if 'STACKL_HOST' not in os.environ:
            raise EnvironmentError(
                'Environment variable STACKL_HOST is not set.' +
                str(os.environ))
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            config.load_incluster_config()
        else:
            config.load_kube_config()
        self._configuration = client.Configuration()
        self._api_instance = client.BatchV1Api(
            client.ApiClient(self._configuration))
        self._api_instance_core = client.CoreV1Api(
            client.ApiClient(self._configuration))
        configuration = stackl_client.Configuration()
        configuration.host = "http://" + os.environ['STACKL_HOST']
        api_client = stackl_client.ApiClient(configuration=configuration)
        self._stack_instance_api = stackl_client.StackInstancesApi(
            api_client=api_client)
        self._stack_fr_api = stackl_client.FunctionalRequirementsApi(
            api_client=api_client)
        self._invoc = invoc
        self._service = self._invoc.service
        self._functional_requirement = self._invoc.functional_requirement
        self._functional_requirement_obj = self._stack_fr_api.get_functional_requirement_by_name(
            self._functional_requirement)
        self._stack_instance = self._stack_instance_api.get_stack_instance(
            self._invoc.stack_instance)
        self._output = None
        self._env_list = {}
        self._volumes = []
        self._init_containers = []
        self.provisioning_parameters = self._stack_instance.services[
            self._service].provisioning_parameters
        self.stackl_namespace = os.environ['STACKL_NAMESPACE']

    def wait_for_job(self, job_name: str, namespace: str):
        ready = False
        api_response = None
        while not ready:
            sleep(5)
            api_response = self._api_instance.read_namespaced_job(
                job_name, namespace)
            logging.debug(f"Api response: {api_response}")
            if api_response.status.failed or api_response.status.succeeded:
                ready = True
        return api_response

    def handle(self):
        logging.info(f"Invocation: {self._invoc}")
        logging.info(f"Action: {self._invoc.action}")

        container_image = self._invoc.image
        name = "stackl-job"
        image_pull_secrets = ["dome-nexus"]
        labels = {
            "app.kubernetes.io/managed-by": "stackl",
            "stackl.io/stack-instance": self._invoc.stack_instance,
            "stackl.io/service": self._invoc.service,
            "stackl.io/functional-requirement":
            self._invoc.functional_requirement
        }
        body, cms = create_job_object(name=name,
                                      container_image=container_image,
                                      env_list=self.env_list,
                                      command=self.command,
                                      command_args=self.command_args,
                                      volumes=self.volumes,
                                      image_pull_secrets=image_pull_secrets,
                                      init_containers=self.init_containers,
                                      namespace=self.stackl_namespace,
                                      output=self._output,
                                      labels=labels)
        try:
            for cm in cms:
                self._api_instance_core.create_namespaced_config_map(
                    self.stackl_namespace, cm)
            self._api_instance.create_namespaced_job(self.stackl_namespace,
                                                     body,
                                                     pretty=True)
        except ApiException as e:
            logging.error(
                f"Exception when calling BatchV1Api->create_namespaced_job: {e}\n"
            )
        logging.debug("job created")
        api_response = self.wait_for_job(body.metadata.name,
                                         self.stackl_namespace)
        if api_response.status.succeeded == 1:
            try:
                for cm in cms:
                    self._api_instance_core.delete_namespaced_config_map(
                        self.stackl_namespace, cm)
                self._api_instance.delete_namespaced_job(self.stackl_namespace,
                                                         body,
                                                         pretty=True)
            except ApiException as e:
                logging.error(
                    f"Exception when calling BatchV1Api->delete_namespaced_job: {e}\n"
                )
            return 0, "", None
        else:
            return 1, "Still need proper output", None

    @property
    def env_list(self) -> dict:
        """Returns the combined environment variables from the Handler, SecretHandler, Output

        :return: environment variables
        :rtype: dict
        """
        env_list = {**self._env_list}
        # A secret handler has been set and is not None
        if self.secret_handler:
            env_list.update(self.secret_handler.env_list)
        if self._output:
            env_list.update(self._output.env_list)
        return env_list

    @property
    def volumes(self) -> list:
        """Returns the combined volumes from the Handler, SecretHandler, Output

        :return: volumes
        :rtype: list
        """
        volumes = self._volumes
        # A secret handler has been set and is not None
        if self.secret_handler:
            volumes += self.secret_handler.volumes
        if self._output:
            volumes += self._output.volumes
        return volumes

    @property
    def init_containers(self) -> list:
        """Returns the combined init_containers from the Handler, SecretHandler, Output

        :return: init_containers
        :rtype: list
        """
        init_containers = self._init_containers
        # A secret handler has been set and is not None
        if self.secret_handler:
            init_containers += self.secret_handler.init_containers
        if self._output:
            init_containers += self._output.init_containers
        return init_containers

    @env_list.setter
    def env_list(self, value):
        self._env_list = value

    @volumes.setter
    def volumes(self, value):
        self._volumes = value

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def command_args(self):
        if self._invoc.action == "create" or self._invoc.action == "update":
            return self.create_command_args
        if self._invoc.action == "delete":
            return self.delete_command_args

    @command_args.setter
    def command_args(self, value):
        self._command_args = value

    @property
    def secret_handler(self):
        return self._secret_handler

    @property
    def __isabstractmethod__(self):
        return any(
            getattr(f, '__isabstractmethod__', False)
            for f in (self.wait_for_job, self.handle, self.get_k8s_objects,
                      self.action))
