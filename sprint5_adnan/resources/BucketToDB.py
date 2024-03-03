import re
import boto3
import os
import uuid


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')

    # URL bucket name
    bucket_name = os.environ["Bucket_Name"]
    table = dynamodb.Table(os.environ['URLs_TABLE_NAME'])

    # get all the objects from the bucket: in this case, all the objects are the URLs.py
    s3_object = s3.get_object(
        Bucket=bucket_name,
        Key='URLs.py'
    )

    # read the contents of URLs file. It returns string type object
    contents = s3_object['Body'].read().decode('utf-8')

    # parsing URLs from the string using regular expression
    regex = re.compile("(https:\/\/w*.\S+\.\S+\/)", re.DOTALL)
    urls_list = re.findall(regex, contents)

    # # Writes target list obtained from s3 bucket to dynamodb
    # with table.batch_writer() as batch:
    #     for url in urls_list:
    #         url_id = uuid.uuid4()
    #         batch.put_item(
    #             Item={
    #                 "URL_ID": str(url_id),
    #                 "website": url
    #             }
    #         )

    # # put the URLs in the table
    for url in urls_list:
        url_id = uuid.uuid4()
        table.put_item(
            TableName=os.environ['URLs_TABLE_NAME'],
            Item={
                "URL_ID": str(url_id),
                "website": url
            }
        )

    return urls_list
