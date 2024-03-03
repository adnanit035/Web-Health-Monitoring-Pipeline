from aws_cdk import (
    Stage
)

import aws_cdk as cdk
from constructs import Construct

from sprint3_adnan.sprint3_adnan_stack import Sprint3AdnanStack

class AdnanStages(Stage):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create stage for the application stack
        self.stage = Sprint3AdnanStack(self, "AdnanAppStack")
        
