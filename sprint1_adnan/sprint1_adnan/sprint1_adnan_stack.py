from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    RemovalPolicy
    # aws_sqs as sqs,
)
from constructs import Construct

class Sprint1AdnanStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hello_lambda = lambda_.Function(self, "Hello-lambda-Adnan",
            code=lambda_.Code.from_asset("./resources"),
            handler="hello_lambda.handler",
            runtime=lambda_.Runtime.PYTHON_3_6
        )
        
        hello_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        