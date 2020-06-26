import click
import yaml

from context import pass_stackl_context, StacklContext

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


@click.group()
def edit():
    pass


@edit.command()
@click.argument('name')
@pass_stackl_context
def zone(stackl_context: StacklContext, name):
    zone = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type_and_name(
        "zone", name)
    new_zone = click.edit(yaml.dump(zone.to_dict(), Dumper=Dumper))
    if new_zone is not None:
        new_zone = yaml.load(new_zone, Loader=yaml.FullLoader)
        stackl_context.infrastructure_base_api.put_infrastructure_base(
            new_zone)
        click.echo("Zone updated")
    else:
        click.echo("No changes, document not modified")


@edit.command()
@click.argument('name')
@pass_stackl_context
def location(stackl_context: StacklContext, name):
    location = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type_and_name(
        "location", name)
    new_location = click.edit(yaml.dump(location.to_dict(), Dumper=Dumper))
    if new_location is not None:
        new_location = yaml.load(new_location, Loader=yaml.FullLoader)
        stackl_context.infrastructure_base_api.put_infrastructure_base(
            new_location)
        click.echo("Location updated")
    else:
        click.echo("No changes, document not modified")


@edit.command()
@click.argument('name')
@pass_stackl_context
def environment(stackl_context: StacklContext, name):
    environment = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type_and_name(
        "environment", name)
    new_environment = click.edit(
        yaml.dump(environment.to_dict(), Dumper=Dumper))
    if new_environment is not None:
        new_environment = yaml.load(new_environment, Loader=yaml.FullLoader)
        stackl_context.infrastructure_base_api.put_infrastructure_base(
            new_environment)
        click.echo("Environment updated")
    else:
        click.echo("No changes, document not modified")


@edit.command()
@click.argument('name')
@pass_stackl_context
def sit(stackl_context: StacklContext, name):
    sit = stackl_context.sit_api.get_stack_infrastructure_template_by_name(
        name)
    new_sit = click.edit(yaml.dump(sit.to_dict(), Dumper=Dumper))
    if new_sit is not None:
        new_sit = yaml.load(new_sit, Loader=yaml.FullLoader)
        stackl_context.infrastructure_base_api.put_infrastructure_base(new_sit)
        click.echo("SIT updated")
    else:
        click.echo("No changes, document not modified")


@edit.command()
@click.argument('name')
@pass_stackl_context
def sat(stackl_context: StacklContext, name):
    sat = stackl_context.sat_api.get_stack_infrastructure_template_by_name(
        name)
    new_sat = click.edit(yaml.dump(sat.to_dict(), Dumper=Dumper))
    if new_sat is not None:
        new_sat = yaml.load(new_sat, Loader=yaml.FullLoader)
        stackl_context.infrastructure_base_api.put_infrastructure_base(new_sat)
        click.echo("SAT updated")
    else:
        click.echo("No changes, document not modified")
