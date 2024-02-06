from env import *

import boto3

def upload_file(file_path, key_name):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.upload_file(file_path, 'bluef1ag', key_name)
    print(f'{file_path} uploaded to S3 bucket.')

def download_file(key_name, file_path):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.download_file('bluef1ag', key_name, file_path)
    print(f'{key_name} downloaded to {file_path}.')
    
