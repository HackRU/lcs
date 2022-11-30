import datetime
import json
import time

import requests
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from pymongo import DESCENDING
from src import util
import config


@util.cors
def google_cal(event, context, testing=False):
    if not config.GOOGLE_CAL.CAL_API_KEY:
        return {'statusCode': 500, 'body': 'Google API key not configured'}

    if not config.GOOGLE_CAL.CAL_ID:
        return {'statusCode': 500, 'body': 'Google Calendar ID not set'}

    num_events = event.get('num_events', 10)

    try:
        service = discovery.build('calendar', 'v3', developerKey=config.GOOGLE_CAL.CAL_API_KEY, cache_discovery=False)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        # pylint: disable=no-member
        events_result = service.events().list(calendarId=config.GOOGLE_CAL.CAL_ID, timeMin=now, maxResults=num_events * 5,
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        return {'statusCode': 200, 'body': events}
    except HttpError as err:
        return {'statusCode': 500,
                'body': 'Encountered a Google Calendar API error: '+ json.loads(err.args[1])["error"]["message"]}


def slack_announce(event, context):
    slacks = util.coll('slack messages')
    num_messages = event.get('num_messages', 30)

    def refresh_cache():
        # refresh cache
        token = config.SLACK_KEYS['token']
        channel = config.SLACK_KEYS['channel']
        url = 'https://slack.com/api/conversations.history'
        params = {'channel': channel, 'limit': num_messages}
        headers = {"Authorization": "Bearer {}".format(token)}
        result = requests.get(url, params=params, headers=headers)
        reply = result.json()
        if not reply.get('ok'):
            return util.add_cors_headers({'statusCode': 400, 'body': 'Unable to retrieve messages'})

        # clean up the slack response
        all_messages = reply.get('messages')
        if not all_messages:
            return util.add_cors_headers({'statusCode': 400, 'body': 'No messages found.'})
        messages = list(filter(lambda x: x.get('type') == 'message' and 'subtype' not in x, all_messages))
        now_for_slack = str(time.time())
        for msg in messages:
            # update the cache
            msg['c_ts'] = now_for_slack
            m = list(slacks.find({'text': msg['text']}))
            if m is None or m == [] or m == ():
                slacks.insert_one(msg)
            else:
                slacks.update_one({'text': msg['text']}, {'$set': {'c_ts': msg['c_ts']}})
        return messages

    # check cache
    cache = list(slacks.find().sort([('c_ts', DESCENDING)]).limit(1))
    if len(cache) == 1:
        latest_msg = cache[0]
        msg_time = datetime.datetime.utcfromtimestamp(float(latest_msg['ts']) / 1e3)
        if msg_time + datetime.timedelta(minutes=10) > datetime.datetime.now():
            # cache hit
            messages = list(slacks.find().sort([('ts', DESCENDING)]).limit(num_messages))
            for msg in messages:
                del msg['_id']
        else:
            messages = refresh_cache()
    else:
        messages = refresh_cache()

    return util.add_cors_headers({'statusCode': 200, 'body': messages})
