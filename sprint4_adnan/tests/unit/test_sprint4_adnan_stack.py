import aws_cdk as core
import aws_cdk.assertions as assertions

from sprint4_adnan.sprint4_adnan_stack import Sprint4AdnanStack


def test_s3_count():
    """
        Test S3 Bucket count
    Returns: None

    """
    # create the app
    app = core.App()
    # create application stack
    stack = Sprint4AdnanStack(app, "sprint3-adnan")
    # create assertion template to perform assertions/test/verification/validation/check/claim
    template = assertions.Template.from_stack(stack)  # << cloud formation template >>

    # assert that S3 Bucket count is 1
    template.resource_count_is(
        type="AWS::S3::Bucket",
        count=1
    )


def test_lambda_count():
    """
        Test Lambda Function count
    Returns: None

    """
    # create the app
    app = core.App()
    # create application stack
    stack = Sprint4AdnanStack(app, "sprint3-adnan")
    # create assertion template to perform assertions/test/verification/validation/check/claim
    template = assertions.Template.from_stack(stack)  # << cloud formation template >>

    # assert that Lambda Function counts are 3
    template.resource_count_is(
        type="AWS::Lambda::Function",
        count=6
    )
