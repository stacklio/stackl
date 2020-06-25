import json

import click
import stackl_client

from context import pass_stackl_context, StacklContext


@click.group()
def update():
    pass


@update.command()
@click.option('-p', '--params', default="{}")
@click.option('-s', '--secrets', default="{}")
@click.option('-d', '--disable-invocation', is_flag=True)
@click.argument('instance-name')
@pass_stackl_context
def instance(stackl_context: StacklContext, params, secrets,
             disable_invocation, instance_name):
    invocation = stackl_client.StackInstanceUpdate(
        stack_instance_name=instance_name,
        params=json.loads(params),
        secrets=json.loads(secrets))
    if disable_invocation:
        invocation.disable_invocation = True
    res = stackl_context.stack_instances_api.put_stack_instance(invocation)
    click.echo(res)
