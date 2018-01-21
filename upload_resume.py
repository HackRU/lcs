import boto3

def upload(event, context):
	try:
		boto3.client('s3').upload_file(event['file'], 'hackru-test')
	except Exception as e:
		return e

	return {"statusCode": 200, "body": "Successful request."}

