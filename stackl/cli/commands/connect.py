import os
from pathlib import Path

import click
from context import get_config_path


@click.command()
@click.argument('host', required=True)
def connect(host):
    homedir = str(Path.home())
    if len(homedir) == 0:
        homedir = os.getcwd()
    if not os.path.exists(homedir + os.sep + '.stackl'):
        os.makedirs(homedir + os.sep + '.stackl')
    with open(get_config_path(), 'w+') as stackl_config:
        stackl_config.write(host)



