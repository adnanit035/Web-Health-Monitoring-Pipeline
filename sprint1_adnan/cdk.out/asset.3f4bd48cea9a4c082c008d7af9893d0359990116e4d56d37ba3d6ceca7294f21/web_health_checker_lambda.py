import urllib3
import datetime
import constants
import requests

def lambda_handler(event, context):
    """
    Creates a lambda function which monitors the availability  and latency of web resources.
    
    event: describe what the event is and what it contains
    context: describe what the context is and what it returns
    
    return: A list of dictionaries containing information about health of web resources.
    """
    
    value = []
    for url in constants.URL_TO_MONITOR:
        # availability  of my resource
        avail = calc_availability(url)
        # latency of my resource
        latency = calc_latency(url)
        value.append({"availability ": avail, "latency": latency })
        
    return value
    
def calc_availability(url):
    """
    Calculates the availability of Web resources.
    
    url(str): URL of the web resource to be monitored
    
    return: 1.0 if available and 0.0 if not available
    """
    # http = urllib3.PoolManager()
    
    # response = http.request("GET", url)
    
    response = requests.get(url)
    
    # Check if response is OK (200)
    if response.status_code == 200:
        return 1.0      # Resource is available
    else:
        return 0.0      # Resource is not available
    
def calc_latency(url):
    """
    Calculates the latency of Web resources.
    
    url(str): URL of the web resource to be monitored
    
    return: latency of a web resource in microseconds.
    """
    # http = urllib3.PoolManager()
    start = datetime.datetime.now()
    
    # response = http.request("GET", url)
    response = requests.get(url)
    
    end = datetime.datetime.now()
    delta = end - start
    latencySec = round(delta.microseconds * .000001, 6)
    return latencySec