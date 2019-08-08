import json

from schemas import ensure_schema, ensure_logged_in_user
from config import RESUME, RESUME_BUCKET

import boto3
from botocore.exceptions import ClientError

presign_input = {
    "type": "object",
    "properties": {
        "email": {"type": "string"},
        "token": {"type": "string"}
    },
    "required": ["email", "token"]
}

def presign(method, event, ctx, user):
    client = boto3.client("s3", **RESUME)
    http_method = "GET"
    if method == "put_object":
        http_method="PUT"
    return client.generate_presigned_url(
        method,
        Params={
            "Bucket": RESUME_BUCKET,
            "Key": event["email"] + ".pdf"
        },
        HttpMethod=http_method,
        ExpiresIn=3600,
    )

@ensure_schema(presign_input)
@ensure_logged_in_user()
def download_link(event, ctx, user):
    try:
        return {"statusCode": 200, "body": {"url": presign("get_object", event, ctx, user)}}
    except ClientError as e:
        return {"statusCode": 500, "body": "failed to connect to s3" + str(e)}

@ensure_schema(presign_input)
@ensure_logged_in_user()
def upoad_link(event, ctx, user):
    try:
        return {"statusCode": 200, "body": {"url": presign("put_object", event, ctx, user)}}
    except ClientError as e:
        return {"statusCode": 500, "body": "failed to connect to s3" + str(e)}

def exists(email):
    client = boto3.client("s3", **RESUME)
    try:
        info = client.head_object(Bucket=RESUME_BUCKET, Key=email + ".pdf")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == 404:
            return False
        raise e
    
@ensure_schema(presign_input)
@ensure_logged_in_user()
def resume(event, ctx, user):
    try:
        return {"statusCode": 200, "body": {
            "upload": presign("put_object", event, ctx, user),
            "download": presign("get_object", event, ctx, user),
            "exists": exists(event["email"])
        }}
    except ClientError as e:
        return {"statusCode": 500, "body": "failed to connect to s3" + str(e)}
    
