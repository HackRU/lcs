from sparkpost import SparkPost
from validate import get_validated_user
import config
from pymongo import MongoClient

emails = SparkPost(config.SPARKPOST_KEY)

def list_all_templates(event, context):
    val, usr = get_validated_user(event, context)
    if not val or not user['role']['director']:
        return config.add_cors_headers({'statusCode': 400, 'body': usr})
    else:
        templs = emails.templates.list()
        return config.add_cors_headers({'statusCode': 400, 'body': templs})

def send_to_emails(event, context):
    if 'template' not in event:
        return config.add_cors_headers({'statusCode': 400, 'body': 'Missing template'})
    if 'recipients' not in event and 'query' not in event:
        return config.add_cors_headers({'statusCode': 400, 'body': 'No recipients provided.'})

    val, usr = get_validated_user(event, context)
    if not val:
        return config.add_cors_headers({'statusCode': 400, 'body': usr})
    elif not usr['role']['director'] and event.get('recipients', []) != [usr['email']]:
        return config.add_cors_headers({'statusCode': 400, 'body': "Not authorized to send emails!"})
    else:
        if 'query' in event and 'recipients' not in event:
            client = MongoClient(config.DB_URI)
            db = client['lcs-db']
            db.authenticate(config.DB_USER, config.DB_PASS)
            tests = db['test']

            event['recipients'] = [i['email'] for i in tests.find(event['query'])]
            if len(event['recipients']) == 0:
                return config.add_cors_headers({'statusCode': 204, 'body': "No emails to send."})

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

