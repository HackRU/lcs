import config
from src.schemas import ensure_schema, ensure_logged_in_user
import json

import boto3
from botocore.exceptions import ClientError


def presign(method, user, s3_client):
    """
    Function used to generate a presign URL to download/upload vaccine card
    """
    # default is GET method
    http_method = "GET"
    # creates the parameters, which includes the bucket name and the name of the file to be saved
    # which is the user's email followed by the .pdf extension
    params = {
        "Bucket": config.VACCINE_BUCKET,
        "Key": user["email"] + ".pdf"
    }
    # if instead the desired method is PUT, then ContentType is set and the http method is changed to PUT
    if method == "put_object":
        http_method = "PUT"
        params["ContentType"] = "application/pdf"
    # calls the appropriate library method to create the presigned URL
    return s3_client.generate_presigned_url(
        method,
        Params=params,
        HttpMethod=http_method,
        ExpiresIn=3600,
    )


def exists(email, s3_client):
    """
    Function that checks if a Vaccine card already exists for the given user
    """
    # tries to query the vaccine pdf and returns whether or not there was a 404 error
    try:
        info = s3_client.head_object(Bucket=config.VACCINE_BUCKET, Key=email + ".pdf")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise e

import config
from src.schemas import ensure_schema, ensure_logged_in_user
import boto3
from botocore.exceptions import ClientError


def presign(method, user, s3_client):
    """
    Function used to generate a presign URL to download/upload vaccine card
    """
    # default is GET method
    http_method = "GET"
    # creates the parameters, which includes the bucket name and the name of the file to be saved
    # which is the user's email followed by the .pdf extension
    params = {
        "Bucket": config.VACCINE_BUCKET,
        "Key": user["email"] + ".pdf"
    }
    # if instead the desired method is PUT, then ContentType is set and the http method is changed to PUT
    if method == "put_object":
        http_method = "PUT"
        params["ContentType"] = "application/pdf"
    # calls the appropriate library method to create the presigned URL
    return s3_client.generate_presigned_url(
        method,
        Params=params,
        HttpMethod=http_method,
        ExpiresIn=3600,
    )


def exists(email, s3_client):
    """
    Function that checks if a Vaccine card already exists for the given user
    """
    # tries to query the vaccine pdf and returns whether or not there was a 404 error
    try:
        info = s3_client.head_object(Bucket=config.VACCINE_BUCKET, Key=email + ".pdf")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise e


@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"}
    },
    "required": ["token"]
})
@ensure_logged_in_user()
def vaccine(event, ctx, user=None):
    """
    Function used to upload a user's vaccine card to a S3 bucket
    """
    # creates a client connection to the S3 bucket
    client = boto3.client("s3", **config.AWS)
    # attempts to create presigned URLs to upload and download the vaccine card as well as check if a
    # vaccine card for that user already exists in S3
    try:
        return {
            "statusCode": 200, "body": {
                "upload": presign(method="put_object", user=user, s3_client=client),
                "download": presign(method="get_object", user=user, s3_client=client),
                "exists": exists(email=user["email"], s3_client=client)
            }
        }
    # if there are any errors, they are communicated back
    except ClientError as e:
        return {
            "statusCode": 500,
            "body": "failed to connect to s3" + str(e)
        }
