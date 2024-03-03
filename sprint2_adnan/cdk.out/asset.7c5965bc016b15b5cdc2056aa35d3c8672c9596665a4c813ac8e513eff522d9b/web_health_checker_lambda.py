import urllib3
import datetime
import constants
from cloudwatch import CloudWatch
import boto3

# Download the file:constants.py from the S3 bucket
# s3 = boto3.resource('s3')
# s3.Bucket('sprint2adnanstack-adnanconstantsfilebucket9e89504-gvbd6ukg6zby').download_file('constants.py', '/temp/constants.py')
client = boto3.client("s3")
client.download_file('sprint2adnanstack-adnanconstantsfilebucket9e89504-gvbd6ukg6zby', 'constants.py', '/temp/constants.py')

def lambda_handler(event, context):
    """
        Lambda function that monitors the availability and latency of a web resource.
    :param event: describe what the event is and what it contains
    :param context: describe what the context is and what it returns

    :return: A list of dictionaries containing information about health of web resources.
    """

    # Ini
    cloudWatch = CloudWatch()

    value = []
    for url in constants.URL_TO_MONITOR:
        dimensions = [
            {
                'Name': 'URL',
                'Value': url
            }
        ]

        # calculate the availability of my resource
        avail = calc_availability(url)

        # calculate the latency of resources on cloudwatch
        cloudWatch.publish_metrics(constants.AVAIL_METRIC_NAME + url, constants.ORION_URL_NAME_SPACE, dimensions, avail)

        # calculate the latency of my resource
        latency = calc_latency(url)
        
        # publish the latency of website resources on cloudwatch
        cloudWatch.publish_metrics(constants.LATENCY_METRIC_NAME + url, constants.ORION_URL_NAME_SPACE, dimensions,
                                   latency)
        
        # add the information to the list
        value.append({"availability ": avail, "latency": latency})

    return value


def calc_availability(url):
    """
        Function to calculate the availability of Web resources.
    :param url: URL of the web resource to be monitored 
    
    :return: 1.0 if available and 0.0 if not available 
    """
    http = urllib3.PoolManager()
    response = http.request("GET", url)

    # Check if response is OK (200)
    if response.status == 200:
        return 1.0  # Resource is available
    else:
        return 0.0  # Resource is not available


def calc_latency(url):
    """
        Function to calculate the latency of Web resources.
    :param url: URL of the web resource to be monitored  
    
    :return: 1.0 if available and 0.0 if not available 
    """
    http = urllib3.PoolManager()
    start = datetime.datetime.now()

    # Send a request to the web resource
    http.request("GET", url)
    
    end = datetime.datetime.now()
    
    # Calculate the latency
    delta = end - start
    
    # Convert the latency to microseconds
    latencySec = round(delta.microseconds * .000001, 6)
    
    # Return the latency
    return latencySec