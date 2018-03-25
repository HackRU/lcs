import pymongo
import validate
import config 
import random
def genMagicLink(event,context):
    """
       The event object expects and email and  checks if it is a valid request to generate the magic link  
    """
    if 'email' not in event or 'token' not in event:

        return config.add_cors_headers({"statusCode":400,"body":"You forgot some params try a again"})
    #validate first
    ret_ = validate.validate(event,context);
    #if sucesfully validated 
    if(ret_['statusCode'] == 200):
        #defaul value of numlinks 1
        numLinks = 1
        if 'numLinks' not in event:
            numLinks = event['numLinks']
        permissions = []
        client = MongoClient(config.DB_URI)
        db = client['lcs-db']
        db.authenticate(config.DB_USER,config.DB_PASS)
        tests = db['test']
        magiclinks = db['magiclinks']
        user = tests.find_one({"email":event['email']})
        if user and user['role']['director']:
            #build permissions
            if 'permissions' in event:
                for i in event['permissions']:
                    permissions.append(i)
            for j in range(numLinks):
                random = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
                obj_to_insert = {}
                obj_to_insert[random]['permissions'] = permissions
                obj_to_insert[random]['expiry'] ='' 
                obj_to_insert[random]['email'] = event['emailsTo'][j]
                magiclinks.insert_one(magiclinks)

            return config.add_cors_headers({"statusCode":200,"body":"Made Magic Links with Permissions Director"})
        else:

                return config.add_cors_headers({"statusCode":400,"body":"Invalid permissions"})
    else:

        return config.add_cors_headers({"statusCode":400,"body":"Please input a proper auth token"})





