from aws_cdk import (
    Stage
)

import aws_cdk as cdk
from constructs import Construct

from sprint5_adnan.sprint5_adnan_stack import Sprint5AdnanStack

class AdnanStages(Stage):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create stage for the application stack
        self.stage = Sprint5AdnanStack(self, "AdnanAppStack")
    