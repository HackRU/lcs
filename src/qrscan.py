from datetime import datetime, timezone
from src.schemas import ensure_schema, ensure_logged_in_user, ensure_role
import pymongo
from src.util import coll

def dbinfo():
    user_coll = coll("users")
    print("collection name: " + str(user_coll.name))
    print("collection database: " + str(user_coll.database))
    print("collection document count: " + str(user_coll.count_documents))


@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "link_email": {"type": "string"},
        "qr_code": {"type": "string"}
    },
    "required": ["token", "link_email", "qr_code"]
})
@ensure_logged_in_user()
@ensure_role([['director', 'organizer', 'volunteer']])
def qr_match(event, context, user=None):
    """
    Function used to associate a given QR code with the given email
    """
    user_coll = coll('users')

    result = user_coll.update_one({'email': event["link_email"]}, {'$push': {'qrcode': event["qr_code"]}})
    if result.matched_count == 1:
        return {"statusCode": 200, "body": "success"}
    else:
        return {"statusCode": 404, "body": "User not found"}


@ensure_schema({
    'type': 'object',
    'properties': {
        'token': {'type': 'string'},
        'qr': {'type': 'string'},
        'event': {'type': 'string'},
        'point': {'type': 'integer'},
        'again': {'type': 'boolean'}
    },
    'required': ['token', 'qr', 'event']
})
@ensure_logged_in_user()
@ensure_role([['director', 'organizer', 'volunteer']])
def attend_event(aws_event, context, user=None):
    """
    Function used to mark that a user has attended an event
    """
    users = coll('users')
    houses = coll('houses')
    qr = aws_event['qr']
    event = aws_event['event']
    again = aws_event.get('again', False)
    point = aws_event.get('point', 0)

    # in case user accidentally put a negative number
    if point < 0:
        point = 0

    def attend(user):
        # if the user has already attended the event and is not an event that can be re-attended, complain
        if not again and user['day_of'].get(event, 0) > 0:
            return {'statusCode': 402, 'body': 'user already checked into event'}
        # update the user data to reflect event attendance by incrementing the count of the event by the variable 'point'
        new_user = users.find_one_and_update({'email': user['email']},
                                                { 
                                                    '$inc': {'day_of.' + event: 1},
                                                    '$push': {'day_of.timestamps.' + event: datetime.utcnow()}
                                                },
                                             return_document=pymongo.ReturnDocument.AFTER)

        # update the user's house points to reflect event attendance by incrementing it by the variable 'point'
        update_points = houses.find_one_and_update({"name": new_user['house']}, 
                                                   {
                                                       '$inc': {'points': point}
                                                   },
                                                return_document=pymongo.ReturnDocument.AFTER)

        return {'statusCode': 200, 'body': {'email': new_user['email'], 'new_count': new_user['day_of'][event], 'user_house': new_user['house']}}

    # TODO: revisit if it's valid for qr to be an email
    user = users.find_one({'email': qr})
    if user is not None:
        return attend(user)

    # find the user using the QR code from the database
    user = users.find_one({'qrcode': qr})
    if user is not None:
        return attend(user)

    return {'statusCode': 404, 'body': 'user not found'}
