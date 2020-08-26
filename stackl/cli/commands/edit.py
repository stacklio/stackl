import click
import yaml
from commands.autocomplete import get_zones, get_locations, get_environments, get_services, get_functional_requirements, \
    get_policy_templates, get_sits, get_sats

from context import pass_stackl_context, StacklContext

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


@click.group()
@click.pass_context
def edit(ctx):
    ctx.obj = StacklContext()


@edit.command()
@click.argument('name', autocompletion=get_zones)
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
@click.argument('name', autocompletion=get_locations)
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
@click.argument('name', autocompletion=get_environments)
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
@click.argument('name', autocompletion=get_services)
@pass_stackl_context
def service(stackl_context: StacklContext, name):
    service = stackl_context.services_api.get_service_by_name(name)
    new_service = click.edit(yaml.dump(service.to_dict(), Dumper=Dumper))
    if new_service is not None:
        new_service = yaml.load(new_service, Loader=yaml.FullLoader)
        stackl_context.services_api.put_service(new_service)
        click.echo("Service  updated")
    else:
        click.echo("No changes, document not modified")


@edit.command()
@click.argument('name', autocompletion=get_functional_requirements)
@pass_stackl_context
def functional_requirement(stackl_context: StacklContext, name):
    functional_requirement = stackl_context.functional_requirements_api.get_functional_requirement_by_name(name)
    new_functional_requirement = click.edit(yaml.dump(functional_requirement.to_dict(), Dumper=Dumper))
    if new_functional_requirement is not None:
        new_functional_requirement = yaml.load(new_functional_requirement, Loader=yaml.FullLoader)
        stackl_context.functional_requirements_api.put_functional_requirement(new_functional_requirement)
        click.echo("Functional Requirement updated")
    else:
        click.echo("No changes, document not modified")


@edit.command()
@click.argument('name', autocompletion=get_policy_templates)
@pass_stackl_context
def policy_template(stackl_context: StacklContext, name):
    policy_template = stackl_context.policy_templates_api.get_policy_template_by_name(name)
    new_policy_template = click.edit(yaml.dump(policy_template.to_dict(), Dumper=Dumper))
    if new_policy_template is not None:
        new_policy_template = yaml.load(new_policy_template, Loader=yaml.FullLoader)
        stackl_context.policy_templates_api.put_policy_template(new_policy_template)
        click.echo("Policy template updated")
    else:
        click.echo("No changes, document not modified")


@edit.command()
@click.argument('name', autocompletion=get_sits)
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
@click.argument('name', autocompletion=get_sats)
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
