ORION_URL_NAME_SPACE = "AdnanOrion"
AVAIL_METRIC_NAME = "Availability_"
LATENCY_METRIC_NAME = "Latency_"
CLOUDWATCH_POLICY = "CloudWatchFullAccess"

EMAIL_ADDRESS = "adnan.irshad.skipq@gmail.com"

URLs_TO_MONITOR = [
    'https://www.skipq.org/',
    'https://www.youtube.com/',
    'https://www.netflix.com/pk/',
    'https://www.amazon.com/'
]

ACCOUNT_ID = "315997497220"
REGION = "us-east-2"

GIT_REPO = "adnan2022skipq/Orion_Python"

GIT_BRANCH = "main"

SYNTH_COMMANDS = ["cd AdnanIrshad/sprint4_adnan",
                  "pip install -r requirements.txt",
                  "npm install -g aws-cdk",
                  "cdk synth"]

PIPELINE_CDK_OUTPUT_PATH = "AdnanIrshad/sprint4_adnan/cdk.out"

UNIT_TEST_COMMANDS = ["cd AdnanIrshad/sprint4_adnan",
                      "pip install -r requirements.txt",
                      "pip install pytest",
                      "npm install -g aws-cdk",
                      "pytest tests/unit/test_sprint4_adnan_stack.py"]

INTEGRATION_TEST_COMMANDS = ["cd AdnanIrshad/sprint4_adnan",
                             "pip install pytest",
                             "pip install -r requirements.txt",
                             "npm install -g aws-cdk",
                             "pytest tests/integration/integration_test_sprint4_adnan_stack.py"]
