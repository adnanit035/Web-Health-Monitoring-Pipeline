from aws_cdk import (
    Stack,
    pipelines,
    aws_codepipeline_actions as actions
)

import aws_cdk as cdk
from constructs import Construct
from resources import constants
from sprint4_adnan.stages_stack import AdnanStages


class MyPipeLineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Defining source code for pipeline.
        source = self.define_source_from_github(constants.GIT_REPO, constants.GIT_BRANCH, "POLL")

        # 2. Build the Code from Source.
        synth = self.build_source("Synth", source, constants.SYNTH_COMMANDS, constants.PIPELINE_CDK_OUTPUT_PATH)

        # 3. Define the pipeline.
        adnan_pipeline = pipelines.CodePipeline(self, "Pipeline_Adnan", synth=synth)

        # 4. Define Stages: Staging have to deploy the code in testing environment.
        beta_stage = AdnanStages(self,
                                 'beta', env=cdk.Environment(account=constants.ACCOUNT_ID, region=constants.REGION))

        prod_stage = AdnanStages(self,
                                 'prod', env=cdk.Environment(account=constants.ACCOUNT_ID, region=constants.REGION))

        # 5. Create test to perform on the beta stage in pre-condition.
        unit_test = self.define_test_case("UnitTest", source, constants.UNIT_TEST_COMMANDS)

        # 6. Create test to perform on the beta stage in pre-condition.
        integration_test = self.define_test_case("IntegrationTest", source, constants.INTEGRATION_TEST_COMMANDS)

        # 7. Add stages to pipeline.
        adnan_pipeline.add_stage(beta_stage, pre=[unit_test], post=[integration_test])
        adnan_pipeline.add_stage(prod_stage, pre=[pipelines.ManualApprovalStep("PromoteToProd")])

    def define_source_from_github(self, source_repo: str, branch: str, trigger: str) -> pipelines.CodePipelineSource:
        """
            Define source code for pipeline.
        Args:
            source_repo: name of my forked repo.
            branch: name of repo's branch
            trigger: None: Never Trigger, WebHook, POLL: trigger pipeline after every poll time.

        Returns: instance of CodePipelineSource
        """
        return pipelines.CodePipelineSource.git_hub(
            repo_string=source_repo,
            branch=branch,
            authentication=cdk.SecretValue.secrets_manager("github-tokenAdnan"),
            trigger=actions.GitHubTrigger(trigger)
        )

    def build_source(self, id: str, input: pipelines.CodePipelineSource, commands: list, output_dir: str) -> pipelines.ShellStep:
        """
            Build the Code from Source.
        Args:
            id: name/id of the step
            input: instance of CodePipelineSource
            commands: list of commands to be executed
            output_dir: directory where the output will be stored.

        Returns: instance of ShellStep

        """
        return pipelines.ShellStep(id,
                                   input=input,
                                   commands=commands,
                                   primary_output_directory=output_dir
                                   )

    def define_test_case(self, id: str, input: pipelines.CodePipelineSource, commands: list) -> pipelines.ShellStep:
        """
            Define test case for stages.
        Args:
            id: name/id of the step
            input: instance of CodePipelineSource
            commands: list of commands to be executed

        Returns: Instance of ShellStep

        """
        return pipelines.ShellStep(id, input=input, commands=commands)
