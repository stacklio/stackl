import json
from pathlib import Path

import click
import stackl_client
import yaml

from context import pass_stackl_context


@click.group()
def cli():
    pass


@cli.command()
@click.option('-d', '--directory', type=click.Path(exists=True))
@click.option('-c', '--config-file', type=click.File())
@click.option('-p', '--params', default="{}")
@click.option('-t', '--tags', default="{}")
@click.argument('instance-name', required=False)
@pass_stackl_context
def apply(stackl_context, directory, config_file, params, tags, instance_name):
    if instance_name is None:
        upload_files(directory, stackl_context)
    else:
        apply_stack_instance(config_file, params, tags, stackl_context,
                             instance_name)


def apply_stack_instance(config_file, params, tags, stackl_context,
                         instance_name):
    config_doc = yaml.load(config_file.read(), Loader=yaml.FullLoader)
    params = {**config_doc['params'], **json.loads(params)}
    invocation = stackl_client.StackInstanceInvocation(
        name=instance_name,
        stack_infrastructure_template=config_doc[
            "stack_infrastructure_template"],
        stack_application_template=config_doc["stack_application_template"],
        params=params,
        tags=json.loads(tags))
    try:
        stackl_context.stack_instances_api.get_stack_instance(instance_name)
        res = stackl_context.stack_instances_api.put_stack_instance(invocation)
    except stackl_client.exceptions.ApiException:
        res = stackl_context.stack_instances_api.post_stack_instance(
            invocation)
    click.echo(res)


def upload_files(directory, stackl_context):
    for path in Path(directory).rglob('*.yml'):
        with open(path, 'r') as doc:
            # ignore dotfiles
            if path.name.startswith('.'):
                continue
            click.echo(f"Reading document: { str(path) }")
            stackl_doc = yaml.load(doc.read(), Loader=yaml.FullLoader)
            if 'name' in stackl_doc:
                click.echo(
                    f"Applying stackl document: { str(path) + ' ' + stackl_doc['name']}"
                )
            else:
                click.echo(
                    f"Error in stackl document, no 'name' found: { path }")
            try:
                if stackl_doc["type"] in ["environment", "location", "zone"]:
                    stackl_context.documents_api.put_document(stackl_doc)
                if stackl_doc["type"] == "functional_requirement":
                    stackl_context.functional_requirements_api.put_functional_requirement(
                        stackl_doc)
                if stackl_doc["type"] == "service":
                    stackl_context.services_api.put_service(stackl_doc)
                if stackl_doc["type"] == "stack_application_template":
                    stackl_context.sat_api.put_stack_application_template(
                        stackl_doc)
                if stackl_doc["type"] == "stack_infrastructure_template":
                    stackl_context.sit_api.put_stack_infrastructure_template(
                        stackl_doc)
                click.echo(
                    f"Succesfully applied {stackl_doc['name']} with type {stackl_doc['type']}"
                )
            except stackl_client.exceptions.ApiException as e:
                click.echo(
                    f"Failed to apply {stackl_doc['name']} with type {stackl_doc['type']}: {e.body}"
                )
