import json

import click
import stackl_client

from context import pass_stackl_context, StacklContext


@click.group()
def create():
    pass


@create.command()
@click.option('--stack-infrastructure-template')
@click.option('--stack-application-template')
@click.option('-p', '--params', default="{}")
@click.option('-t', '--tags', default="{}")
@click.argument('instance-name')
@pass_stackl_context
def instance(stackl_context: StacklContext, stack_infrastructure_template,
             stack_application_template, params, tags, instance_name):
    invocation = stackl_client.StackInstanceInvocation(
        stack_instance_name=instance_name,
        stack_infrastructure_template=stack_infrastructure_template,
        stack_application_template=stack_application_template,
        params=json.loads(params),
        tags=json.loads(tags))
    res = stackl_context.stack_instances_api.post_stack_instance(invocation)
    click.echo(res)
