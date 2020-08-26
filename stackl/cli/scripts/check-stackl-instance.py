#!/usr/bin/env python3
import os
import time
from pathlib import Path

import stackl_client


def get_config_path():
    if len(str(Path.home())) == 0:
        config_path = os.getcwd() + os.sep + '.stackl' + os.sep + 'config'
    else:
        config_path = str(Path.home()) + os.sep + '.stackl' + os.sep + 'config'
    return config_path


with open(get_config_path(), 'r+') as stackl_config:
    host = stackl_config.read()
    configuration = stackl_client.Configuration()
    configuration.host = host

api_client = stackl_client.ApiClient(configuration=configuration)
stack_instances_api = stackl_client.StackInstancesApi(
    api_client=api_client)

if "STACKL_INSTANCE" in os.environ:
    stack_instance = stack_instances_api.get_stack_instance(os.environ['STACKL_INSTANCE'])
    ready = False
    while not ready:
        for status in stack_instance.status:
            if status.status == "FAILED":
                print(f"Stack instance {stack_instance.name}: service {status.service} on functional-requirement {status.functional_requirement} failed!")
                exit(1)
            elif status.status == "in_progress":
                print(f"Stack instance {stack_instance.name}: service {status.service} on functional-requirement {status.functional_requirement} not ready, still waiting")
                time.sleep(5)
                stack_instance = stack_instances_api.get_stack_instance(os.environ['STACKL_INSTANCE'])
                ready = False
                break
            else:
                print(
                    f"Stack instance {stack_instance.name}: service {status.service} on functional-requirement {status.functional_requirement} ready")
                ready = True
else:
    print("STACKL_INSTANCE NOT SET")
    exit(1)
