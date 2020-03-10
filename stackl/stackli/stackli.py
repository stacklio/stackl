import click

from commands.apply import apply
from commands.connect import connect
from commands.info import info


@click.group()
def cli():
    pass


cli.add_command(connect)
cli.add_command(info)
cli.add_command(apply)
