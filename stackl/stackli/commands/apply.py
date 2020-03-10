from pathlib import Path

import click
import stackl_client
import yaml

from context import pass_stackl_context


@click.group()
def cli():
    pass


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@pass_stackl_context
def apply(stackl_context, directory):
    for path in Path(directory).rglob('*.yml'):
        with open(path, 'r') as doc:
            stackl_doc = yaml.load(doc.read(), Loader=yaml.FullLoader)
            click.echo(f"Applying stackl document: {stackl_doc['name']}")
            try:
                if stackl_doc["type"] in ["environment", "location", "zone"]:
                    stackl_context.documents_api.put_document(stackl_doc)
                if stackl_doc["type"] == "functional_requirement":
                    stackl_context.functional_requirements_api.put_functional_requirement(stackl_doc)
                if stackl_doc["type"] == "service":
                    stackl_context.services_api.put_service(stackl_doc)
                if stackl_doc["type"] == "stack_application_template":
                    stackl_context.sat_api.put_stack_application_template(stackl_doc)
                if stackl_doc["type"] == "stack_infrastructure_template":
                    stackl_context.sit_api.put_stack_infrastructure_template(stackl_doc)
                click.echo(f"Succesfully applied {stackl_doc['name']} with type {stackl_doc['type']}")
            except stackl_client.exceptions.ApiException as e:
                click.echo(f"Failed to apply {stackl_doc['name']} with type {stackl_doc['type']}: {e.body}")
