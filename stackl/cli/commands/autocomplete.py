import time

import click
from context import StacklContext


def get_stackl_context():
    return StacklContext()


def get_stack_instances(ctx, args, incomplete):
    stack_instances = get_stackl_context().stack_instances_api.get_stack_instances()
    return [si.name for si in stack_instances if si.name.startswith(incomplete)]


def get_environments(ctx, args, incomplete):
    environments = get_stackl_context().infrastructure_base_api.get_infrastructure_base_by_type("environment")
    return [env.name for env in environments if env.name.startswith(incomplete)]


def get_locations(ctx, args, incomplete):
    locations = get_stackl_context().infrastructure_base_api.get_infrastructure_base_by_type("location")
    return [loc.name for loc in locations if loc.name.startswith(incomplete)]


def get_zones(ctx, args, incomplete):
    zones = get_stackl_context().infrastructure_base_api.get_infrastructure_base_by_type("zone")
    return [z.name for z in zones if z.name.startswith(incomplete)]


def get_sats(ctx, args, incomplete):
    sats = get_stackl_context().sat_api.get_stack_application_templates()
    return [s.name for s in sats if s.name.startswith(incomplete)]


def get_sits(ctx, args, incomplete):
    sits = get_stackl_context().sit_api.get_stack_infrastructure_templates()
    return [s.name for s in sits if s.name.startswith(incomplete)]


def get_services(ctx, args, incomplete):
    services = get_stackl_context().services_api.get_services()
    return [s.name for s in services if s.name.startswith(incomplete)]


def get_functional_requirements(ctx, args, incomplete):
    frs = get_stackl_context().functional_requirements_api.get_functional_requirements()
    return [s.name for s in frs if s.name.startswith(incomplete)]


def get_policy_templates(ctx, args, incomplete):
    pts = get_stackl_context().policy_templates_api.get_policy_templates()
    return [pt.name for pt in pts if pt.name.startswith(incomplete)]


def show_progress_bar(stackl_context, instance_name):
    stack_instance = stackl_context.stack_instances_api.get_stack_instance(instance_name)
    with click.progressbar(length=len(stack_instance.status),
                           label='Stack Instance Status') as bar:
        bar.update(0)
        ready = False
        while not ready:
            for status in stack_instance.status:
                if status.status == "FAILED":
                    click.echo(
                        f"Stack instance {stack_instance.name}: service {status.service} on functional-requirement {status.functional_requirement} failed!")
                    exit(1)
                elif status.status == "in_progress":
                    time.sleep(1)
                    stack_instance = stackl_context.stack_instances_api.get_stack_instance(instance_name)
                    ready = False
                    break
                else:
                    bar.update(1)
                    ready = True
