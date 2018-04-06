#!/usr/bin/env python

import httplib2
#import os
#import oauth2client
import datetime
import argparse

#from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient import discovery

import urllib.request
import json

#flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
#CLIENT_SECRET_FILE = 'client_secret.json'
#APPLICATION_NAME = 'Google Calendar Python API Quickstart'

def google_cal(event, context):
    num_events = event.get('num_events', 10)
    #home_dir = os.path.expanduser('~')
    #credential_dir = os.path.join(home_dir, '.google_credential_dir')
    #credential_path = os.path.join(credential_dir, 'calendar-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    #if not credentials or credentials.invalid:
    #    flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    #    flow.user_agent = APPLICATION_NAME
    #    credentials = tools.run_flow(flow, store, flags)
    #    print("storing credentials to {}".format(credential_path))
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print("getting the next 10 events")
    eventsResult = service.events().list(
            calendarId = 'primary', timeMin = now, maxResults = num_events,
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
    num_messages = event.get('num_messages', 30)
    with open('token.txt') as f:
        s = f.read()
        token = s[:-1]
    with open('channel.txt') as f:
        s = f.read()
        channel = s[:-1]
    url = 'https://slack.com/api/channels.history?token={}&channel={}&count={}'.format( token, channel, num_messages)
    result = urllib.request.urlopen(url)
    reply = json.load(result)
    if not reply.get('ok'):
        return config.add_cors_headers({'statusCode': 400, 'body': 'Unable to retrieve messages'})
    allMessages = reply.get('messages')
    if not allMessages:
        return config.add_cors_headers({'statusCode': 400, 'body': 'No messages found.'})
    messages = list(filter(lambda x: x.get('subtype') != 'channel_join', allMessages))
    tenMessages = messages[:10]
    return config.add_cors_headers({'statusCode': 200, 'body': tenMessages})
