import imaplib
import email
import time 
import json 
import config

from testing_utils import *
from src import emails
import pytest
import mock

#look at line 29 comment of emails.py, works here though, maybe cause using imap.login
email_test = config.EMAIL_ADDRESS
email_password = config.EMAIL_PASSWORD

# Connect to inbox
imap_server = imaplib.IMAP4_SSL(host='imap.gmail.com')
imap_server.login(email_test, email_password)
imap_server.select()  # Default is `INBOX`

def test_forgot_password_link():
    
    link = 'https://hackru.org/'

    #Send_email function and hard timer here
    emails.send_email(email_test, link, "FORGOT_PASSWORD", email_test)
    time.sleep(2)

    #Get latest message in inbox
    _, message_numbers_raw = imap_server.search(None, 'ALL')
    message_list = message_numbers_raw[0].split()
    message_number = message_list[len(message_list)-1]
    _, msg = imap_server.fetch(message_number, '(RFC822)')
    message = email.message_from_bytes(msg[0][1])

    #Closing connection and logging out
    imap_server.close()
    imap_server.logout()

    #Parse email sent and get template body
    sent_email_from = email.utils.parseaddr(message['from'])[1]
    sent_email_body = ''
    #Append each sub-message as get_payload returns body line by line (since it is multipart)
    for sub in message.get_payload():
        sent_email_body += sub
    sent_email_body = sent_email_body.replace('\r', '').strip()

    #Get file text and replace {link} in template
    template_text = open("templates/FORGOT_PASSWORD.txt").read().format(link=link)
    
    assert sent_email_from == email_test and sent_email_body == template_text

def test_forgot_password_link_bad_email():
    email_bogus = 'bogus'

    # Fail with email not belonging to any user
    res = emails.send_email(email_bogus, '', "FORGOT_PASSWORD", email_test)

    assert res['statusCode'] == 400 and res['body'] == f"List of emails failed: ['{email_bogus}']"

def test_email_bad_template():
    template_bogus = 'bogus'

    # Fail with template not matching to any file
    res = emails.send_email(email_test, '', template_bogus, email_test)
    assert res['statusCode'] == 400 and res['body'] == f"There is no template named {template_bogus}.txt"