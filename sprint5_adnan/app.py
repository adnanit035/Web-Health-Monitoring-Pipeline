#!/usr/bin/env python3
import aws_cdk as cdk
from resources import constants

from sprint5_adnan.pipeline_adnan_stack import MyPipeLineStack

from sprint5_adnan.sprint5_adnan_stack import Sprint5AdnanStack

app = cdk.App()
# MyPipeLineStack(app, "AdnanPipelineStack",
Sprint5AdnanStack(app, "Sprint5AdnanStack",
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
