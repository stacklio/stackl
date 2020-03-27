import click

from commands.apply import apply
from commands.edit import edit
from commands.get import get
from commands.connect import connect
from commands.create import create
from commands.info import info
from commands.update import update


@click.group()
def cli():
    pass


cli.add_command(connect)
cli.add_command(get)
cli.add_command(info)
cli.add_command(apply)
cli.add_command(create)
cli.add_command(update)
cli.add_command(edit)
