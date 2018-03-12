import boto3
import botocore
import config

def upload(event, context):
    try:
    	boto3.client('s3').upload_file(event['file'], 'hackru-test', event['name'] + '_resume')
    except Exception as e:
    	return config.add_cors_header(e)

    return config.add_cors_header({"statusCode": 200, "body": "Successful request."})

def download(event, context):
    try:
        s3.Bucket('hackru-test').download_file(event['key'], event['file_name'])
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return {'statusCode': 404, 'body': 'The file does not exist.'}
        else
            raise

    return {'statusCode': 200, 'body': 'Successful request.'}

