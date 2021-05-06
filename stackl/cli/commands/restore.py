import click

from context import StacklContext
from urllib3.exceptions import NewConnectionError, MaxRetryError


@click.command()
@click.argument('snapshot_name', required=True)
def restore(snapshot_name):
    try:
        stackl_context = StacklContext
        result = stackl_context.snapshot_api.restore_snapshot(snapshot_name)
        click.echo(result)
    except (NewConnectionError, MaxRetryError) as e:
        click.echo("Unable to connect to Stackl host")
        click.echo(e)
        exit(1)
