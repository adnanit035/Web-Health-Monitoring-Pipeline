import aws_cdk as core
import aws_cdk.assertions as assertions

from sprint2_adnan.sprint2_adnan_stack import Sprint2AdnanStack

# example tests. To run these tests, uncomment this file along with the example
# resource in sprint2_adnan/sprint2_adnan_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Sprint2AdnanStack(app, "sprint2-adnan")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
