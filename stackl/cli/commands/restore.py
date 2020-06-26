import click

from context import pass_stackl_context, StacklContext


@click.command()
@click.argument('snapshot_name', required=True)
@pass_stackl_context
def restore(stackl_context: StacklContext, snapshot_name):
    result = stackl_context.snapshot_api.restore_snapshot(snapshot_name)
    click.echo(result)