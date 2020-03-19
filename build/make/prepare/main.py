import click
import yaml
from jinja2 import Environment, FileSystemLoader


def render_jinja(src, dest, **kw):
    jinja_env = Environment(loader=FileSystemLoader('/templates'), trim_blocks=True, lstrip_blocks=True)
    t = jinja_env.get_template(src)
    with open(dest, 'w') as f:
        f.write(t.render(**kw))
    print("Generated configuration file: %s" % dest)


def parse_yaml_config(config_file_path):
    config_dict = {}
    with open(config_file_path) as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)

    http_config = configs.get('http') or {}
    config_dict['http_port'] = http_config.get('port', 80)

    datastore_config = configs.get('datastore')
    config_dict['datastore_type'] = datastore_config.get('type')
    config_dict['datastore_lfs_volume'] = datastore_config.get('lfs_volume', '')

    datastore_config = configs.get('opa')
    config_dict['opa_files_location'] = datastore_config.get('opa_files_location', '')

    task_broker_config = configs.get('task_broker')
    config_dict['task_broker_type'] = task_broker_config.get('type')

    message_channel_config = configs.get('message_channel')
    config_dict['message_channel_type'] = message_channel_config.get('type')

    agent_broker_config = configs.get('agent_broker')
    config_dict['agent_broker_type'] = agent_broker_config.get('type')
    config_dict['agent_host'] = agent_broker_config.get('host', '')

    return config_dict

@click.command()
@click.option('--conf', help="the path of the stackl configuration file")
def main(conf):
    config_dict = parse_yaml_config(conf)
    render_jinja('docker-compose.yml.j2', '/output/docker-compose.yml', **config_dict)


if __name__ == '__main__':
    main()
