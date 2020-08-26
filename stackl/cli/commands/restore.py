import click

from context import StacklContext


@click.command()
@click.argument('snapshot_name', required=True)
def restore(snapshot_name):
    stackl_context = StacklContext
    result = stackl_context.snapshot_api.restore_snapshot(snapshot_name)
    click.echo(result)
