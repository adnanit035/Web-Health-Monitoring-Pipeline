import boto3

class CloudWatch:
    def __init__(self):
        self.client = boto3.client('cloudwatch')
        
    def publish_metrics(self, metric_name, namespace, dimensions, value):
        """
            Publish metrics to CloudWatch
        :param metric_name: Name of the metric 
        :param namespace: Namespace of the metric 
        :param dimensions: Dimensions of the metric  
        :param value: Value of the metric 
        :return: none
        """
        response = self.client.put_metric_data(
            Namespace = namespace,
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Dimensions': dimensions,
                    'Value': value,
                },
            ]
        )