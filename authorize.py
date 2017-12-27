import string
import random
def authorize(event,context):



    email = event['email']
    hash_ = event['hash']
    #querydb 
    
    #generate auth token
    token = gen()
    ret_val = { 'authtoken' : token }
    return ret_val
def gen (size = 20, chars = string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))
