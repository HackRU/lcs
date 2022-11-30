from src.schemas import ensure_schema, ensure_logged_in_user
from src import util

import bcrypt
import json


@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"}
    },
    "required": ["token"]
})
@ensure_logged_in_user()
def promotion_link(event, maglinkobj, user=None):
    """
    Function used to update an user based on a magic link
    """
    user_coll = util.coll('users')
    # grab the permissions object
    permissions = maglinkobj['permissions']
    # for every permission of the user, other than hacker (which is already given upon creation), update the
    # relevant boolean within the database
    for i in permissions:
        if i != 'hacker':
            role_bit = 'role.' + i
            user_coll.update_one({'email': user['email']}, {'$set': {role_bit: True}})

    return {"statusCode": 200, "body": "Successfully updated your role"}


@ensure_schema({
    "type": "object",
    "properties": {
        "password": {"type": "string"},
    },
    "required": ["password"]
})
def forgot_password_link(event, user_coll, maglinkobj):
    """
    Function used to deal with a "forgot password" type of magic link
    """
    # the new password is fetched from the given object and then hashed with a salt
    pass_ = event['password']
    pass_ = bcrypt.hashpw(pass_.encode('utf-8'), bcrypt.gensalt(rounds=8))
    # verifies that the user exists (and complain if they don't)
    user_data = user_coll.find_one({"email": maglinkobj['email']})
    if user_data is None:
        return {"statusCode": 400, "body":  "We could not find that email"}
    # sets the password to the new password given by the user
    user_coll.update_one({"email": maglinkobj['email']}, {'$set': {'password': pass_}})
    return {"statusCode": 200, "body":  "Successfully updated your password"}


@ensure_schema({
    "type": "object",
    "properties": {
        "link": {"type": "string"},
    },
    "required": ["link"]
})
def consume_url(event, context):
    """
    Lambda function to consume a url. Queries the database and checks permissions and updates accordingly
    """
    # fetches the user collection
    user_coll = util.coll('users')
    # fetches the magic link collection
    magiclinks = util.coll('magic links')
    # tries to find the given magic link within the recognized collection of magic links
    maglinkobj = magiclinks.find_one({"link": event['link']})
    # complain if the link is invalid
    if maglinkobj is None:
        return util.add_cors_headers({"statusCode": 400, "body":  "Invalid magiclink, try again"})
    # the appropriate function is called to consume this link depending on whether the magic link is for forgotten
    # password or some other type
    if maglinkobj['forgot']:
        result = forgot_password_link(event, user_coll, maglinkobj)
    else:
        result = promotion_link(event, maglinkobj)
    # remove link after consuming
    if result['statusCode'] == 200:
        magiclinks.remove({"link": maglinkobj['link']})
    return result
