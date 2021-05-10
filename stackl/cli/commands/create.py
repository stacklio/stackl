import json
import time

import click
import stackl_client
from commands.autocomplete import show_progress_bar
from context import pass_stackl_context, StacklContext
from urllib3.exceptions import NewConnectionError, MaxRetryError
from stackl_client.exceptions import ApiException, ApiValueError


@click.group()
@click.pass_context
def create(ctx):
    ctx.obj = StacklContext()


@create.command()
@click.option('--stack-infrastructure-template')
@click.option('--stack-application-template')
@click.option('-p', '--params', default=[], multiple=True)
@click.option('-t', '--tags', default="{}")
@click.option('-r', '--replicas', default="{}")
@click.option('-s', '--show-progress', default=False, is_flag=True)
@click.argument('instance-name')
@pass_stackl_context
def instance(stackl_context: StacklContext, stack_infrastructure_template,
             stack_application_template, params, tags, replicas, show_progress,
             instance_name):
    try:
        final_params = {}
        for item in params:
            final_params = {**final_params, **json.loads(item)}
        invocation = stackl_client.models.StackInstanceInvocation(
            stack_instance_name=instance_name,
            stack_infrastructure_template=stack_infrastructure_template,
            stack_application_template=stack_application_template,
            replicas=json.loads(replicas),
            params=final_params,
            tags=json.loads(tags))
        res = stackl_context.stack_instances_api.post_stack_instance(invocation)
        click.echo(res)
        if show_progress:
            show_progress_bar(stackl_context, instance_name)
    except ApiException as e:
        click.echo(e.body)
        exit(1)
    except ApiValueError as e:
        click.echo(e.body)
        exit(1)
    except (NewConnectionError, MaxRetryError) as e:
        click.echo("Unable to connect to Stackl host")
        click.echo(e)
        exit(1)



@create.command()
@click.argument("type", required=True)
@click.argument("name", required=True)
@pass_stackl_context
def snapshot(stackl_context: StacklContext, type, name):
    result = stackl_context.snapshot_api.create_snapshot(type, name)
    click.echo(result)


@create.command()
@click.option('-p', '--policy-file', type=click.File())
@click.option('-i', '--inputs', type=click.STRING, default="")
@click.argument('policy-name')
@pass_stackl_context
def policy(stackl_context: StacklContext, policy_file, policy_name, inputs):
    inputs = [i.strip() for i in inputs.split(',')]
    policy = stackl_client.models.PolicyTemplate(name=policy_name,
                                  type="policy",
                                  category="configs",
                                  description="policy through cli",
                                  policy=policy_file.read(),
                                  inputs=inputs)
    res = stackl_context.policies_api.put_policy(policy)
    click.echo(res)
