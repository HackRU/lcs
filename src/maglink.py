import random
import string
from datetime import datetime, timedelta
from src import emails
from src import util
from src.schemas import ensure_schema, ensure_logged_in_user, ensure_role

DEFAULT_LINK_BASE = 'https://hackru.org/magic/{}'


@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
    },
    "required": ["email"]
})
def forgot_user(event, magiclinks, user_coll):
    """
    Function used to generate forgotten password magic links
    """
    # find the user who forgot their password
    user = user_coll.find_one({"email": event['email']})
    # if the user is not found, then return an error
    if user is None:
        return util.add_cors_headers({"statusCode": 400, "body": "Invalid email: please create an account."})
    else:
        # generate the magic link using the prefix "forgot" concatenated with 32 random alphanumeric characters
        magiclink = 'forgot-' + ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(32)])
        # create magic link object that stores other details
        obj_to_insert = {'email': event['email'],
                         'link': magiclink,
                         'forgot': True,
                         'valid_until': (datetime.now() + timedelta(hours=3)).isoformat()}
        # add it to the collection of magic links
        magiclinks.insert_one(obj_to_insert)
        # creates the complete link using a provided link_base (default one is used if it's absent)
        link_base = event.get('link_base', DEFAULT_LINK_BASE)

        # Send an email with the complete link to the registered email address
        rv = emails.send_email(event["email"], link_base.format(magiclink), "FORGOT_PASSWORD", None)

        if rv['statusCode'] != 200:
            return rv
        return util.add_cors_headers({"statusCode": 200, "body": "Forgot password link has been emailed to you"})


def director_link(magiclinks, num_links, event, user):
    """
    Function used to generate magic links for one or more users to be promoted
    """
    links_list = []
    permissions = []
    # fetches the permissions the promoted users should have
    for i in event['permissions']:
        permissions.append(i)
    # for each of the emails requested to be promoted...
    for j in range(min(num_links, len(event['emailsTo']))):
        # a unique magic link is generated as 32 random alphanumeric characters
        magiclink = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(32)])
        # an object is created to be stored in the database
        obj_to_insert = {'permissions': permissions,
                         'email': event['emailsTo'][j],
                         'forgot': False,
                         'link': magiclink,
                         "valid_until": (datetime.now() + timedelta(hours=3)).isoformat()}
        # this object is stored in the collection of magic links in the database
        magiclinks.insert_one(obj_to_insert)
        # the complete link is then created using a given link_base (or a default if none is provided)
        link_base = event.get('link_base', DEFAULT_LINK_BASE)
        link = link_base.format(magiclink)
        # sends the email
        sent = emails.send_email(obj_to_insert["email"], link,
                                        event.get("template", "UPGRADE_USER"), user)["body"]
        # adds a tuple containing the link and the return value from attempting to send the email
        links_list.append((magiclink, sent))
    # the list of tuples generated is returned
    return links_list


@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "template": {"type": "string"},
        "link_base": {"type": "string"},
        "permissions": {"type": "array"},
        "emailsTo": {"type": "array"},
        "numLinks": {"type": "integer"}
    },
    "required": ["token", "permissions", "emailsTo"]
})
@ensure_logged_in_user()
@ensure_role([['director']])
def do_director_link(event, magiclinks, user=None):
    """
    Function used by directors to promote users through magiclinks
    """
    num_links = event.get('numLinks', 1)
    links_list = director_link(magiclinks, num_links, event, user)
    return util.add_cors_headers({"statusCode": 200, "body": links_list})


@ensure_schema({
    "type": "object",
    "properties": {
        "link_base": {"type": "string"}
    }
})
def gen_magic_link(event, context):
    """
    The event object expects an email and checks if it is a valid request to generate the magic link
    """
    user_coll = util.coll('users')
    magiclinks = util.coll('magic links')

    # depending on the type of magic link request, the appropriate function is called
    if 'forgot' in event:
        return forgot_user(event, magiclinks, user_coll)
    return do_director_link(event, magiclinks)
