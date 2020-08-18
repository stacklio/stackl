import click

from commands.apply import apply
from commands.connect import connect
from commands.create import create
from commands.delete import delete
from commands.edit import edit
from commands.get import get
from commands.info import info
from commands.restore import restore
from commands.update import update

CLICK_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.version_option()
@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
def cli():
    pass


cli.add_command(connect)
cli.add_command(get)
cli.add_command(info)
cli.add_command(apply)
cli.add_command(edit)
cli.add_command(create)
cli.add_command(update)
cli.add_command(delete)
cli.add_command(restore)
