import os

import click


@click.command()
@click.argument('host', required=True)
def connect(host):
    homedir = os.path.expanduser('~')
    if not os.path.exists(homedir + os.sep + '.stackl'):
        os.makedirs(homedir + os.sep + '.stackl')
    with open(config_path, 'w+') as stackl_config:
        stackl_config.write(host)


config_path = os.path.expanduser('~') + os.sep + '.stackl' + os.sep + 'config'
