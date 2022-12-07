from src.schemas import ensure_schema, ensure_logged_in_user, ensure_role
from src import util
from datetime import date, datetime

def tidy_results(res):
    """
    Function used to clean up read results before returning to the user
    """
    for i in res:
        del i['_id']
        del i['password']
    return res

def stringify_timestamps(res):
    """
    Function used to stringify timestamps from datetime format
    """
    for obj in res:
        if "timestamps" in obj["day_of"]:
            for event in obj["day_of"]["timestamps"]:
                for i in range(len(obj["day_of"]["timestamps"].get(event))):
                    obj["day_of"]["timestamps"].get(event)[i] = obj["day_of"]["timestamps"].get(event)[i] .isoformat()
    return res

@ensure_schema({
    "type": "object",
    "properties": {
        "query": {
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["major", "shirt_size", "dietary_restrictions", "school", "grad_year",
                                 "gender", "level_of_study", "ethnicity"]
                    },
                    "uniqueItems": True
                },
                "just_here": {"type": "boolean"}
            },
            "required": ["fields"]
        },
        "aggregate": {"type": "boolean", "const": True}
    },
    "required": ["query"]
})
def public_read(event, context):
    """
    Function responsible for performing a public read (can be requested by anyone)
    """
    # the fields to be aggregated
    fields = event['fields']
    # filter based on the just_here boolean indicating whether or not to aggregate on checked-in users
    match = {"$match": {"registration_status": ("checked-in" if event.get('just_here', False) else {"$ne": "unregistered"})}}
    # group by is performed using each of the fields requested
    group = {"$group": {"_id": {field: "$" + field for field in fields}, "total": {"$sum": 1}}}
    user_coll = util.coll('users')
    # aggregate's pipelining is used to fetch the results from the user data
    return {"statusCode": 200, "body": list(user_coll.aggregate([match, group]))}


def user_read(event, context, user):
    """
    Function used by a LCS user to fetch their information
    """
    # if the desired action is to aggregate, than it is no different from a public read
    if event.get('aggregate', False):
        return public_read(event, context)

    # otherwise, any reimbursement information is removed before sending that user's data back
    if user['registration_status'] in ['unregistered', 'registered', 'rejected']:
        if 'travelling_from' in user and 'reimbursement' in user['travelling_from']:
            del user['travelling_from']['reimbursement']
    
    return {"statusCode": 200, "body": stringify_timestamps([user])}


@ensure_role([['director', 'organizer']], on_failure=lambda e, c, u, *a: user_read(e, c, u))
def organizer_read(event, context, user):
    """
    Function responsible for performing an organizer query. In-case of insufficient permissions, falls back on user_read
    """
    # if aggregation is desired, a public read will suffice
    if event.get('aggregate', False):
        return public_read(event, context)

    # otherwise, the organizer submitted query is ran on the database and results are returned
    user_coll = util.coll('users')
    return {"statusCode": 200, "body": stringify_timestamps(tidy_results(list(user_coll.find(event['query']))))}


@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "query": {"type": "object"},
        "aggregate": {"type": "boolean"}
    },
    "required": ["query"]
})
@ensure_logged_in_user(on_failure=lambda e, c, u, *a: public_read(e, c))
@ensure_role([['director']], on_failure=lambda e, c, u, *a: organizer_read(e, c, u))
def read_info(event, context, user=None):
    """
    We allow for an arbitrary mongo query to be passed in.
    If the aggregate field is present and true, we aggregate
    and otherwise "find_one."
    If the endpoint is called by a non-LCS user, falls back upon public_read
    If the endpoint is called by a non-director, falls back upon organizer_read
    """
    tests = util.coll('users')

    if event.get('aggregate', False):
        return {"statusCode": 200, "body": stringify_timestamps(list(tests.aggregate(event['query'])))}
    return {"statusCode": 200, "body": stringify_timestamps(tidy_results(list(tests.find(event['query']))))}
