def authorize(event,context):
    email = event['email']
    hash_ = event['hash']
    #querydb 
    
    #generate auth token
    token = ""
