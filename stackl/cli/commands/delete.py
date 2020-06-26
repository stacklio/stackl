import json

import click
import stackl_client

from context import pass_stackl_context, StacklContext


@click.group()
def delete():
    pass


@delete.command()
@click.argument('instance-name')
@pass_stackl_context
def instance(stackl_context: StacklContext, instance_name):
    res = stackl_context.stack_instances_api.delete_stack_instance(
        instance_name)
    click.echo(res)


@delete.command()
@click.argument('snapshot-name')
@pass_stackl_context
def snapshot(stackl_context: StacklContext, snapshot_name):
    res = stackl_context.snapshot_api.delete_snapshot(snapshot_name)
    click.echo(res)
