import config
from src.schemas import ensure_schema, ensure_logged_in_user, get_token
import boto3
from botocore.exceptions import ClientError


def presign(file, method, user, s3_client):
    """
    Function used to generate a presign URL to download/upload resume
    """
    # default is GET method
    http_method = "GET"
    # creates the parameters, which includes the bucket name and the name of the file to be saved
    # which is the user's email followed by the .pdf extension
    if (file.capitalize() == "Resume"):
        params = {
            "Bucket": config.RESUME_BUCKET,
            "Key": user["email"] + ".pdf"
        }
    elif (file.capitalize() == "Vaccine"):
        params = {
            "Bucket": config.VACCINE_BUCKET,
            "Key": user["email"] + ".pdf"
        }
    elif (file.capitalize() == "Waiver"):
        params = {
            "Bucket": config.WAIVER_BUCKET,
            "Key": user["email"] + ".pdf"
        }
    else:
        raise Exception("Your file input parameter is wrong. Can only be 3 options: Resume, Vaccine, or Waiver")
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


def exists(file, email, s3_client):
    """
    Function that checks if a resume already exists for the given user
    """
    # tries to query the resume pdf and returns whether or not there was a 404 error
    try:
        if (file.capitalize() == "Resume"):
            info = s3_client.head_object(Bucket=config.RESUME_BUCKET, Key=email + ".pdf")
        elif (file.capitalize() == "Vaccine"):
            info = s3_client.head_object(Bucket=config.VACCINE_BUCKET, Key=email + ".pdf")
        elif (file.capitalize() == "Waiver"):
            info = s3_client.head_object(Bucket=config.WAIVER_BUCKET, Key=email + ".pdf")
        else:
            # file input param can only be: Resume, Vaccine, or Waiver
            raise Exception("Your file input parameter is wrong. Can only be 3 options: Resume, Vaccine, or Waiver") 
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise e


# @ensure_schema({
#      "type": "object",
#      "properties": {
#          "token": {"type": "string"}
#      },
#      "required": ["token"]
#  })

# Note for tomorrow: error has something to do with @ensure_schema, change it so that headers obj inside event is kept
@ensure_schema({
     "type":"object",
      "properties": {

        "body": {
          "type": "object",
          "properties": {

            "token": {"type": "string"},
            },
            "required": ["token"]
        }
      },
      "required": ["body", "headers"]
 })
@get_token()
@ensure_logged_in_user()
def resume_vaccine_waiver(event, ctx, user=None):
    """
    Function used to upload a user's resume to a S3 bucket
    """
    # # creates a client connection to the S3 bucket
    # client = boto3.client("s3", **config.AWS)
    # # attempts to create presigned URLs to upload and download the resume as well as check if a
    # # resume for that user already exists in S3
    # try:
    #     return {
    #         "statusCode": 200, "body": {
    #             "upload": presign(file, method="put_object", user=user, s3_client=client),
    #             "download": presign(file, method="get_object", user=user, s3_client=client),
    #             "exists": exists(file, email=user["email"], s3_client=client)
    #         }
    #     }
    # # if there are any errors, they are communicated back
    # except ClientError as e:
    #     return {
    #         "statusCode": 500,
    #         "body": "failed to connect to s3" + str(e)
    #     }
    print("//////////// inside endpoint /////////////")
    print("Event: ")
    print(event)
    # print(event.path)
    # print("ctx")
    # print(ctx.function_name)

def waiver(event, ctx, user=None):
    """
    Function used to upload a user's resume to a S3 bucket
    """
    # creates a client connection to the S3 bucket
    # client = boto3.client("s3", **config.AWS)
    # # attempts to create presigned URLs to upload and download the resume as well as check if a
    # # resume for that user already exists in S3
    # try:
    #     return {
    #         "statusCode": 200, "body": {
    #             "upload": presign("Waiver", method="put_object", user=user, s3_client=client),
    #             "download": presign("Waiver", method="get_object", user=user, s3_client=client),
    #             "exists": exists("Waiver", email=user["email"], s3_client=client)
    #         }
    #     }
    # # if there are any errors, they are communicated back
    # except ClientError as e:
    #     return {
    #         "statusCode": 500,
    #         "body": "failed to connect to s3" + str(e)
    #     }
    print(event)

def resume(event, ctx, file, user=None):
    """
    Function used to upload a user's resume to a S3 bucket
    """
    # creates a client connection to the S3 bucket
    client = boto3.client("s3", **config.AWS)
    # attempts to create presigned URLs to upload and download the resume as well as check if a
    # resume for that user already exists in S3
    try:
        return {
            "statusCode": 200, "body": {
                "upload": presign("Resume", method="put_object", user=user, s3_client=client),
                "download": presign("Resume", method="get_object", user=user, s3_client=client),
                "exists": exists("Resume", email=user["email"], s3_client=client)
            }
        }
    # if there are any errors, they are communicated back
    except ClientError as e:
        return {
            "statusCode": 500,
            "body": "failed to connect to s3" + str(e)
        }
    
def vaccine(event, ctx, file, user=None):
    """
    Function used to upload a user's resume to a S3 bucket
    """
    # creates a client connection to the S3 bucket
    client = boto3.client("s3", **config.AWS)
    # attempts to create presigned URLs to upload and download the resume as well as check if a
    # resume for that user already exists in S3
    try:
        return {
            "statusCode": 200, "body": {
                "upload": presign("Vaccine", method="put_object", user=user, s3_client=client),
                "download": presign("Vaccine", method="get_object", user=user, s3_client=client),
                "exists": exists("Vaccine", email=user["email"], s3_client=client)
            }
        }
    # if there are any errors, they are communicated back
    except ClientError as e:
        return {
            "statusCode": 500,
            "body": "failed to connect to s3" + str(e)
        }