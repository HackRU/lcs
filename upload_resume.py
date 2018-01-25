import boto3
import config

def upload(event, context):
	try:
		boto3.client('s3').upload_file(event['file'], 'hackru-test')
	except Exception as e:
		return config.add_cors_header(e)

	return config.add_cors_header({"statusCode": 200, "body": "Successful request."})

