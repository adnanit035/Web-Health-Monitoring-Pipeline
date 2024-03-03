from aws_cdk import (
    Stage
)

import aws_cdk as cdk
from constructs import Construct

from sprint4_adnan.sprint4_adnan_stack import Sprint4AdnanStack

class AdnanStages(Stage):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create stage for the application stack
        self.stage = Sprint4AdnanStack(self, "AdnanAppStack")
    