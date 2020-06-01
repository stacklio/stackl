import json

import click
import stackl_client

from context import pass_stackl_context, StacklContext


@click.group()
def create():
    pass


@create.command()
@click.option('--stack-infrastructure-template')
@click.option('--stack-application-template')
@click.option('-p', '--params', default="{}")
@click.option('-t', '--tags', default="{}")
@click.option('-r', '--replicas', default="{}")
@click.argument('instance-name')
@pass_stackl_context
def instance(stackl_context: StacklContext, stack_infrastructure_template,
             stack_application_template, params, tags, replicas,
             instance_name):
    invocation = stackl_client.StackInstanceInvocation(
        name=instance_name,
        stack_infrastructure_template=stack_infrastructure_template,
        stack_application_template=stack_application_template,
        replicas=json.loads(replicas),
        params=json.loads(params),
        tags=json.loads(tags))
    res = stackl_context.stack_instances_api.post_stack_instance(invocation)
    click.echo(res)


@create.command()
@click.option('-p', '--policy-file', type=click.File())
@click.option('-i', '--inputs', type=click.STRING, default="")
@click.argument('policy-name')
@pass_stackl_context
def policy(stackl_context: StacklContext, policy_file, policy_name, inputs):
    inputs = [i.strip() for i in inputs.split(',')]
    policy = stackl_client.Policy(name=policy_name,
                                  type="policy",
                                  category="configs",
                                  description="policy through cli",
                                  policy=policy_file.read(),
                                  inputs=inputs)
    res = stackl_context.policies_api.put_policy(policy)
    click.echo(res)
