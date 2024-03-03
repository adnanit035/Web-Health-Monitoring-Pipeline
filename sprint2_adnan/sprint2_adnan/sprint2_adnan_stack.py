from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    RemovalPolicy,
    aws_events_targets as targets_,
    aws_events as events_,
    aws_iam as iam_,
    aws_cloudwatch as cloudwatch_,
    aws_sns as sns_,
    aws_sns_subscriptions as sns_subscriptions,
    aws_cloudwatch_actions as actions_,
    aws_s3 as s3_,
    aws_s3_deployment as s3deploy_,

    # aws_sqs as sqs,
)

from resources import constants
from constructs import Construct


class Sprint2AdnanStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a role by adding CLOUDWATCH_POLICY for cloudwatch access
        my_role = self.create_role("CWRole", "This is cloudwatch access role", constants.CLOUDWATCH_POLICY)

        # Create a lambda function to do cron job on list of websites
        WH_lambda = self.create_lambda("AdnanWHLambda", "./resources", "web_health_checker_lambda.lambda_handler",
                                       my_role)

        # Apply removal policy to destroy all instances of the lambda function when stack is deleted
        WH_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # Create a rule to schedule lambda function to run every 1 minutes
        rule = events_.Rule(self, "AdnanWHRule",
                            description="This my WH rule that triggers lambda after every 1 minute.",
                            enabled=True,
                            schedule=events_.Schedule.rate(Duration.minutes(1)),
                            targets=[targets_.LambdaFunction(WH_lambda)]
                            )

        #########################################################################
        # Set Alarms and Actions on CloudWatch for Lambda Function
        #########################################################################
        # 1. Create a topic to send notifications to SNS
        topic = sns_.Topic(self, id="AdnanWHTopic", display_name="Web-Health")

        # 2. Add a sns subscription to send notifications to adnan.irshad.skipq@gmail.com
        topic.add_subscription(sns_subscriptions.EmailSubscription("adnan.irshad.skipq@gmail.com"))

        # 3. Loop through all websites and create alarms for each website
        for url in constants.URL_TO_MONITOR:
            # Create availability alarm for each website
            self.create_alarm(metric_name=constants.AVAIL_METRIC_NAME + url,
                              namespace=constants.ORION_URL_NAME_SPACE,
                              url=url,
                              alarm_id="AI-Availability-Alarm_" + url,
                              comparison_operator=cloudwatch_.ComparisonOperator.LESS_THAN_THRESHOLD,
                              threshold=1,
                              evaluation_periods=1,
                              topic=topic
                              )

            # Create latency alarm for each website
            self.create_alarm(metric_name=constants.LATENCY_METRIC_NAME + url,
                              namespace=constants.ORION_URL_NAME_SPACE,
                              url=url,
                              alarm_id="AI-Latency-Alarm_" + url,
                              comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
                              threshold=0.3,
                              evaluation_periods=1,
                              topic=topic
                              )
        #########################################################################
        # *** End of Set Alarms and Actions on CloudWatch for Lambda Function ***
        #########################################################################

        #########################################################################
        # Create S3 Bucket and deploy files to it
        #########################################################################
        # 1. Create a S3 bucket to store the globals variables store in constants.py
        bucket = s3_.Bucket(self, id="Adnan-ConstantsFileBucket",
                            versioned=True,
                            removal_policy=RemovalPolicy.DESTROY,
                            auto_delete_objects=True,
                            public_read_access=True, 
                            )

        # 2. Grants read/write permissions for this bucket and it’s contents to an IAM principal (Role/Group/User).
        bucket.grant_read_write(WH_lambda)
        # 3. Create a deployment to deploy the bucket
        deployment = s3deploy_.BucketDeployment(self, "Adnan-ConstantsBucketDeploy",
                                                sources=[s3deploy_.Source.asset("./resources",
                                                                                exclude=["*", "!constants.py"])],
                                                destination_bucket=bucket,
                                                retain_on_delete=False
                                                )

        # 4. Add resource policy to allow only constansts.py file to be uploaded
        result = bucket.add_to_resource_policy(
            iam_.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[bucket.arn_for_objects("constants.py")],
                principals=[iam_.AccountRootPrincipal()]
            )
        )
        #############################################################################
        # ********** End of creating S3 Bucket and deploying files to it ************
        #############################################################################

    def create_role(self, role_id, description, policy):
        """
                Function to create role(s) for the lambda function
            :param role_id: describe the id of role
            :param description: describe the description of role
            :param policy: describe the policy of role

            :return: an instance of role
        """
        role = iam_.Role(self, role_id,
                         assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
                         description=description
                         )

        # Add policy to the role
        role.add_managed_policy(
            iam_.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        role.add_managed_policy(iam_.ManagedPolicy.from_aws_managed_policy_name(policy))

        return role

    def create_lambda(self, lambda_id, assets, handler, role):
        """
            Function to create lambda function
        :param lambda_id: describe the id of lambda function
        :param assets: describe the assets of lambda function
        :param handler: describe the handler of lambda function
        :param role: describe the role of lambda function

        :return: an instance of lambda function
        """
        return lambda_.Function(self, lambda_id,
                                code=lambda_.Code.from_asset(assets),
                                handler=handler,
                                role=role,
                                runtime=lambda_.Runtime.PYTHON_3_6,
                                timeout=Duration.seconds(60)  # Timeout after 60 seconds by default it is 3 seconds.
                                )

    def create_alarm(self, metric_name, namespace, url, alarm_id, comparison_operator, threshold, evaluation_periods,
                     topic):
        """
            Function to create alarms
        :param metric_name: describe the metric name of alarm
        :param namespace: describe the namespace for alarm
        :param url: describe the url for alarm to be used in dimensions_map
        :param alarm_id: describe the id of alarm
        :param comparison_operator: describe the comparison operator to make decision
        :param threshold: describe the threshold for alarm
        :param evaluation_periods: describe the evaluation periods for alarm
        :param topic: describe the subscription topic for alarm to send notifications

        :return: an instance of alarm
        """
        metric = cloudwatch_.Metric(
            namespace=namespace,
            metric_name=metric_name,
            dimensions_map={
                "URL": url
            },
            period=Duration.seconds(60)
        )

        alarm = cloudwatch_.Alarm(self, alarm_id,
                                  comparison_operator=comparison_operator,
                                  threshold=threshold,
                                  evaluation_periods=evaluation_periods,
                                  metric=metric
                                  )

        # Create an OpsItem with specific severity and category when alarm triggers
        alarm.add_alarm_action(actions_.SnsAction(topic))