import json

import click
import stackl_client
from context import pass_stackl_context, StacklContext


@click.group()
@click.pass_context
def update(ctx):
    ctx.obj = StacklContext()


@update.command()
@click.option('-p', '--params', default=[], multiple=True)
@click.option('-s', '--secrets', default="{}")
@click.option('-d', '--disable-invocation', is_flag=True)
@click.argument('instance-name')
@pass_stackl_context
def instance(stackl_context: StacklContext, params, secrets,
             disable_invocation, instance_name):
    final_params = {}
    for item in params:
        final_params = {**final_params, **json.loads(item)}
    invocation = stackl_client.StackInstanceUpdate(
        stack_instance_name=instance_name,
        params=final_params,
        secrets=json.loads(secrets))
    if disable_invocation:
        invocation.disable_invocation = True
    res = stackl_context.stack_instances_api.put_stack_instance(invocation)
    click.echo(res)


@update.command()
@click.option('-p', '--params', default="{}")
@click.option('-i', '--infrastructure-target', required=True)
@click.option('-s', '--service', required=True)
@click.argument('instance-name')
@pass_stackl_context
def outputs(stackl_context: StacklContext, params, infrastructure_target, service, instance_name):
    outputs_update = stackl_client.OutputsUpdate(outputs=json.loads(params), infrastructure_target=infrastructure_target,
                                                 service=service, stack_instance=instance_name)
    stackl_context.outputs_api.add_outputs(outputs_update)
    click.echo("Updated outputs")
