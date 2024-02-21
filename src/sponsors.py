from src import util
import boto3
import config

def sponsors(event, context, user=None): 
    # fetch all the photo URLs of sponsors' logo pics from S3 bucket
    # Initialize a session using Amazon S3 credentials
    session = boto3.Session(**config.AWS)
    
    # Create an S3 client using the session
    s3 = session.client('s3')
    
    # Retrieve the list of objects in the specified bucket
    photo_urls = []
    paginator = s3.get_paginator('list_objects_v2')
    
    # Pagination handles buckets with many objects
    for page in paginator.paginate(Bucket=config.SPONSOR_BUCKET):
        for obj in page.get('Contents', []):
            if obj['Key'].lower().endswith(('.png', '.jpg', '.jpeg')):
                photo_url = f"https://{config.SPONSOR_BUCKET}.s3.amazonaws.com/{obj['Key']}"
                photo_urls.append(photo_url)
    
    return {
        "photos": photo_urls
    }