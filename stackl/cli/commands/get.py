import json

import click
import yaml
from commands.autocomplete import get_stack_instances, get_environments, get_locations, get_zones, get_sats, get_sits, \
    get_services, get_functional_requirements, get_policy_templates
from stackl_client import StackInfrastructureTemplate, ApiException
from tabulate import tabulate

try:
    from yaml import CDumper as Dumper, SafeDumper
except ImportError:
    from yaml import Dumper

from context import pass_stackl_context, StacklContext


@click.group()
@click.pass_context
def get(ctx):
    ctx.obj = StacklContext()


def table_data(stackl_object):
    table = []
    if isinstance(stackl_object, list):
        if stackl_object and isinstance(stackl_object[0],
                                        StackInfrastructureTemplate):
            for so in stackl_object:
                table.append([so.name, "", "", ""])
                for it in so.infrastructure_targets:
                    table.append(["", it.environment, it.location, it.zone])
                return table, ["name", "environment", "location", "zone"]
        else:
            for so in stackl_object:
                table.append([so.name])
            return table, ["name"]
    else:
        if isinstance(stackl_object, StackInfrastructureTemplate):
            table.append([stackl_object.name, "", "", ""])
            for it in stackl_object.infrastructure_targets:
                table.append(["", it.environment, it.location, it.zone])
            return table, ["name", "environment", "location", "zone"]
        else:
            table.append([stackl_object.name])
            return table, ["name"]


def parse(stackl_object, output_type):
    if output_type is None:
        data, headers = table_data(stackl_object)
        return tabulate(data, headers)
    else:
        if isinstance(stackl_object, list):
            table = []
            for so in stackl_object:
                table.append(so.to_dict())
            dump_object = table
        else:
            dump_object = stackl_object.to_dict()
        if output_type == 'yaml':
            return yaml.dump(dump_object, Dumper=Dumper)
        elif output_type == 'json':
            return json.dumps(dump_object,
                              sort_keys=True,
                              indent=4,
                              separators=(',', ': '))
        else:
            return "Output type not supported"



@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False, autocompletion=get_stack_instances)
@pass_stackl_context
def instance(stackl_context: StacklContext, output, name):
    try:
        if name is None:
            env = stackl_context.stack_instances_api.get_stack_instances()
        else:
            env = stackl_context.stack_instances_api.get_stack_instance(name)
        click.echo(parse(env, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False, autocompletion=get_environments)
@pass_stackl_context
def environment(stackl_context: StacklContext, output, name):
    document_type = "environment"
    try:
        if name is None:
            env = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type(
                document_type)
        else:
            env = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type_and_name(
                document_type, name)
        click.echo(parse(env, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False, autocompletion=get_locations)
@pass_stackl_context
def location(stackl_context: StacklContext, output, name):
    document_type = "location"
    try:
        if name is None:
            env = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type(
                document_type)
        else:
            env = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type_and_name(
                document_type, name)
        click.echo(parse(env, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False, autocompletion=get_zones)
@pass_stackl_context
def zone(stackl_context: StacklContext, output, name):
    document_type = "zone"
    try:
        if name is None:
            env = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type(
                document_type)
        else:
            env = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type_and_name(
                document_type, name)
        click.echo(parse(env, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False, autocompletion=get_sats)
@pass_stackl_context
def sat(stackl_context: StacklContext, output, name):
    try:
        if name is None:
            sat = stackl_context.sat_api.get_stack_application_templates()
        else:
            sat = stackl_context.sat_api.get_stack_application_template_by_name(
                name)
        click.echo(parse(sat, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False, autocompletion=get_sits)
@pass_stackl_context
def sit(stackl_context: StacklContext, output, name):
    try:
        if name is None:
            sit = stackl_context.sit_api.get_stack_infrastructure_templates()
        else:
            sit = stackl_context.sit_api.get_stack_infrastructure_template_by_name(
                name)
        click.echo(parse(sit, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False, autocompletion=get_services)
@pass_stackl_context
def service(stackl_context: StacklContext, output, name):
    try:
        if name is None:
            env = stackl_context.services_api.get_services()
        else:
            env = stackl_context.services_api.get_service_by_name(name)
        click.echo(parse(env, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False, autocompletion=get_functional_requirements)
@pass_stackl_context
def functional_requirement(stackl_context: StacklContext, output, name):
    try:
        if name is None:
            env = stackl_context.functional_requirements_api.get_functional_requirements(
            )
        else:
            env = stackl_context.functional_requirements_api.get_functional_requirement_by_name(
                name)
        click.echo(parse(env, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument('name', required=False, autocompletion=get_policy_templates)
@pass_stackl_context
def policy_template(stackl_context: StacklContext, output, name):
    try:
        if name is None:
            env = stackl_context.policy_templates_api.get_policy_templates()
        else:
            env = stackl_context.policy_templates_api.get_policy_template_by_name(
                name)
        click.echo(parse(env, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument('type')
@click.argument('name')
@pass_stackl_context
def snapshots(stackl_context: StacklContext, type, name, output):
    try:
        snapshots = stackl_context.snapshot_api.get_snapshots(type, name)
        click.echo(parse(snapshots, output))
    except ApiException as e:
        click.echo(e.body)


@get.command()
@click.option('-o', '--output')
@click.argument("name")
@pass_stackl_context
def snapshot(stackl_context: StacklContext, name, output):
    try:
        snapshot = stackl_context.snapshot_api.get_snapshot(name)
        click.echo(parse(snapshot, output))
    except ApiException as e:
        click.echo(e.body)
