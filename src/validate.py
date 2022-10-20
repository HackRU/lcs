import re

import googlemaps as gm

from src.schemas import ensure_schema, ensure_logged_in_user

from src import util

import config



@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"}
    },
    "required": ["token"]
})
@ensure_logged_in_user()
def validate(event, context, user=None):
    """
    Given a token, ensure that the token is an unexpired token of the user with the provided email.
    """
    return {"statusCode": 200, "body": user, "isBase64Encoded": False}


def validate_updates(user, updates, auth_usr=None):
    """
    Ensures that the user is being updated in a legal way. Invariants are explained at line 116 for most fields and
    65 for the registration_status in detail.
    """

    # if the user updating is not provided, we assume the user's updating themselves.
    if auth_usr is None:
        auth_usr = user

    # quick utilities
    # rejects all updates
    def say_no(x, y, z):
        return False

    # rejects updates from anyone BUT organizer and director
    def say_no_to_non_admin(x, y, z):
        return auth_usr['role']['organizer'] or auth_usr['role']['director']

    # rejects updates from hacker
    def say_no_to_just_hacker(x, y, z):
        return auth_usr['role']['organizer'] or auth_usr['role']['director'] or auth_usr['role']['volunteer']

    # creates a Google Map client
    gmaps = gm.Client(config.MAPS_API_KEY)

    def check_addr(y):
        try:
            location = gmaps.geocode(y)
            return True
        except gm.exceptions.ApiError:
            return False

    def check_registration(old, new, op):
        """
        Ensures that an edge exists in the user state graph and that the edge can be traversed by this mode of update.
        "True" edges are traversible by the user or through an admin whereas "False" ones require admin intervention.
        We only '$set' this field.
        """
        state_graph = {
            "unregistered": {  # unregistered = did not fill out all of application.
                "registered": True  # they can fill out the application.
            },
            "registered": {  # they have filled out the application.
                # all transitions out of this are through the voting
                # system are require admins to have voted.
                "rejected": False,
                "confirmation": False,
                "waitlist": False
            },
            "rejected": {  # the user is "rejected". REMEMBER: they see "pending"
                # only an admin may check a user in.
                "checked-in": False
            },
            "confirmation": {  # This is when a user may or may not RSVP.
                # they get to choose if they're coming or not.
                "coming": True,
                "not-coming": True
            },
            "coming": {  # they said they're coming.

                # they may change their mind, but only we can finalize things.
                "not-coming": True,
                "confirmed": False,
                "checked-in": False  # TODO: remove when there are many waves
            },
            "not-coming": {  # the user said they ain't comin'.

                # They can always make a better decision. But only we can finalize their poor choice.
                "coming": True,
                "waitlist": False
            },
            "waitlist": {  # They were waitlisted. (Didn't RSVP, or not-coming.)
                # Only we can check them in.
                "checked-in": False
            },

            "confirmed": {  # They confirmed attendance and are guaranteed a spot!
                # But only we can check them in.
                "checked-in": False,
                # bailing at the last minute
                "waitlist": True
            }
        }
        # the update is valid if it is an edge traversible in the current mode of update.
        return old in state_graph and new in state_graph[old] \
            and (state_graph[old][new] or say_no_to_non_admin(1, 2, 3)) \
            and op == "$set"

    # For all fields, we map a regex to a function of the old and new value and the operator being used. The function
    # determines the validity of the update. We "and" all the regexes, so an update is valid for all regexes it matches,
    # not just one.
    validator = {
        # this is a Mongo internal. DO NOT TOUCH.
        '_id': say_no,
        #TODO: we have to figure out "forgot password"
        'password': say_no,
        # no hacks on the role object
        '^role$': say_no,
        # can't me self-made judge?
        'role\\.judge': say_no_to_non_admin, #TODO: do magic links need these?
        # can't unmake hacker
        'role\\.hacker': say_no_to_non_admin,
        # can't self-make organizer or director
        'role\\.director': say_no_to_non_admin,
        'role\\.organizer': say_no_to_non_admin,
        # can't change email
        'email': say_no,
        # can't change your own votes
        'votes': say_no_to_non_admin,
        'votes_from': say_no_to_non_admin,
        'skipped_users': say_no_to_non_admin,
        # or MLH info
        'mlh': say_no,
        # no destroying the day-of object
        'day_of': say_no_to_just_hacker,
        'day_of\\.[A-Za-z1-2_]+': say_no_to_just_hacker,
        'registration_status': check_registration,
        # auth tokens are never given access
        'token': say_no,
        # travel info
        'travelling_from\\.mode': lambda x, y, z: y in ('bus', 'train', 'car', 'plane'),
        'travelling_from\\.formatted_addr': lambda x, y, z: check_addr(y),
        'slack_id': lambda x, y, z: re.match(r"^[UW][A-Z0-9]{2,}$", y) is not None,

    }

    def find_dotted(key):
        """
        Traverse the dictionary, moving down the dots (ie. role.mentor indicates the mentor field within the role object
         within the user).
        """
        curr = user
        for i in key.split('.'):
            if i not in curr:

                # We assume that absence means the addition of a new field, which we allow.
                return None
            curr = curr[i]
        return curr

    def validate(key, op):
        """
        Finds out if a key is present in the object. If it is, ensure that for each regex it matches (from the validator
         - line 116), the validator accepts the change. Returns a boolean.
        """
        usr_attr = find_dotted(key)
        for item in validator:
            if re.match(item, key) is not None:
                if not validator[item](usr_attr, updates[op][key], op):
                    return False
        return True

    # return all the valid updates that can be performed
    return {i: {j: updates[i][j] for j in updates[i] if validate(j, i)} for i in updates}


# TODO: get this to replace the above fn
@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "user_email": {"type": "string", "format": "email"},
        "updates": {
            "type": "object",
            "properties": {
                "$set": {"type": "object"},
                "$inc": {
                    "type": "object",
                    "properties": {
                        "votes": {"type": "number"}
                    },
                    "additionalProperties": False
                },
                "$push": {
                    "type": "object",
                    "properties": {
                        "votes_from": {"type": "string", "format": "email"},
                        "skipped_users": {"type": "string", "format": "email"}
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["user_email", "token", "updates"]
})
@ensure_logged_in_user()
def update(event, context, auth_user):
    """
    Given a user email, a token, and the dictionary of updates, performs all updates the
    authorised user is permitted to, from the "updates" object, on the user with email "user_email".
    """

    user_coll = util.coll('users')

    # assuming the user is authorised through the token, find the user being modified.
    # if the user making changes is the same the one to be updated, no need for extra lookups
    if event['user_email'] == auth_user['email']:
        # save a query in the nice case
        results = auth_user
    # if the user is an admin, they may modify any user.
    elif auth_user['role']['organizer'] or auth_user['role']['director']:
        results = user_coll.find_one({"email": event['user_email']})
    else:
        return {"statusCode": 403, "body": "Permission denied"}

    # ensure that the user was indeed found.
    if results is None or results == [] or results == {}:
        return {"statusCode": 400, "body": "User email not found."}

    # validate the updates, passing only the allowable ones through.
    updates = validate_updates(results, event['updates'], auth_user)
    #May need to be more descriptive (say which updates failed specific)
    if len(updates) == 0:
        return {"statusCode": 403, "body": "No provided updates were valid."}
    # update the user and report success.
    user_coll.update_one({'email': event['user_email']}, updates)
    return {"statusCode": 200, "body": "Successful request."}
