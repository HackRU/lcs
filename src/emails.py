import smtplib
import ssl

import config
from src.schemas import ensure_schema, ensure_logged_in_user
from src import util
from src.read import read_info

import traceback

def do_substitutions(recipients, links, template, user):
    """
    Given the recipients, links for each recipients,
    a template, and the current user, sends out emails
    with the correct link substituted into the template.

    Args:
        - recipients:   list of str of recipient email addresses
        - links:        list of str of recipient magic links
        - template:     str
        - user:         LCS user object
    """
    try:
        with open(f"templates/{template}.txt") as template_text:
            email_body = template_text.read()
    except Exception as e:
        return util.add_cors_headers({"statusCode": 400, "body": f"There is no template named {template}.txt"})

    #for some reason passes these vars as tuples and need to convert to str -- look into 
    email_sender = ''.join(config.EMAIL_ADDRESS)
    email_password = ''.join(config.EMAIL_PASSWORD)

    try:
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls(context=ssl.create_default_context())
        
        smtp.login(email_sender, email_password)
        failed_emails = []
        if links and len(links) != len(recipients):
            return util.add_cors_headers({"statusCode": 400, "body": "Differing lengths between links and recipients"})
        if links and len(links) == len(recipients):
            for recipient, link in zip(recipients, links):
                message = email_body.format(link=link)
                try:
                    smtp.sendmail(email_sender, recipient, message)
                except Exception:
                    failed_emails.append(recipient)
        else:
            for recipient in recipients:
                try:
                    smtp.sendmail(email_sender, recipient, email_body)
                except Exception:
                    failed_emails.append(recipient)

        smtp.quit()
    except Exception as e:
        return util.add_cors_headers({"statusCode": 500, "body": "Error: " + traceback.format_exc()})

    if failed_emails:
        return util.add_cors_headers({"statusCode": 400, "body": f"List of emails failed: {failed_emails}"})

    return util.add_cors_headers({"statusCode": 200, "body": "Success!"})


def send_email(recipient, link, template, sender):
    """
    Sends an email to one person - recipient with the link.
    If "forgot", use the forgotten password template.

    If not "forgot" sender needs to be non None.
    """
    # if no sender is given (for something like forgotten password), the sender is set to be the recipient
    if sender is None:
        sender = util.coll("users").find_one({"email": recipient})
    return do_substitutions([recipient], [link], template, sender)


@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "template": {"type": "string"},
        "recipients": {"type": "array"}
    },
    "required": ["token", "template"]
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
    the email key of every returned document is emailed.  If both lists are provided, 
    only the 'recipients' list is used.

    If there is a 'recipients' list and a 'link' key is provided, it is assumed
    that the 'link' is an array of corresponding links to substitute for each
    recipient. This substitution is performed using "do_substitutions" specified
    above.  If the lengths of the links and recipients are unequal, an error will throw.
    If a 'query' is provided, it will be ignored as only the 'recipients'
    list will be used.
    """
    # disallow non-director users from sending emails to anyone but themselves
    if not usr['role']['director'] and event.get('recipients', []) != [usr['email']]:
        return {'statusCode': 400, 'body': "Not authorized to send emails!"}
    else:  # note, below this point, we can assume usr is a director or that the recipients list has length 1.
        # recall that a non-director cannot have this: they must have "recipients"
        if 'query' not in event and 'recipients' not in event:
            return {'statusCode': 204, 'body': "No recipients or query provided!"}
        elif 'query' in event and 'recipients' not in event:
            # if there is query, then read_info is called
            queried = read_info(event, context)
            if queried['statusCode'] != 200:
                return queried
            event['recipients'] = []
            # if there is an error running the provided query, tries to assume recipients using any emails in query
            queried = json.loads(queried['body'])
            for user in queried:
                if 'email' in user:
                    event['recipients'].append(user['email'])
            # in case no recipients can be assumed, complains
            if len(event['recipients']) == 0:
                return {'statusCode': 204, 'body': "No recipients found!"}
        # if links are given, then the appropriate method is called to send emails
        elif 'links' in event:
            return do_substitutions(event['recipients'], event['links'], event['template'], usr)
        # in case any recipients were specified (without links) or were assumed using the query, then email is sent to
        # these recipients with the provided template
        return do_substitutions(recipients=event['recipients'], links = None, template=event['template'], user = None)
