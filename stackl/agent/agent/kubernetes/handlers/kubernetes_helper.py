import logging
from random import random
from string import ascii_lowercase, digits
from typing import Dict, List
from kubernetes import client
from agent.kubernetes.outputs.output import Output

def check_container_status(container_status):
    """
    Checks the status of the job containers
    Returns a tuple with a boolean and a string
    True if failed, False if succeeded
    """
    if container_status.state.terminated is not None:
        if container_status.state.terminated.reason == "Error":
            return True, "failed"
    if container_status.state.waiting is not None:
        if container_status.state.waiting.reason == "ErrImagePull" \
            or container_status.state.waiting.reason == "ImagePullBackOff":
            return True, "Image for this functional requirement can not be found"
    return False, ""

def id_generator(size=12, chars=ascii_lowercase + digits):
    """
    Generates a random id
    """
    return ''.join(random.choice(chars) for _ in range(size))


def check_job_status(job):
    """
    Checks the status of the job, returning False if done
    """
    if job.status.conditions is not None and \
        job.status.active is None and job.status.succeeded is None:
        for condition in job.status.conditions:
            if condition.type == 'Failed' and condition.reason == 'DeadlineExceeded':
                return True, condition.message
    return False, ""


def create_job_object(name: str,
                      container_image: str,
                      env_list: dict,
                      command: List[str],
                      command_args: List[str],
                      volumes: List[Dict],
                      init_containers: List[Dict],
                      output: Output,
                      namespace: str = "stackl",
                      container_name: str = "jobcontainer",
                      api_version: str = "batch/v1",
                      image_pull_policy: str = "Always",
                      ttl_seconds_after_finished: int = 3600,
                      restart_policy: str = "Never",
                      backoff_limit: int = 0,
                      active_deadline_seconds: int = 3600,
                      service_account: str = "stackl-agent-stackl-agent",
                      image_pull_secrets: List[str] = [],
                      labels=None) -> client.V1Job:
    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
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
    :param active_deadline_seconds: Timeout on a job, defaults to 3600 seconds
    :type active_deadline_seconds: int, optional
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
        backoff_limit=backoff_limit,
        active_deadline_seconds=active_deadline_seconds)

    return body, cms

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