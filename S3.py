from os import getenv

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client('s3', aws_access_key_id = getenv("AWS_ACCESS_KEY"), aws_secret_access_key = getenv("AWS_SECRET_KEY"))
