import datetime
import dateutil.parser as dp
import os
import time

from googleapiclient import discovery
from google_auth_oauthlib import get_user_credentials
from google.auth.transport.requests import Request
from pymongo import DESCENDING
import requests

import config
from config import GOOGLE_CAL
import pickle
import util

token_path = "./token.pickle"

def gen_token():
    creds = get_user_credentials(
        GOOGLE_CAL.SCOPES,
        GOOGLE_CAL.CLIENT_ID,
        GOOGLE_CAL.CLIENT_SECRET
    )
    # Save the credentials for the next run
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)

@util.cors
def google_cal(event, context, testing=False):
    num_events = event.get('num_events', 10)

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # IMPORTANT gen_token must be ran and authorized before uploading to lambda,
    # and token.pickle should be uploaded with it
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    else:
        return {'statusCode': 500, 'body': 'couldn\'t find stored authorization token in ' + os.getcwd()}
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
               return {'statusCode': 500, 'body': 'failed to refresh credentials'}
        else:
            return {'statusCode': 500, 'body': 'google calendar credentials invalid'}
    
    service = discovery.build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    # pylint: disable=no-member
    eventsResult = service.events().list(
            calendarId = GOOGLE_CAL.CAL_ID, timeMin = now, maxResults = num_events * 5,
            singleEvents = True, orderBy = 'startTime').execute()
    events = eventsResult.get('items', [])
    # TODO handle if there are no events
    if not events:
        return {'statusCode': 400, 'body': 'Unable to get events.'}
    return {'statusCode': 200, 'body': events}

def slack_announce(event, context):
    slacks = util.coll('slack messages')
    num_messages = event.get('num_messages', 30)

    def refresh_cache():
        #refresh cache
        token = config.SLACK_KEYS['token']
        channel = config.SLACK_KEYS['channel']
        url = 'https://slack.com/api/channels.history'
        params = {'token': token, 'channel': channel, 'count': num_messages}
        result = requests.get(url, params)
        reply = result.json()
        if not reply.get('ok'):
            return util.add_cors_headers({'statusCode': 400, 'body': 'Unable to retrieve messages'})

        #clean up the slack response
        allMessages = reply.get('messages')
        if not allMessages:
            return util.add_cors_headers({'statusCode': 400, 'body': 'No messages found.'})
        messages = list(filter(lambda x: x.get('type') == 'message' and 'subtype' not in x, allMessages))
        now_for_slack = str(time.time())
        for msg in messages:
            #update the cache
            msg['c_ts'] = now_for_slack
            m = list(slacks.find({'text': msg['text']}))
            if m == None or m == [] or m == ():
                slacks.insert_one(msg)
            else:
                slacks.update_one({'text': msg['text']}, {'$set': {'c_ts': msg['c_ts']}})
        return messages

    #check cache
    cache = list(slacks.find().sort([('c_ts', DESCENDING)]).limit(1))
    if len(cache) == 1:
        latest_msg = cache[0]
        msg_time = datetime.datetime.utcfromtimestamp(float(latest_msg['ts']) / 1e3)
        if msg_time + datetime.timedelta(minutes=10) > datetime.datetime.now():
            #cache hit
            messages = list(slacks.find().sort([('ts', DESCENDING)]).limit(num_messages))
            for msg in messages:
                del msg['_id']
        else:
            messages = refresh_cache()
    else:
        messages = refresh_cache()

    return util.add_cors_headers({'statusCode': 200, 'body': messages})
