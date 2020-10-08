import click

from context import pass_stackl_context, StacklContext


@click.group()
@click.pass_context
def delete(ctx):
    ctx.obj = StacklContext()


@delete.command()
@click.argument('instance-name')
@click.option('--force', default=False, is_flag=True)
@pass_stackl_context
def instance(stackl_context: StacklContext, instance_name, force):
    res = stackl_context.stack_instances_api.delete_stack_instance(
        instance_name, force=force)
    click.echo(res)


@delete.command()
@click.argument('snapshot-name')
@pass_stackl_context
def snapshot(stackl_context: StacklContext, snapshot_name):
    res = stackl_context.snapshot_api.delete_snapshot(snapshot_name)
    click.echo(res)


@delete.command()
@click.argument('environment-name')
@pass_stackl_context
def environment(stackl_context: StacklContext, environment_name):
    res = stackl_context.infrastructure_base_api.delete_infrastructure_base(
        "environment", environment_name)
    click.echo(res)


@delete.command()
@click.argument('location-name')
@pass_stackl_context
def location(stackl_context: StacklContext, location_name):
    res = stackl_context.infrastructure_base_api.delete_infrastructure_base(
        "location", location_name)
    click.echo(res)


@delete.command()
@click.argument('zone-name')
@pass_stackl_context
def zone(stackl_context: StacklContext, zone_name):
    res = stackl_context.infrastructure_base_api.delete_infrastructure_base(
        "zone", zone_name)
    click.echo(res)


@delete.command()
@click.argument('sat-name')
@pass_stackl_context
def sat(stackl_context: StacklContext, sat_name):
    res = stackl_context.sat_api.delete_stack_application_template(sat_name)
    click.echo(res)


@delete.command()
@click.argument('sit-name')
@pass_stackl_context
def sit(stackl_context: StacklContext, sit_name):
    res = stackl_context.sit_api.delete_stack_infrastructure_template(sit_name)
    click.echo(res)


@delete.command()
@click.argument('service-name')
@pass_stackl_context
def service(stackl_context: StacklContext, service_name):
    res = stackl_context.services_api.delete_service(service_name)
    click.echo(res)


@delete.command()
@click.argument('functional-requirement-name')
@pass_stackl_context
def functional_requirement(stackl_context: StacklContext,
                           functional_requirement_name):
    res = stackl_context.functional_requirements_api.delete_functional_requirement(
        functional_requirement_name)
    click.echo(res)


@delete.command()
@click.argument('policy-template-name')
@pass_stackl_context
def policy_template(stackl_context: StacklContext, policy_template_name):
    res = stackl_context.policy_templates_api.delete_policy_template(
        policy_template_name)
    click.echo(res)
