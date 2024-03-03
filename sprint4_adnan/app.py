#!/usr/bin/env python3
import aws_cdk as cdk
from resources import constants

from sprint4_adnan.pipeline_adnan_stack import MyPipeLineStack

from sprint4_adnan.sprint4_adnan_stack import Sprint4AdnanStack

app = cdk.App()
MyPipeLineStack(app, "AdnanPipelineStack",
# Sprint4AdnanStack(app, "Sprint4AdnanStack",
                  # If you don't specify 'env', this stack will be environment-agnostic.
                  # Account/Region-dependent features and context lookups will not work,
                  # but a single synthesized template can be deployed anywhere.

                  # Uncomment the next line to specialize this stack for the AWS Account
                  # and Region that are implied by the current CLI configuration.

                  # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

                  # Uncomment the next line if you know exactly what Account and Region you
                  # want to deploy the stack to. */

                  env=cdk.Environment(account=constants.ACCOUNT_ID, region=constants.REGION)

                  # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
                  )
app.synth()
