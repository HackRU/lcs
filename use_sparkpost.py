from sparkpost import SparkPost
from validate import get_validated_user
import config
from read import read_info
from pymongo import MongoClient

emails = SparkPost(config.SPARKPOST_KEY)

def list_all_templates(event, context):
    """
    Gets a list of all the templates iff the
    user (email, token keys in event) is an
    authenticated director.

    The template list is some sort of dictionary
    from sparkpost.
    """
    val, usr = get_validated_user(event, context)
    if not val or not user['role']['director']:
        return config.add_cors_headers({'statusCode': 400, 'body': usr})
    else:
        templs = emails.templates.list()
        return config.add_cors_headers({'statusCode': 400, 'body': templs})

def do_substitutions(recs, links, template, usr):
    """
    Given the recipients, links for each recipients,
    a template, and the current user, sends out emails
    with the correct link substituted into the template.

    The shorter of recs and links is used for the matching.
    """
    #we use the uniqueness of emails to gaurentee the uniqueness of these list_id's
    list_id = usr['email'] + '-emailing-people'
    emails.recipient_lists.create(
            id= list_id,
            name= usr['first_name'] + ' sending emails',
            recipients=[{
                    'address': {'email': i[0]},
                    'substitution_data': {'link': i[1]}
                } for i in zip(recs, links)]
            )
    try:
        templ = emails.templates.get(template)
        resp = emails.transmissions.send(
                recipients_list=list_id,
                template=template
        )
        if resp[u'total_accepted_recipients'] != len(recs):
            rv = config.add_cors_headers({'statusCode': 500, 'body': "Sparkpost troubles!"})
        else:
            rv = config.add_cors_headers({'statusCode': 200, 'body': "Success!"})
    except SparkPostAPIException:
        rv = config.add_cors_headers({'statusCode': 400, 'body': "Template not found or error in sending"})
    finally: #1st time I'm legit using a finally... kawaii OwO.
        emails.recipient_lists.delete(list_id)
        return rv

def send_to_emails(event, context):
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
    if 'template' not in event:
        return config.add_cors_headers({'statusCode': 400, 'body': 'Missing template'})
    if 'recipients' not in event and 'query' not in event:
        return config.add_cors_headers({'statusCode': 400, 'body': 'No recipients provided.'})

    val, usr = get_validated_user(event, context)
    if not val:
        return config.add_cors_headers({'statusCode': 400, 'body': usr})
    elif not usr['role']['director'] and event.get('recipients', []) != [usr['email']]:
        return config.add_cors_headers({'statusCode': 400, 'body': "Not authorized to send emails!"})
    else: #note, below this point, we can assume usr is a director or that the recipients list has length 1.
        if 'query' in event and 'recipients' not in event: #recall that a non-director cannot have this: they must have "recipients"
            queried = read_info(event, context)
            if queried['statusCode'] != 200:
                return queried
            event['recipients'] = [i['email'] for i in queried['body'] if 'email' in i]
            if len(event['recipients']) == 0:
                return config.add_cors_headers({'statusCode': 204, 'body': "No recipients found!"})
        elif 'links' in event:
            return do_substitutions(event['recipients'], event['links'], event['template'], usr)
        try:
            templ = emails.templates.get(event['template'])
            resp = emails.transmissions.send(
                    recipients=event['recipients'],
                    template=event['template']
            )
            if resp[u'total_accepted_recipients'] != len(event['recipients']):
                return config.add_cors_headers({'statusCode': 500, 'body': "Sparkpost troubles!"})
            else:
                return config.add_cors_headers({'statusCode': 200, 'body': "Success!"})
        except SparkPostAPIException:
            return config.add_cors_headers({'statusCode': 400, 'body': "Template not found or error in sending"})

