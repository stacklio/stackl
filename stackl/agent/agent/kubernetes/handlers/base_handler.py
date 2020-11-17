import logging
import os
import random
from abc import ABC
from string import ascii_lowercase, digits
from time import sleep
from typing import Dict, List

import stackl_client
from agent.kubernetes.outputs.output import Output
from agent.kubernetes.secrets.conjur_secret_handler import ConjurSecretHandler
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from agent import config as agent_config


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
                      ttl_seconds_after_finished: int = 3600,
                      restart_policy: str = "Never",
                      backoff_limit: int = 0,
                      service_account: str = "stackl-agent-stackl-agent",
                      labels={},
                      env_from: List[Dict] = None) -> client.V1Job:
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
            if isinstance(value, dict):
                if 'config_map_key_ref' in value:
                    k8s_env_from = client.V1EnvVar(
                        name=key,
                        value_from=client.V1EnvVarSource(
                            config_map_key_ref=client.V1ConfigMapKeySelector(
                                name=value['config_map_key_ref']["name"],
                                key=value['config_map_key_ref']["key"])))
                    k8s_env_list.append(k8s_env_from)
                elif 'field_ref' in value:
                    k8s_env_from = client.V1EnvVar(
                        name=key,
                        value_from=client.V1EnvVarSource(
                            field_ref=client.V1ObjectFieldSelector(
                                field_path=value['field_ref'])))
                    k8s_env_list.append(k8s_env_from)
            else:
                k8s_env = client.V1EnvVar(name=key, value=value)
                k8s_env_list.append(k8s_env)

    k8s_env_from_list = []

    # if env_from:
    #     for env in env_from:
    #         if 'config_map_ref' in env:
    #             k8s_env_from = client.V1EnvFromSource(
    #                 config_map_ref=env['config_map_ref'])
    #             k8s_env_from_list.append(k8s_env_from)
    #         elif 'secret_ref' in env:
    #             k8s_env_from = client.V1EnvFromSource(
    #                 secret_ref=env['secret_ref'])
    #             k8s_env_from_list.append(k8s_env_from)

    logging.debug(f"Environment list created for job {name}: {k8s_env_list}")
    print(f"Environment list created for job {name}: {k8s_env_list}")

    container = client.V1Container(name=container_name,
                                   image=container_image,
                                   env=k8s_env_list,
                                   volume_mounts=k8s_volume_mounts,
                                   image_pull_policy=image_pull_policy,
                                   command=command,
                                   args=command_args,
                                   env_from=k8s_env_from_list)

    k8s_init_containers = []

    logging.debug(f"Init containers for job {name}: {init_containers}")
    for c in init_containers:
        k8s_c = client.V1Container(name=c['name'],
                                   image=c['image'],
                                   volume_mounts=k8s_volume_mounts,
                                   env=k8s_env_list)

        if 'args' in c:
            k8s_c.args = c['args']

        k8s_init_containers.append(k8s_c)

    k8s_secrets = []
    for secret in image_pull_secrets:
        k8s_secrets.append(client.V1LocalObjectReference(name=secret))

    logging.debug(f"Secret list created for job {name}: {k8s_secrets}")

    containers = [container]
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
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            config.load_incluster_config()
        else:
            config.load_kube_config()
        logging.getLogger().setLevel(agent_config.settings.loglevel)
        self._configuration = client.Configuration()
        self._api_instance = client.BatchV1Api(
            client.ApiClient(self._configuration))
        self._api_instance_core = client.CoreV1Api(
            client.ApiClient(self._configuration))
        configuration = stackl_client.Configuration()
        configuration.host = agent_config.settings.stackl_host
        api_client = stackl_client.ApiClient(configuration=configuration)
        self._stack_instance_api = stackl_client.StackInstancesApi(
            api_client=api_client)
        self._stack_fr_api = stackl_client.FunctionalRequirementsApi(
            api_client=api_client)
        self._invoc = invoc
        self._service = self._invoc.service
        self.hosts = self._invoc.hosts
        self._functional_requirement = self._invoc.functional_requirement
        self._functional_requirement_obj = self._stack_fr_api.get_functional_requirement_by_name(
            self._functional_requirement)
        self._stack_instance = self._stack_instance_api.get_stack_instance(
            self._invoc.stack_instance)
        self._output = None
        self._env_from = {}
        self._env_list = {}
        self._volumes = []
        self._init_containers = []
        self.stackl_namespace = agent_config.settings.stackl_namespace
        self.service_account = agent_config.settings.service_account

    def check_container_status(self, container_status):
        if container_status.state.terminated is not None:
            if container_status.state.terminated.reason == "Error":
                return True, "failed"
        if container_status.state.waiting is not None:
            if container_status.state.waiting.reason == "ErrImagePull" or container_status.state.waiting.reason == "ImagePullBackOff":
                return True, "Image for this functional requirement can not be found"
        return False, ""

    def wait_for_job(self, job_pod_name: str, namespace: str):
        while True:
            sleep(5)
            api_response = self._api_instance_core.read_namespaced_pod_status(
                job_pod_name, namespace)
            # Check init container statuses
            for init_cs in api_response.status.init_container_statuses:
                error, msg = self.check_container_status(init_cs)
                if error:
                    return False, msg, init_cs.name
            # Check container statuses
            for cs in api_response.status.container_statuses:
                error, msg = self.check_container_status(cs)
                if error:
                    return False, msg, cs.name
                if cs.state.waiting is None and cs.state.running is None and cs.state.terminated is not None and cs.state.terminated.reason == 'Completed' and cs.name == "jobcontainer":
                    return True, "", cs.name

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
                                      service_account=self.service_account,
                                      output=self._output,
                                      labels=labels)

        try:
            for cm in cms:
                self._api_instance_core.create_namespaced_config_map(
                    self.stackl_namespace, cm)
            created_job = self._api_instance.create_namespaced_job(
                self.stackl_namespace, body, pretty=True)
        except ApiException as e:
            logging.error(
                f"Exception when calling BatchV1Api->create_namespaced_job: {e}\n"
            )
        logging.debug("job created")
        sleep(5)
        job_pods = self._api_instance_core.list_namespaced_pod(
            self.stackl_namespace,
            label_selector=f"job-name={created_job.metadata.name}")
        job_succeeded, job_status, job_container_name = self.wait_for_job(
            job_pods.items[0].metadata.name, self.stackl_namespace)

        if job_succeeded:
            print("job succeeded")
            try:
                for cm in cms:
                    self._api_instance_core.delete_namespaced_config_map(
                        cm.metadata.name, self.stackl_namespace)
                self._api_instance.delete_namespaced_job(body.metadata.name,
                                                         self.stackl_namespace,
                                                         pretty=True)

            except ApiException as e:
                logging.error(
                    f"Exception when calling BatchV1Api->delete_namespaced_job: {e}\n"
                )
            return 0, ""
        else:
            print("job failed")
            if job_status == "failed":
                error_msg = self._api_instance_core.read_namespaced_pod_log(
                    job_pods.items[0].metadata.name,
                    self.stackl_namespace,
                    container=job_container_name)
            else:
                error_msg = job_status
            return 1, error_msg

    @property
    def index(self):
        index = 0
        for service_definition in self._stack_instance.services[self._service]:
            if service_definition.infrastructure_target == self._invoc.infrastructure_target:
                return index
            index += 1

    @property
    def provisioning_parameters(self):
        for service_definition in self._stack_instance.services[self._service]:
            if service_definition.infrastructure_target == self._invoc.infrastructure_target:
                return service_definition.provisioning_parameters

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

    @property
    def env_from(self) -> list:
        """Returns the combined env_from from the Handler, SecretHandler, Output

        :return: env_from
        :rtype: list
        """
        env_from = self._env_from
        if self.secret_handler:
            env_from.update(self.secret_handler._env_from)
        return env_from

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

    @property
    def create_command_args(self) -> List[str]:
        if isinstance(self.secret_handler, ConjurSecretHandler):
            return [
                "summon --provider summon-conjur -f /tmp/conjur/secrets.yml "
            ]
        else:
            return [""]
