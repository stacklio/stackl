import os
import click
from context import StacklContext
import stackl_client
import yaml


@click.option('-d', '--directory', type=click.Path(exists=True))
@click.command()
def generate(directory):
    # stackl_context = StacklContext()
    # about_api = stackl_client.AboutApi(api_client=stackl_context.api_client)
    sub_dirs = [
        "environments", "locations", "zones", "sats", "sits",
        "functional-requirements", "services"
    ]
    directories = [os.path.join(directory, x) for x in sub_dirs]
    for d in directories:
        try:
            os.mkdir(d)
        except FileExistsError as e:
            click.echo(f"Directory {d} already exists")

    environment = stackl_client.InfrastructureBaseDocument(
        name="development",
        category="configs",
        type="environment",
        description="Generated enviroment document for development",
        params={"test": "value"},
        secrets={})
    with open(os.path.join(directory, "environments/development.yml"),
              'w') as environment_file:
        yaml.dump(environment.to_dict(), environment_file)

    location = stackl_client.InfrastructureBaseDocument(
        name="brussels",
        category="configs",
        type="location",
        description="Generated location document for brussels")
    with open(os.path.join(directory, "locations/brussels.yml"),
              'w') as location_file:
        yaml.dump(location.to_dict(), location_file)

    zone = stackl_client.InfrastructureBaseDocument(
        name="blue",
        category="configs",
        type="zone",
        description="Generated zone document for blue")
    with open(os.path.join(directory, "zones/blue.yml"), 'w') as zone_file:
        yaml.dump(zone.to_dict(), zone_file)

    infrastructureTarget = stackl_client.InfrastructureTarget(
        environment="development", location="brussels", zone="blue")
    sit = stackl_client.StackInfrastructureTemplate(
        name="example-sit",
        category="configs",
        description="Generated sit",
        infrastructure_targets=[infrastructureTarget])
    with open(os.path.join(directory, "sits/example-sit.yml"),
              'w') as sit_file:
        yaml.dump(sit.to_dict(), sit_file)

    invocation = stackl_client.Invocation(tool="ansible",
                                          image="add-fdi-here",
                                          description="demo invocation")
    fr = stackl_client.FunctionalRequirement(
        name="demo-functional-requirement",
        category="configs",
        invocation={"general": invocation})
    with open(
            os.path.join(
                directory,
                "functional-requirements/demo-functional-requirement.yml"),
            'w') as fr_file:
        yaml.dump(fr.to_dict(), fr_file)

    service = stackl_client.Service(
        name="demo-service",
        category="configs",
        functional_requirements=["demo-functional-requirement"])
    with open(os.path.join(directory, "services/demo-service.yml"),
              'w') as service_file:
        yaml.dump(service.to_dict(), service_file)

    sat_service = stackl_client.StackApplicationTemplateService(
        name="demo-service-name",
        service="demo-service",
    )
    sat = stackl_client.StackApplicationTemplate(name="demo-sat",
                                                 category="configs",
                                                 services=[sat_service])
    with open(os.path.join(directory, "sats/demo-sat.yml"), 'w') as sat_file:
        yaml.dump(sat.to_dict(), sat_file)
