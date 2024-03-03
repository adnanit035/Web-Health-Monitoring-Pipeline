import sys
import boto3
import json
import logging
import os
from custom_encoder import CustomEncoder
import uuid

# download the file from s3 bucket
# s3_client = boto3.client('s3')
# s3_client.download_file(os.environ['Bucket_Name'], 'constants.py', '/tmp/constants.py')
# sys.path.insert(1, '/tmp')

logger = logging.getLogger()  # Return a logger with the specified name
logger.setLevel(logging.INFO)  # Sets the threshold for this logger to level.
table_name = os.getenv("URLs_TABLE_NAME")  # Getting environemntal variable

# methods
getMethod = "GET"
postMethod = "POST"
patchMethod = "PATCH"
delMethod = "DELETE"

# paths
healthPath = "/health"
urlsPath = "/URLS"

dynamoDBClient = boto3.resource('dynamodb')
table = dynamoDBClient.Table(table_name)


def lambda_handler(event, context):
    """
        lambda_handler
    :param event: event
    :param context: context
    :return: response
    """

    print(event)

    logger.info(event)

    httpMethod = event['httpMethod']  # Getting http methods
    path = event['path']  # Getting path

    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == urlsPath:
        response_data = getURLS()  # show the all urls in dynamodb table
        response = buildResponse(200, response_data['Items'])
    elif httpMethod == postMethod and path == urlsPath:
        jsonData = json.loads(event['body'])
        response = postURL(jsonData['website'])  # Add Url in the in the dynamodb table
    elif httpMethod == delMethod and path == urlsPath:
        jsonData = json.loads(event['body'])
        response = delURL(jsonData['URL_ID'])  # Delete Url in the in the dynamodb table
    elif httpMethod == patchMethod and path == urlsPath:
        jsonData = json.loads(event['body'])
        response = updateURL(jsonData)  # update Url in the in the dynamodb table
    else:
        response = buildResponse('404', 'Not Found')

    return response


def getURLS():
    """
        getURLS
    :return: response of table scan
    """
    response = table.scan()
    return response


def postURL(url):
    try:
        URL_ID = str(uuid.uuid4())
        response = table.put_item(Item={"URL_ID": URL_ID, "website": url})
        # response = table.put_item(Item={'url': url})
        body = {
            "Operation": "SAVE",
            "Message": "SUCCESS",
            "Item": url,
        }
        return buildResponse(200, body=body)
    except:
        logger.exception("ERROR IN ADD URL")


def delURL(url_id):
    try:
        response = table.delete_item(
            Key={
                'URL_ID': url_id,
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            "Operation": "DELETE URL",
            "Message": "SUCCESS",
            "DeletedItem": response,
        }
        return buildResponse(200, body=body)
    except:
        logger.exception("ERROR IN DELETE URL")


def updateURL(data):
    try:
        url_id = data['URL_ID']
        url = data['website']
        updateKey = "website"
        response = table.update_item(
            Key={
                'URL_ID': url_id,
            },
            UpdateExpression='set %s = :value' % updateKey,
            ExpressionAttributeValues={':value': url},
            ReturnValues='UPDATED_NEW'
        )
        body = {
            "Operation": "UPDATE URL",
            "Message": "SUCCESS",
            "UpdatedItem": response,
        }
        return buildResponse(200, body=body)
    except:
        logger.exception("ERROR IN UPDATE URL")


def buildResponse(statusCode, body=None):
    response = {
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)

    return response
