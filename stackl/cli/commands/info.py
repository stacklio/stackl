import click
import stackl_client

from context import pass_stackl_context


@click.command()
@pass_stackl_context
def info(stackl_context):
    about_api = stackl_client.AboutApi(api_client=stackl_context.api_client)
    click.echo(about_api.get_hostname())
