import json
from pathlib import Path
from stackl_client.models import StackStage
from sys import exit

import click
import stackl_client
import yaml
from urllib3.exceptions import NewConnectionError, MaxRetryError
from stackl_client.exceptions import ApiException, ApiValueError
from commands.autocomplete import show_progress_bar
from context import StacklContext
from mergedeep import merge


@click.command()
@click.option('-d', '--directory', type=click.Path(exists=True))
@click.option('-c', '--config-file', type=click.File())
@click.option('-p', '--params', default=[], multiple=True)
@click.option('-t', '--tags', default="{}")
@click.option('-r', '--replicas', default="{}")
@click.option('-s', '--secrets', default="{}")
@click.option('-e', '--service-params', default="{}")
@click.option('--service-secrets', default="{}")
@click.option('--services', default=[])
@click.option('-s', '--show-progress', default=False, is_flag=True)
@click.argument('instance-name', required=False)
def apply(directory, config_file, params, tags, secrets, service_params,
          service_secrets, replicas, services, instance_name, show_progress):
    try:
        stackl_context = StacklContext()
        if instance_name is None:
            upload_files(directory, stackl_context)
        else:
            apply_stack_instance(config_file, params, tags, secrets,
                                service_params, service_secrets, replicas,
                                services, stackl_context, instance_name,
                                show_progress)
    except ApiException as e:
        click.echo(e.body)
        exit(1)
    except ApiValueError as e:
        click.echo(e.body)
        exit(1)
    except (NewConnectionError, MaxRetryError) as e:
        click.echo("Unable to connect to Stackl host")
        click.echo(e)
        exit(1)


def apply_stack_instance(config_file, params, tags, secrets, service_params,
                         service_secrets, replicas, services, stackl_context,
                         instance_name, show_progress):
    final_params = {}
    for item in params:
        final_params = {**final_params, **json.loads(item)}
    config_doc = yaml.load(config_file.read(), Loader=yaml.FullLoader)
    final_params = {**config_doc['params'], **final_params}
    tags = json.loads(tags)
    replicas = json.loads(replicas)
    stages = []
    if "replicas" in config_doc:
        replicas = {**config_doc['replicas'], **replicas}
    secrets = json.loads(secrets)
    service_params = json.loads(service_params)
    if "service_params" in config_doc:
        service_params = merge(config_doc['service_params'], service_params)
    service_secrets = json.loads(service_secrets)
    if "service_secrets" in config_doc:
        service_secrets = merge(config_doc['service_secrets'], service_secrets)
    if "secrets" in config_doc:
        secrets = {**config_doc['secrets'], **secrets}
    if "tags" in config_doc:
        tags = {**config_doc['tags'], **tags}
    if "services" in config_doc:
        services = config_doc['services']
    if "stages" in config_doc:
        stages_list = config_doc['stages']
        for stage in stages_list:
            stage_obj = StackStage(name=stage['name'], services=stage['services'])
            stages.append(stage_obj)
    invocation = stackl_client.models.StackInstanceInvocation(
        stack_instance_name=instance_name,
        stack_infrastructure_template=config_doc[
            "stack_infrastructure_template"],
        stack_application_template=config_doc["stack_application_template"],
        params=final_params,
        replicas=replicas,
        service_params=service_params,
        service_secrets=service_secrets,
        secrets=secrets,
        services=services,
        stages=stages,
        tags=tags)
    try:
        invocation = stackl_client.models.StackInstanceUpdate(
        stack_instance_name=instance_name,
        params=final_params,
        replicas=replicas,
        service_params=service_params,
        service_secrets=service_secrets,
        secrets=secrets,
        services=services,
        stages=stages,
        tags=tags)
        stackl_context.stack_instances_api.get_stack_instance(instance_name)
        res = stackl_context.stack_instances_api.put_stack_instance(invocation)
    except stackl_client.exceptions.NotFoundException as e:
        try:
            invocation = stackl_client.models.StackInstanceInvocation(
            stack_instance_name=instance_name,
            stack_infrastructure_template=config_doc[
                "stack_infrastructure_template"],
            stack_application_template=config_doc["stack_application_template"],
            params=final_params,
            replicas=replicas,
            service_params=service_params,
            service_secrets=service_secrets,
            secrets=secrets,
            services=services,
            stages=stages,
            tags=tags)
            res = stackl_context.stack_instances_api.post_stack_instance(invocation)
        except ApiException as e:
            click.echo(e)
            exit(1)
    except ApiException as e:
        click.echo(e.body)
        exit(1)
    except ApiValueError as e:
        click.echo(e.body)
        exit(1)
    except (NewConnectionError, MaxRetryError) as e:
        click.echo("Unable to connect to Stackl host")
        click.echo(e)
        exit(1)

    click.echo(res)

    if show_progress:
        show_progress_bar(stackl_context, instance_name)


def upload_file(stackl_doc, stackl_context, path):
    if 'name' in stackl_doc:
        click.echo(
            f"Applying stackl document: {str(path) + ' ' + stackl_doc['name']}"
        )
    else:
        click.echo(f"Error in stackl document, no 'name' found: {path}")
    try:
        if stackl_doc["type"] in ["environment", "location", "zone"]:
            stackl_context.infrastructure_base_api.put_infrastructure_base(
                stackl_doc)
        if stackl_doc["type"] == "functional_requirement":
            stackl_context.functional_requirements_api.put_functional_requirement(
                stackl_doc)
        if stackl_doc["type"] == "service":
            stackl_context.services_api.put_service(stackl_doc)
        if stackl_doc["type"] == "stack_application_template":
            stackl_context.sat_api.put_stack_application_template(stackl_doc)
        if stackl_doc["type"] == "stack_infrastructure_template":
            stackl_context.sit_api.put_stack_infrastructure_template(
                stackl_doc)
        if stackl_doc["type"] == "policy_template":
            stackl_context.policy_templates_api.put_policy_template(stackl_doc)
        click.echo(
            f"Succesfully applied {stackl_doc['name']} with type {stackl_doc['type']}"
        )
    except ApiException as e:
        click.echo(
            f"Failed to apply {stackl_doc['name']} with type {stackl_doc['type']}: {e.body}"
        )
        exit(1)
    except ApiValueError as e:
        click.echo(e.body)
        exit(1)
    except (NewConnectionError, MaxRetryError) as e:
        click.echo("Unable to connect to Stackl host")
        click.echo(e)
        exit(1)


def upload_files(directory, stackl_context):
    for path in Path(directory).rglob('*.yml'):
        with open(path, 'r') as doc:
            # ignore dotfiles
            if path.name.startswith('.'):
                continue
            click.echo(f"Reading document: {str(path)}")
            stackl_doc = yaml.load(doc.read(), Loader=yaml.FullLoader)
            upload_file(stackl_doc, stackl_context, path)
    for path in Path(directory).rglob('*.json'):
        with open(path, 'r') as doc:
            # ignore dotfiles
            if path.name.startswith('.'):
                continue
            click.echo(f"Reading document: {str(path)}")
            stackl_doc = yaml.load(doc.read(), Loader=yaml.FullLoader)
            upload_file(stackl_doc, stackl_context, path)
