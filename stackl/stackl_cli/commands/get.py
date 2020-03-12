import json

import click
import yaml
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from context import pass_stackl_context, StacklContext


@click.group()
def get():
    pass


def parse(stackl_object, output_type):
    if output_type == 'yaml':
        return yaml.dump(stackl_object.to_dict(), Dumper=Dumper)
    elif output_type == 'json':
        return json.dumps(stackl_object.to_dict(), sort_keys=True,
                          indent=4, separators=(',', ': '))
    else:
        return "Output type not supported"


@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False)
@pass_stackl_context
def instance(stackl_context: StacklContext, output, name):
    stack_instance = stackl_context.stack_instances_api.get_stack_instance(name)
    click.echo(parse(stack_instance, output))
