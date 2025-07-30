import os
import boto3
from botocore.config import Config

dynamodb_max_attempts = int(os.environ.get('DYNAMODB_MAX_ATTEMPTS', 3))
dynamodb_retry_mode = os.environ.get('DYNAMODB_RETRY_MODE', 'adaptive')
dynamodb_connect_timeout = int(os.environ.get('DYNAMODB_CONNECT_TIMEOUT', 5))
dynamodb_read_timeout = int(os.environ.get('DYNAMODB_READ_TIMEOUT', 5))

ddb_config = Config(
    retries=dict(
        max_attempts = dynamodb_max_attempts,
        mode = dynamodb_retry_mode
    ),
    connect_timeout = dynamodb_connect_timeout,
    read_timeout = dynamodb_read_timeout
)

dbclient = boto3.client('dynamodb', config=ddb_config)
