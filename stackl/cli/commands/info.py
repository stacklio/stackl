import click
import stackl_client.apis as stackl_apis

from context import StacklContext
from urllib3.exceptions import NewConnectionError, MaxRetryError

@click.command()
def info():
    try:
        stackl_context = StacklContext()
        about_api = stackl_apis.AboutApi(api_client=stackl_context.api_client)
        click.echo(about_api.get_hostname())
    except (NewConnectionError, MaxRetryError) as e:
        click.echo("Unable to connect to Stackl host")
        click.echo(e)
        exit(1)
