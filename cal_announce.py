#!/usr/bin/env python

import httplib2
import os
from shutil import copy2
import oauth2client
import datetime
import time
import dateutil.parser as dp

#from oauth2client import tools
from oauth2client.file import Storage
from oauth2client import tools, client
from googleapiclient import discovery

import requests
from pymongo import MongoClient, DESCENDING
import json
import config

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'HackRU calendar backend'

def google_cal(event, context, testing=False):
    num_events = event.get('num_events', 10)

    credential_path = 'calendar-python-quickstart.json'
    credentials = None
    store = Storage('/tmp/' + credential_path)
    try:
        copy2('calendar-python-quickstart.json', '/tmp/')
        credentials = store.get()
    except:
        if not testing:
            return config.add_cors_headers({'statusCode': 400, 'body': 'Misconfigured endpoint.'})

    if not credentials or credentials.invalid:
        if not testing:
            return config.add_cors_headers({'statusCode': 400, 'body': 'Please interactively generate client secret file.'})
        else:
            flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
            print("storing credentials to {}".format(credential_path))

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print("getting the next 10 events")
    # pylint: disable=no-member
    eventsResult = service.events().list(
            calendarId = config.GOOGLE_CAL_ID, timeMin = now, maxResults = num_events * 5,
            singleEvents = True, orderBy = 'startTime').execute()
    events = eventsResult.get('items', [])
    if not events:
        return config.add_cors_headers({'statusCode': 400, 'body': 'Unable to get events.'})
    return config.add_cors_headers({'statusCode': 200, 'body': events})

def slack_announce(event, context):
    #DB connection
    client = MongoClient(config.DB_URI)
    db = client[config.DB_NAME]
    db.authenticate(config.DB_USER, config.DB_PASS)
    slacks = db[config.DB_COLLECTIONS['slack messages']]
    num_messages = event.get('num_messages', 30)

    #check cache
    latest_msg = list(slacks.find().sort([('ts', DESCENDING)]).limit(1))[0]
    time = datetime.datetime.utcfromtimestamp(float(latest_msg['ts']) / 1e3)
    if time + datetime.timedelta(minutes=10) < datetime.datetime.now():
        #cache hit
        messages = list(slacks.find().sort([('ts', DESCENDING)]).limit(num_messages))
        for msg in messages:
            del msg['_id']
    else:

        #refresh cache
        token = config.SLACK_KEYS['token']
        channel = config.SLACK_KEYS['channel']
        url = 'https://slack.com/api/channels.history'
        params = {'token': token, 'channel': channel, 'count': num_messages}
        result = requests.get(url, params)
        reply = result.json()
        if not reply.get('ok'):
            return config.add_cors_headers({'statusCode': 400, 'body': 'Unable to retrieve messages'})

        #clean up the slack response
        allMessages = reply.get('messages')
        if not allMessages:
            return config.add_cors_headers({'statusCode': 400, 'body': 'No messages found.'})
        messages = list(filter(lambda x: x.get('type') == 'message' and 'subtype' not in x, allMessages))
        now_for_slack = str(time.time())
        for msg in messages:
            #update the cache
            msg['c_ts'] = now_for_slack
            m = list(slacks.find({'text': msg['text']}))
            if m == None or m == [] or m == ():
                slacks.insert(msg)
            else:
                slacks.update_one({'text': msg['text']}, {'$set': {'c_ts': msg['c_ts']}})

    return config.add_cors_headers({'statusCode': 200, 'body': messages})
