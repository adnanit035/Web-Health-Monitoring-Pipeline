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
    aws_codedeploy as codedeploy_,
    aws_dynamodb as dynamodb_,
    aws_apigateway as gateway_
)
from constructs import Construct
from resources import URLs
from resources import constants


class Sprint4AdnanStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #########################################################################
        # Define Role for Lambda Function
        #########################################################################
        lambda_role = self.create_lambda_role("AdnanHWLambdaRole")

        #########################################################################
        # Define Lambdas Functions
        #########################################################################
        # 1. Create a lambda function to do cron job on list of websites
        WH_lambda = self.create_lambda("AdnanWHLambda", "./resources", "web_health_checker_lambda.lambda_handler",
                                       lambda_role)
        # 2. Create a lambda function to save the logs to dynamodb table
        db_lambda = self.create_lambda("AdnanDBLambda", "./resources", "db_lambda.lambda_handler", lambda_role)
        # 3. create a lambda to download data from bucket and save to dynamodb table
        bucket_to_db_handler_lambda = self.create_lambda('AdnanBucketToDBHandlerLambda', './resources',
                                                         'BucketToDB.lambda_handler', lambda_role)
        # 4. Create a CRUD API lambda function
        api_handler_lambda = self.create_lambda("AdnanCrudApiHandlerLambda", "./resources", "ApiHandler.lambda_handler",
                                                lambda_role)

        # Apply removal policy to destroy all instances of the lambda function when stack is deleted
        WH_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        db_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        bucket_to_db_handler_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        api_handler_lambda.apply_removal_policy(RemovalPolicy.DESTROY)

        #########################################################################
        # Create DynamoDB Tables
        #########################################################################
        # 1. dynamodb table to Store Alarms Logs
        dynamodb_alrams_table = dynamodb_.Table(
            self,
            id="AdnanAlarmsTable",
            partition_key=dynamodb_.Attribute(name="id", type=dynamodb_.AttributeType.STRING),
            # add a sort key to the table
            sort_key=dynamodb_.Attribute(name="timestamp", type=dynamodb_.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        # 2. dynamodb table to download data from s3 bucket and save to dynamodb table
        # dynamodb_urls_table = dynamodb_.Table(
        #     self,
        #     id="AdnanURLsTable",
        #     partition_key=dynamodb_.Attribute(name="url", type=dynamodb_.AttributeType.STRING),
        #     removal_policy=RemovalPolicy.DESTROY
        # )
        dynamodb_urls_table = dynamodb_.Table(
            self,
            id="AdnanURLsTable",
            removal_policy=RemovalPolicy.DESTROY,
            partition_key=dynamodb_.Attribute(name="URL_ID", type=dynamodb_.AttributeType.STRING)
        )

        # grant permission to lambda function to read/write to dynamodb tables
        dynamodb_alrams_table.grant_full_access(db_lambda)
        dynamodb_urls_table.grant_full_access(bucket_to_db_handler_lambda)
        dynamodb_urls_table.grant_full_access(api_handler_lambda)

        #########################################################################
        # Set Event Rule on WH Lambda
        #########################################################################
        # Apply event rule on WH lambda to schedule lambda function to run every 10 minutes
        events_.Rule(self, "AdnanWHRule",
                     description="This is my WH rule that triggers lambda after every 3 hours.",
                     enabled=True,
                     schedule=events_.Schedule.rate(Duration.hours(3)),
                     targets=[targets_.LambdaFunction(WH_lambda)]
                     )

        #########################################################################
        # Set Alarms and Actions on CloudWatch for Lambda Function
        #########################################################################
        # 1. Create a topic to send notifications to SNS
        topic = sns_.Topic(self, id="AdnanWHTopic", display_name="Web-Health")
        topic.apply_removal_policy(RemovalPolicy.DESTROY)

        # 2. Add a sns subscription to send notifications to adnan.irshad.skipq@gmail.com
        topic.add_subscription(sns_subscriptions.EmailSubscription(constants.EMAIL_ADDRESS))
        topic.add_subscription(sns_subscriptions.LambdaSubscription(db_lambda))
        topic.add_subscription(sns_subscriptions.LambdaSubscription(bucket_to_db_handler_lambda))

        # 3. Loop through all websites and create alarms for each website
        for url in URLs.URLs_TO_MONITOR:
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
                              threshold=0.65,
                              evaluation_periods=1,
                              topic=topic
                              )

        #########################################################################
        # Create S3 Bucket and deploy files to it
        #########################################################################
        # 1. Create a S3 bucket to store the globals variables store in URLs.py
        bucket = s3_.Bucket(self, id="Adnan-ConstantsFileBucket",
                            versioned=True,
                            removal_policy=RemovalPolicy.DESTROY,
                            auto_delete_objects=True,
                            public_read_access=True
                            )

        # 2. Grants read/write permissions for this bucket and it’s contents to an IAM principal (Role/Group/User).
        bucket.grant_read_write(WH_lambda)
        bucket.grant_read_write(bucket_to_db_handler_lambda)

        # 3. Create a deployment to deploy the bucket
        s3deploy_.BucketDeployment(self, "Adnan-ConstantsBucketDeploy",
                                   sources=[s3deploy_.Source.asset("./resources",
                                                                   exclude=["*", "!URLs.py"])],
                                   destination_bucket=bucket
                                   # retain_on_delete=False
                                   )

        # 4. Add resource policy to allow only constansts.py file to be uploaded
        bucket.add_to_resource_policy(
            iam_.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[bucket.arn_for_objects("URLs.py")],
                principals=[iam_.AccountRootPrincipal()]
            )
        )

        #########################################################################
        # Set Environment Variables
        #########################################################################
        # Adding environment variables to the lambda functions
        WH_lambda.add_environment("Bucket_Name", bucket.bucket_name)
        # WH_lambda.add_environment("URLs_TABLE_NAME", dynamodb_urls_table.table_name)

        db_lambda.add_environment("ALARMS_TABLE_NAME", dynamodb_alrams_table.table_name)

        bucket_to_db_handler_lambda.add_environment('Bucket_Name', bucket.bucket_name)
        bucket_to_db_handler_lambda.add_environment('URLs_TABLE_NAME', dynamodb_urls_table.table_name)

        api_handler_lambda.add_environment('Bucket_Name', bucket.bucket_name)
        api_handler_lambda.add_environment('URLs_TABLE_NAME', dynamodb_urls_table.table_name)

        #############################################################################
        # *********** Set Rollback: Version Control Through Code Deploy *************
        #############################################################################
        # Failure dimensions for web health lambda
        WHL_failure_dimensions = {'FunctionName': WH_lambda.function_name}
        WHL_failure_invo_dimensions = {'FunctionName': WH_lambda.function_name}

        # Failure dimensions for dynamo lambda
        dynamo_failureDimensions = {'FunctionName': db_lambda.function_name}
        dynamo_failure_invoDimensions = {'FunctionName': db_lambda.function_name}

        invo_dynamo_metric = db_lambda.metric_invocations(
            dimensions_map=dynamo_failure_invoDimensions,
            period=Duration.minutes(5))

        dur_dynamo_metric = db_lambda.metric_duration(
            dimensions_map=dynamo_failureDimensions,
            period=Duration.minutes(5))

        invo_whl_metric = WH_lambda.metric_invocations(
            dimensions_map=WHL_failure_invo_dimensions,
            period=Duration.minutes(5))

        dur_whl_metric = WH_lambda.metric_duration(
            dimensions_map=WHL_failure_dimensions,
            period=Duration.minutes(5))

        # Duration & Invocation Alarms for Web Health Lambda
        whl_duration_failure_alarm = cloudwatch_.Alarm(self, "AdnanWHLambdaDurationFailureAlarm",
                                                       comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
                                                       threshold=4000,
                                                       evaluation_periods=1,
                                                       metric=dur_whl_metric
                                                       )

        # Create an alarm if the Lambda function reaches invokation threshold
        whl_invokation_failure_alarm = cloudwatch_.Alarm(self, "AdnanWHLambdaInvokationFailureAlarm",
                                                         comparison_operator=cloudwatch_.ComparisonOperator.LESS_THAN_THRESHOLD,
                                                         # threshold=1,
                                                         threshold=100,
                                                         evaluation_periods=1,
                                                         metric=invo_whl_metric
                                                         )

        # Duration & Invocation Alarms for Dyanmo Lambda 
        dynamo_duration_failure_alarm = cloudwatch_.Alarm(self, "AdnanDynamoLambdaDurationFailureAlarm",
                                                          comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
                                                          threshold=4000,
                                                          evaluation_periods=1,
                                                          metric=dur_dynamo_metric
                                                          )

        # Create an alarm if the Lambda function reaches invokation threshold
        dynamo_invokation_failure_alarm = cloudwatch_.Alarm(self, "AdnanDynamoLambdaInvokationFailureAlarm",
                                                            comparison_operator=cloudwatch_.ComparisonOperator.LESS_THAN_THRESHOLD,
                                                            threshold=100,
                                                            # threshold=1,
                                                            evaluation_periods=1,
                                                            metric=invo_dynamo_metric
                                                            )

        # Creating Alias for Rollback
        whl_alias = lambda_.Alias(
            self,
            "AdnanWHLambdaAlias",
            alias_name="AdnanCurrentWHLambdaAlias",
            version=WH_lambda.current_version
            # Returns a lambda.Version which represents the current version of this Lambda function.
            # A new version will be created every time the function’s configuration changes.
        )

        dynamo_alias = lambda_.Alias(
            self,
            "AdnanDynamoLambdaAlias",
            alias_name="AdnanCurrentDynamoLambdaAlias",
            version=db_lambda.current_version
        )

        # Creating deployment groups
        codedeploy_.LambdaDeploymentGroup(
            self,
            "AdnanWHLambdaDeploymentGroup",
            alias=whl_alias,
            deployment_config=codedeploy_.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE,
            alarms=[whl_duration_failure_alarm, whl_invokation_failure_alarm]
        )

        codedeploy_.LambdaDeploymentGroup(
            self,
            "AdnanDynamoLambdaDeploymentGroup",
            alias=dynamo_alias,
            deployment_config=codedeploy_.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE,
            alarms=[dynamo_duration_failure_alarm, dynamo_invokation_failure_alarm]
        )

        # Binding Failure Alarms with SNS
        whl_duration_failure_alarm.add_alarm_action(actions_.SnsAction(topic))
        whl_invokation_failure_alarm.add_alarm_action(actions_.SnsAction(topic))
        dynamo_duration_failure_alarm.add_alarm_action(actions_.SnsAction(topic))
        dynamo_invokation_failure_alarm.add_alarm_action(actions_.SnsAction(topic))

        #############################################################################
        # ******************************* Defining API ******************************
        #############################################################################

        # instantiating API Gateway
        self.create_api_gateway('AdnanCrudApiGateway', api_handler_lambda)

        dblambda_schedule = events_.Schedule.rate(Duration.minutes(1))
        dblambda_target = targets_.LambdaFunction(bucket_to_db_handler_lambda)

        events_.Rule(self, "DBLambdaInvocation",
                     description="Periodic DB Lambda",
                     schedule=dblambda_schedule,
                     enabled=True,
                     targets=[dblambda_target])

    #######################################################################################################################
    # USER DEFINED HELPER FUNCTIONS
    #######################################################################################################################
    def create_lambda_role(self, id_):
        """
            Function to create IAM Role for lambda
        Args:
            None

        Returns: role object with defined policies
        """
        role = iam_.Role(
            self,
            id=id_,
            assumed_by=iam_.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam_.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                iam_.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
                iam_.ManagedPolicy.from_aws_managed_policy_name('AmazonDynamoDBFullAccess'),
                iam_.ManagedPolicy.from_aws_managed_policy_name('CloudWatchFullAccess'),
            ]
        )

        return role

    def create_lambda(self, lambda_id, assets, handler, role):
        """
            Function to create lambda function.
        Args:
            lambda_id: desired lambda function id
            assets: describe the assets required for the lambda function
            handler: handler function of the lambda function
            role: role to be attached to the lambda function

        Returns: an instance of lambda function

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
        Args:
            metric_name: describe the metric name of alarm
            namespace: describe the namespace for alarm
            url: describe the url for alarm to be used in dimensions_map
            alarm_id: describe the id of alarm
            comparison_operator: describe the comparison operator to make decision
            threshold: describe the threshold for alarm
            evaluation_periods: describe the evaluation periods for alarm
            topic: describe the subscription topic for alarm to send notifications

        Returns: an instance of alarm
        """
        # create metric for alarm
        metric = cloudwatch_.Metric(
            namespace=namespace,
            metric_name=metric_name,
            dimensions_map={
                "URL": url
            },
            period=Duration.seconds(60)
        )

        # Create cloudwatch alarm
        alarm = cloudwatch_.Alarm(self, alarm_id,
                                  comparison_operator=comparison_operator,
                                  threshold=threshold,
                                  evaluation_periods=evaluation_periods,
                                  metric=metric
                                  )

        # Create an OpsItem with specific severity and category when alarm triggers
        alarm.add_alarm_action(actions_.SnsAction(topic))

    def create_api_gateway(self, id_=None, handler_=None):
        """
            Function to create api gateway and perform crud operations on resources.
        :param id_: api gateway id
        :param handler_: lambda handler
        :return: rest api
        """
        # creating a lambda-backed API Gateway
        api = gateway_.LambdaRestApi(
            self,
            id=id_,
            handler=handler_,
            cloud_watch_role=True
        )
        api.apply_removal_policy(RemovalPolicy.DESTROY)

        # adding resource <s3> and methods for it
        health = api.root.add_resource("health")
        health.add_method("GET")  # GET /items

        # adding resource <urls> and methods for it
        url = api.root.add_resource("URLS")
        url.add_method("GET")  # GET /url
        url.add_method("POST")  # POST /url
        url.add_method("PATCH")  # UPDATE /url
        url.add_method("DELETE")  # DELETE /url

        return api
