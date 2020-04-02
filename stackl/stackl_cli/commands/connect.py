import os
from pathlib import Path
import click


@click.command()
@click.argument('host', required=True)
def connect(host):
    homedir = str(Path.home())
    if len(homedir) == 0:
        homedir = os.getcwd()
    if not os.path.exists(homedir + os.sep + '.stackl'):
        os.makedirs(homedir + os.sep + '.stackl')
    with open(config_path, 'w+') as stackl_config:
        stackl_config.write(host)


if len(str(Path.home())) == 0:
    config_path = os.getcwd() + os.sep + '.stackl' + os.sep + 'config'
else:
    config_path = str(Path.home()) + os.sep + '.stackl' + os.sep + 'config'
