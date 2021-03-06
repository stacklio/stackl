import json

import click
import stackl_client
from commands.autocomplete import show_progress_bar
from context import pass_stackl_context, StacklContext
from urllib3.exceptions import NewConnectionError, MaxRetryError
from stackl_client.exceptions import ApiException, ApiValueError


@click.group()
@click.pass_context
def update(ctx):
    ctx.obj = StacklContext()


@update.command()
@click.option('-p', '--params', default=[], multiple=True)
@click.option('-s', '--secrets', default="{}")
@click.option('-d', '--disable-invocation', is_flag=True)
@click.option('-r', '--replicas', default="{}")
@click.option('-s', '--show-progress', default=False, is_flag=True)
@click.argument('instance-name')
@pass_stackl_context
def instance(stackl_context: StacklContext, params, secrets, replicas, show_progress,
             disable_invocation, instance_name):
    try:
        final_params = {}
        for item in params:
            final_params = {**final_params, **json.loads(item)}
        invocation = stackl_client.models.StackInstanceUpdate(
            stack_instance_name=instance_name,
            params=final_params,
            secrets=json.loads(secrets),
            replicas=json.loads(replicas))
        if disable_invocation:
            invocation.disable_invocation = True
        res = stackl_context.stack_instances_api.put_stack_instance(invocation)
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


@update.command()
@click.option('-p', '--params', default="{}")
@click.option('-i', '--infrastructure-target', required=True)
@click.option('-s', '--service', required=True)
@click.argument('instance-name')
@pass_stackl_context
def outputs(stackl_context: StacklContext, params, infrastructure_target, service, instance_name):
    try:
        outputs_update = stackl_client.models.OutputsUpdate(outputs=json.loads(params), infrastructure_target=infrastructure_target,
                                                    service=service, stack_instance=instance_name)
        stackl_context.outputs_api.add_outputs(outputs_update)
        click.echo("Updated outputs")
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
