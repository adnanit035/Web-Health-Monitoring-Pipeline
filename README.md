# Web-Health Monitoring with CICD Pipeline
The objective of this sprint was to implement a CRUD API Gateway pipeline to automatically monitor resource usage by different websites in real time by crawling a list of websites to find out their availability and delay (response time) after every 10 minute, publish cloudwatch metrics and create alarms to monitor a list of web resources, save logs to DynamoDB, move resources from S3 to dynamodb and implement CRUD operations on resouces urls. 

### Technologies Used:
- Cloud9 Enviornment
- Python3
- AWS Lambda Function
- GitHub
- Cloudwatch
- EC2 Bucket
- AWS CodePipelines
- AWS ShellStep
- AWS CodeDeploy
- Boto3
- DynamoDB
- AWS API Gateway

### Getting Started:
To run this project, need to follow following steps:

First Clone the repo.

```
$ git clone <repo-link>
```

Initilize the AWS CDK.

```
$ cdk init app --language python
```

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```
To deploy the CloudFormation template:

```
$ cdk deploy <id-of-pipeline>
```

## Other Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
