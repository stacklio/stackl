from context import StacklContext

stackl_context = StacklContext()


def get_stack_instances(ctx, args, incomplete):
    stack_instances = stackl_context.stack_instances_api.get_stack_instances()
    return [si.name for si in stack_instances if si.name.startswith(incomplete)]


def get_environments(ctx, args, incomplete):
    environments = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type("environment")
    return [env.name for env in environments if env.name.startswith(incomplete)]


def get_locations(ctx, args, incomplete):
    locations = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type("location")
    return [loc.name for loc in locations if loc.name.startswith(incomplete)]


def get_zones(ctx, args, incomplete):
    zones = stackl_context.infrastructure_base_api.get_infrastructure_base_by_type("zone")
    return [z.name for z in zones if z.name.startswith(incomplete)]


def get_sats(ctx, args, incomplete):
    sats = stackl_context.sat_api.get_stack_application_templates()
    return [s.name for s in sats if s.name.startswith(incomplete)]


def get_sits(ctx, args, incomplete):
    sits = stackl_context.sit_api.get_stack_infrastructure_templates()
    return [s.name for s in sits if s.name.startswith(incomplete)]


def get_services(ctx, args, incomplete):
    services = stackl_context.services_api.get_services()
    return [s.name for s in services if s.name.startswith(incomplete)]


def get_functional_requirements(ctx, args, incomplete):
    frs = stackl_context.functional_requirements_api.get_functional_requirements()
    return [s.name for s in frs if s.name.startswith(incomplete)]


def get_policy_templates(ctx, args, incomplete):
    pts = stackl_context.policy_templates_api.get_policy_templates()
    return [pt.name for pt in pts if pt.name.startswith(incomplete)]
