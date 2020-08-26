import click
import stackl_client

from context import StacklContext


@click.command()
def info():
    stackl_context = StacklContext()
    about_api = stackl_client.AboutApi(api_client=stackl_context.api_client)
    click.echo(about_api.get_hostname())
