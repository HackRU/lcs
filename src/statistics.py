from src import util

@util.cors
def statistics(event, context): 
    # Please write your code below. Modify the response object as you wish.

    return {"statusCode": 200, "body": "Successful request.", "headers": {"Content-Type": "application/json"}}