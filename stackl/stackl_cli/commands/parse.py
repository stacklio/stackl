import json

import click
import stackl_client
import yaml

from context import pass_stackl_context, StacklContext


@click.command()
@click.option('-c', '--config-file', type=click.File())
@click.option('-p', '--params', default="{}")
@click.argument('instance-name')
@pass_stackl_context
def parse(stackl_context: StacklContext, config_file, params, instance_name):
    config_doc = yaml.load(config_file.read(), Loader=yaml.FullLoader)
    params = {**config_doc['params'], **json.loads(params)}
    invocation = stackl_client.StackInstanceInvocation(stack_instance_name=instance_name,
                                                       stack_infrastructure_template=config_doc[
                                                           "stack_infrastructure_template"],
                                                       stack_application_template=config_doc[
                                                           "stack_application_template"],
                                                       params=params)
    res = stackl_context.stack_instances_api.post_stack_instance(invocation)
    click.echo(res)
