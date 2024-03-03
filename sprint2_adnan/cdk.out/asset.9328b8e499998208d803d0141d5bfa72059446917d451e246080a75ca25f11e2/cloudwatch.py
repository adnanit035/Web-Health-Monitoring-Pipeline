import boto3

class CloudWatch:
    def __init__(self):
        self.client = boto3.client('cloudwatch')
        
    def publish_metrics(self, metric_name, namespace, dimensions, value):
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