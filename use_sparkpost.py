from sparkpost import SparkPost

from schemas import *
import config
import util
from read import read_info

emails = SparkPost(config.SPARKPOST_KEY)

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "token": {"type": "string"}
    },
    "required": ["email", "token"]
})
@ensure_logged_in_user()
@ensure_role([['director']])
def list_all_templates(event, context, user):
    """
    Gets a list of all the templates iff the
    user (email, token keys in event) is an
    authenticated director.

    The template list is some sort of dictionary
    from sparkpost.
    """
    templs = emails.templates.list()
    return {'statusCode': 400, 'body': templs}

def do_substitutions(recs, links, template, usr):
    """
    Given the recipients, links for each recipients,
    a template, and the current user, sends out emails
    with the correct link substituted into the template.

    The shorter of recs and links is used for the matching.
    """
    #we use the uniqueness of emails to gaurentee the uniqueness of these list_id's
    list_id = usr['email'] + '-emailing-people'
    rl = [{
        'address': i[0],
        'substitution_data': {'link': i[1]}
        } for i in zip(recs, links)]
    try:
        emails.recipient_lists.create(
            id= list_id,
            name= usr['first_name'] + ' sending emails',
            recipients=rl
        )
        templ = emails.templates.get(template)
        resp = emails.transmissions.send(
                recipient_list=list_id,
                template=template
        )
        if resp[u'total_accepted_recipients'] != len(recs):
            rv = config.add_cors_headers({'statusCode': 500, 'body': "Sparkpost troubles!"})
        else:
            rv = config.add_cors_headers({'statusCode': 200, 'body': "Success!"})
    except Exception as e:
        rv = config.add_cors_headers({'statusCode': 400, 'body': "Error: " + str(e)})
    finally: #1st time I'm legit using a finally... kawaii OwO.
        emails.recipient_lists.delete(list_id)
        return rv

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "token": {"type": "string"},
        "template": {"type": "string"},
        "recipients": {"type": "array"}
    },
    "required": ["email", "token", "template"]
})
@ensure_logged_in_user()
def send_to_emails(event, context, usr):
    """
    If the user (validated via the email and token keys)
    is a non-director, the only keys allowed are the 'recipients' one
    and the 'template' one. (The template should be a valid template.)

    If a valid director is logged in then the 'recipients' list can be
    arbitrary. If a 'query' is provided and no 'recipients' list is, then
    the 'query' is run as if passed to the 'read' endpoint
    the email key of every returned document is emailed.

    If there is a 'recipients' list and a 'link' key is provided, it is assumed
    that the 'link' is an array of corresponding links to substitute for each
    recipient. This substitution is performed using "do_substitutions" specified
    above.
    """
    if not usr['role']['director'] and event.get('recipients', []) != [usr['email']]:
        return {'statusCode': 400, 'body': "Not authorized to send emails!"}
    else: #note, below this point, we can assume usr is a director or that the recipients list has length 1.
        if 'query' in event and 'recipients' not in event: #recall that a non-director cannot have this: they must have "recipients"
            queried = read_info(event, context)
            if queried['statusCode'] != 200:
                return queried
            event['recipients'] = [i['email'] for i in queried['body'] if 'email' in i]
            if len(event['recipients']) == 0:
                return {'statusCode': 204, 'body': "No recipients found!"}
        elif 'links' in event:
            return do_substitutions(event['recipients'], event['links'], event['template'], usr)
        try:
            templ = emails.templates.get(event['template'])
            resp = emails.transmissions.send(
                    recipients=event['recipients'],
                    template=event['template']
            )
            if resp[u'total_accepted_recipients'] != len(event['recipients']):
                return {'statusCode': 500, 'body': "Sparkpost troubles!"}
            else:
                return {'statusCode': 200, 'body': "Success!"}
        except Exception:
            return {'statusCode': 400, 'body': "Template not found or error in sending"}

def send_email(recipient, link, template, sender):
    """
        Sends an email to one person - recipient
        with the link.
        If "forgot", use the forgotten password template.

        If not "forgot" sender needs to be non None.
    """

    if sender is None:
        tests = util.coll('users')
        sender = tests.find_one({"email":recipient})
    return do_substitutions([recipient],[link], template, sender)
