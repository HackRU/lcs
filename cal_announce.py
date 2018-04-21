#!/usr/bin/env python

import httplib2
import os
from shutil import copy2
import oauth2client
import datetime
import dateutil.parser as dp

#from oauth2client import tools
from oauth2client.file import Storage
from oauth2client import tools, client
from googleapiclient import discovery

import requests
from pymongo import MongoClient
import json
import config

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar Python API Quickstart'

def google_cal(event, context, testing=False):
    num_events = event.get('num_events', 10)
    credential_path = 'calendar-python-quickstart.json'
    copy2('calendar-python-quickstart.json', '/tmp/')
    store = Storage('/tmp/' + credential_path)
    credentials = store.get()
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
    eventsResult = service.events().list(
            calendarId = 'hl4bsn6030jr76nql68cen2jto@group.calendar.google.com', timeMin = now, maxResults = num_events * 5,
            singleEvents = True, orderBy = 'startTime').execute()
    events = eventsResult.get('items', [])
    #if not events:
    #    print("no events found")
    #for event in events:
    #    start = event['start'].get('dateTime', event['start'].get('date'))
    #    print(start, event['summary'])
    if not events:
        return config.add_cors_headers({'statusCode': 400, 'body': 'Unable to get events.'})
    return config.add_cors_headers({'statusCode': 200, 'body': events})

def slack_announce(event, context):
    #DB connection
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER,config.DB_PASS)
    slacks = db['slack-msgs']

    update = False
    iso_time = datetime.datetime.utcnow().isoformat()
    sentinal = slacks.find_one({'type': 'sentinal'})
    def do(): pass

    if sentinal == None:
        do = lambda: slacks.insert({'type': 'sentinal', 'time': iso_time})
        update = True
    elif dp.parse(sentinal['time']) < datetime.timedelta(minutes=10) + datetime.datetime.now():
        do = lambda: slacks.update({'type': 'sentinal'}, {'time': iso_time})
        update = True

    print(update, sentinal)

    if update:
        num_messages = event.get('num_messages', 30)
        token = config.SLACK_KEYS['token']
        channel = config.SLACK_KEYS['channel']
        url = 'https://slack.com/api/channels.history?token={}&channel={}&count={}'.format( token, channel, num_messages)
        result = requests.get(url)
        reply = result.json()
        if not reply.get('ok'):
            return config.add_cors_headers({'statusCode': 400, 'body': 'Unable to retrieve messages'})
        allMessages = reply.get('messages')
        if not allMessages:
            return config.add_cors_headers({'statusCode': 400, 'body': 'No messages found.'})
        messages = list(filter(lambda x: x.get('subtype') != 'channel_join', allMessages))
        tenMessages = messages[:num_messages]
        for msg in tenMessages:
            m = list(slacks.find(msg))
            print(m)
            if m == None or m == []:
                print(msg)
                slacks.insert(msg)
        do()

    return config.add_cors_headers({'statusCode': 200, 'body': list(slacks.find({'type': {'$ne': 'sentinal'}}))})
