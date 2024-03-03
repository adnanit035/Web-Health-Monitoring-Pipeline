import boto3
import os
import json


def lambda_handler(event, context):
    # convert the event to a dict
    data = json.loads(json.dumps(event))
    data = data['Records'][0]['Sns']

    # parse the message id
    alarm_id = data["MessageId"]
    # parse the timestamp
    timestamp = data["Timestamp"]
    # parse the metrics
    metric_name = json.loads(data['Message'])['Trigger']['MetricName']

    # create boto3 client which provides methods to connect with AWS service DynamoDB
    dynamodb_client = boto3.client('dynamodb')
    table_name = os.environ['ALARMS_TABLE_NAME']

    # put the alarm logs into the table
    response = dynamodb_client.put_item(
        TableName=table_name,
        Item={
            'id': {'S': alarm_id},
            'timestamp': {'S': timestamp},
            'Metric_Name': {'S': metric_name}
        }
    )

    return response
