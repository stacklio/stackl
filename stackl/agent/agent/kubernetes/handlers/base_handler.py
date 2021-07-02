"""
This module contains all methods and classes for creating resources in kubernetes
"""
import logging
import os
from abc import ABC
from time import sleep
from typing import Any, Dict, List

import stackl_client
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from agent import config as agent_config
from agent.kubernetes.handlers.kubernetes_helper import (
    check_container_status, check_job_status, create_job_object)


class Handler(ABC):
    # pylint: disable=too-many-instance-attributes
    """
    Base handler class used by the subclasses of the different automation tools
    to provision resources through kubernetes
    """
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
        self.command = None
        self._output = None
        self._env_from = {}
        self._env_list = {}
        self._volumes = []
        self._init_containers = []
        self.stackl_namespace = agent_config.settings.stackl_namespace
        self.service_account = agent_config.settings.service_account
        self._secret_handler = None

    def wait_for_job(self, job_pod_name: str, namespace: str, job):
        """
        This method polls every 5 seconds to see if the job is ready
        """
        while True:
            sleep(5)
            job = self._api_instance.read_namespaced_job(
                job.metadata.name, namespace)
            error, msg = check_job_status(job)
            if error:
                return False, msg, None
            api_response = self._api_instance_core.read_namespaced_pod_status(
                job_pod_name, namespace)
            # Check init container statuses
            for init_cs in api_response.status.init_container_statuses:
                error, msg = check_container_status(init_cs)
                if error:
                    return False, msg, init_cs.name
            # Check container statuses
            containers_ready = True
            for cs in api_response.status.container_statuses:
                error, msg = check_container_status(cs)
                if error:
                    return False, msg, cs.name
                if cs.state.terminated is None or \
                    cs.state.terminated.reason != 'Completed':
                    containers_ready = False
            if containers_ready:
                return True, "", None

    def handle(self):
        """
        Entrypoint for handling
        """
        logging.info(f"Invocation: {self._invoc}")
        logging.info(f"Action: {self._invoc.action}")

        container_image = self._invoc.image
        name = "stackl-job"
        labels = {
            "app.kubernetes.io/managed-by": "stackl",
            "stackl.io/stack-instance": self._invoc.stack_instance,
            "stackl.io/service": self._invoc.service,
            "stackl.io/functional-requirement":
            self._invoc.functional_requirement
        }
        sidecar_containers = []
        if self._invoc.action != "delete" and self._output:
            sidecar_containers = self._output.containers
        body, cms = create_job_object(name=name,
                                      container_image=container_image,
                                      env_list=self.env_list,
                                      command=self.command,
                                      command_args=self.command_args,
                                      volumes=self.volumes,
                                      init_containers=self.init_containers,
                                      sidecar_containers=sidecar_containers,
                                      namespace=self.stackl_namespace,
                                      service_account=self.service_account,
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
            job_pods.items[0].metadata.name, self.stackl_namespace,
            created_job)

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
        """
        Returns the index of the service definition of the current
        infrastructure target?
        """
        index = 0
        for service_definition in self._stack_instance.services[self._service]:
            if service_definition.infrastructure_target == self._invoc.infrastructure_target:
                return index
            index += 1
        return None

    @property
    def provisioning_parameters(self) -> Dict[str, Any]:
        """
        Get all provisioning parameters for the current invocation
        """
        for service_definition in self._stack_instance.services[self._service]:
            if service_definition.infrastructure_target == self._invoc.infrastructure_target:
                return service_definition.provisioning_parameters
        return {}

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
        if self._output and self._invoc.action != "delete":
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
    def command_args(self):
        """
        Gets the command args for create or delete
        """
        if self._invoc.action == "create" or self._invoc.action == "update":
            return self.create_command_args
        if self._invoc.action == "delete":
            return self.delete_command_args
        return None

    @command_args.setter
    def command_args(self, value):
        self._command_args = value

    @property
    def secret_handler(self):
        """
        Returns the secret handler
        """
        return self._secret_handler

    @property
    def create_command_args(self) -> List[str]:
        """
        Returns the command args to be run in the container
        """
        return [""]

    @property
    def delete_command_args(self) -> List[str]:
        """
        Returns the command args to be run in the container
        for deleting
        """
        return [""]
