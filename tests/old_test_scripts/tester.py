import requests
import json
import config
import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient
from validate import validate_updates
from random import sample, randint
from functools import reduce
from sys import argv
from src.validate import validate_updates

def e2e_test(url):
    """
    Assumes all endpoints are correctly up at url
    and runs through some standard queries.
    """

    # failed log in: no email or password
    user_email = "team@nonruhackathon.notemail.com"
    passhash = '42'
    usr_dict = {'email': user_email, 'password': passhash}
    auth = requests.post(url + '/authorize', json=(usr_dict))
    print("Non-existant: ", auth.text)

    # the other failure case: wrong password
    user_email = "hemangandhi@gmail.com"
    usr_dict = {'email': user_email, 'password': passhash}
    auth = requests.post(url + '/authorize', json=(usr_dict))
    print("Bad password: ", auth.text)

    # log in succeeds.
    passhash = "12345"
    usr_dict = {'email': user_email, 'password': passhash}
    auth = requests.post(url + '/authorize', json=(usr_dict))
    res = auth.json()['body']
    token = json.loads(res).get('auth')
    token = token is not None and token.get('token')
    print("Got token:", token)
    if token is None:
        print("Bad token")
        print("Got: ", auth.text)
        return

    # make sure that validation indeed validates the valid token.
    val_dict = {'email': user_email, 'authtoken': token}
    valid = requests.post(url + '/validate', json=(val_dict))
    print("From validate:", valid.text)

    # update a random user.
    rando = "the.scrub@rutgers.edu"
    val_dict = {'user_email': rando, 'auth': token, 'auth_email': user_email}
    valid = requests.post(url + '/update', json=(val_dict))
    print("From update:", valid.text)

    # trying to test MLH Callback
    mlh_url = 'https://my.mlh.io/oauth/authorize?client_id={}&redirect_uri={}&response_type={}&scope=email+education+birthday'

    # create user
    fake_user = {
            'email': 'testing@hackru.org',
            'password': 'defacto',
    }
    auth = requests.post(url + '/create', json=fake_user)
    token = auth.json()['body']
    token = json.loads(token)['auth']['token']

    # read the newborn user.
    query_d = {
            'email': 'testing@hackru.org',
            'token': token,
            'query': {'email': 'testing@hackru.org'}
    }
    read = requests.post(url + '/read', json=(query_d))
    print(read.text)

    # update our newborn
    upd_val = {
            'user_email': 'testing@hackru.org',
            'auth_email': 'testing@hackru.org',
            'auth': token,
            'updates': {'github': '11'}
    }
    upd = requests.post(url + '/update', json=upd_val)
    print(upd.text)

    # delete the newborn. (Infanticide.)
    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    test = db[config.DB_COLLECTIONS['users']]
    u = test.find_one({'email': 'testing@hackru.org'})
    print(u['github'])
    test.delete_one({'email': 'testing@hackru.org'})

def update_validation_test(random = True):
    """
    A long series of unit tests for the update validator.
    Only assumes that update exists - no web/DB assumptions
    made.
    """
    token = str(uuid.uuid4())

    update_val = {
    }
    # a different fake user (I waste so much time).
    fake_usr = {
        "_id": "The Mongo Longo",
        "email": "doesnt@matter.horn",
        "auth": {
            "token": token,
            "valid_until": (datetime.now() + timedelta(days=3)).isoformat()
        },
        "role": {
            "hacker": True,
            "volunteer": False,
            "judge": False,
            "sponsor": False,
            "mentor": False,
            "organizer": False,
            "director": False
        },
        "password": "Ross' brother, Hash Brown",
        "github": "m3m3s",
        "major": "major major major major",
        "short_answer": "Shyam, the shortest of answers.",
        "shirt_size": "epsilon",
        "first_name": "TooMac",
        "last_name": "Fun",
        "dietary_restrictions": "Can't eat food",
        "special_needs": "Every",
        "date_of_birth": "2/23/2018",
        "school": "Princeton Day Care",
        "grad_year": "Eventual",
        "gender": "Undecidable",
        "registration_status": "unregistered",
        "level_of_study": "Low",
        "mlh": False,
        "day_of":{
            "checkIn": False
        },
        "votes": -1
    }
    # A fake director
    fake_auth = {
        "role": {
            "director": True,
            "organizer": True
        }
    }

    def try_to_alter_key(key, usr_can, admin_can, value = None, op = '$set'):
        """
        Generate the update dictionary (passed to update),
        whether the user should be able to do the update,
        whether an admin should be able to do the update,
        and an optional value to update to.
        Optionally, use a specific operation. Defaults to '$set'.
        """

        #the dictionary is trivial
        upd_dict = {op: {key: value}} # {$set: {key: "Dummy"} }

        #if the update should work, the key should be present
        #in the validated update dictionary.
        if usr_can:
            usr = lambda x: key in x[op]
        else:
            #otherwise not.
            usr = lambda x: key not in x[op]

        #ditto ^.
        if admin_can:
            admin = lambda x: key in x[op]
        else:
            admin = lambda x: key not in x[op]

        return (upd_dict, usr, admin)

    # all the test cases. Test name maps to the update and whether the user and admin
    # should be able to perform the update.
    try_to_fuck_with = {
        "auth_general": try_to_alter_key("auth",False,False),
        "the number of votes": try_to_alter_key("votes", False, True),
        "the _id field": try_to_alter_key("_id", False, False),
        "the role object": try_to_alter_key("role", False, False),
        "the innards of role": try_to_alter_key("role.director", False, True),
        "being a volunteer": try_to_alter_key("role.volunteer", True, True),
        "not being a hacker": try_to_alter_key("role.hacker", False, True),
        "being a mentor": try_to_alter_key("role.mentor", True, True),
        "being an organizer": try_to_alter_key("role.organizer", False, True),
        "email key": try_to_alter_key("email", False, False),
        "mlh key": try_to_alter_key("mlh", False, False),
        "password key": try_to_alter_key("password", False, False),
        "adding a new key": try_to_alter_key("shite", True, True),
        "voting from": try_to_alter_key("votes_from", False, True),
        "skipping voting": try_to_alter_key("skipped_users", False, True)

    }

    if random:
        # making arbitrary intersections of the above
        def intersect(t1, t2):
            """Given two functions, returns their "and"."""
            return lambda x: t1(x) and t2(x)

        def merge_dicts(d1, d2):
            """
            Returns sorta d1.merge(d2),
            but without altering d1 or d2.
            This is also specialized to merge for each operation.
            """
            # I'm too sexy for the standard library.
            d = dict()
            for op in d1:
                d[op] = dict()
                d[op].update(d1[op])
                if op in d2:
                    d[op].update(d2[op])
            for op in d2:
                d[op] = dict()
                d[op].update(d2[op])
                if op in d1:
                    d[op].update(d1[op])
            return d

        for i in range(5):
            # we randomly sample a random number of tests
            # and "and" all the lambdas. We also merge the
            # update dictionaries. This is equivalent to
            # "anding" the above conditions at random.
            new_test = sample(list(try_to_fuck_with),\
                    randint(2, len(try_to_fuck_with)) )
            new_dict = reduce(merge_dicts, (try_to_fuck_with[i][0] for i in new_test))
            new_usr_valid = reduce(intersect, (try_to_fuck_with[i][1] for i in new_test))
            new_admin_valid = reduce(intersect, (try_to_fuck_with[i][2] for i in new_test))
            # we add our random test case after making all the components.
            try_to_fuck_with[str(new_dict)] = (new_dict, new_usr_valid, new_admin_valid)

    # these tests cannot intersect one another, so we have them after intersections.
    # (ie. they're mutually exclusive.)
    try_to_fuck_with.update({
        "getting registered": try_to_alter_key("registration_status", True, True, "registered"),
        "registration state leaps": try_to_alter_key("registration_status", False, False, "checked-in"),
        "bad registration values": try_to_alter_key("registration_status", False, False)
    })

    for name in try_to_fuck_with:
        # get the test case
        upd, usr_valid, admin_valid = try_to_fuck_with[name]
        # document our activity.
        print("Trying to fuck with", name)
        # clean up the updates and see if we got what we expected.
        usr_cleaned = validate_updates(fake_usr, upd)
        admin_cleaned = validate_updates(fake_usr, upd, fake_auth)

        if usr_valid(usr_cleaned):
            print("User case worked")
        else:
            print("User case failure, got:", usr_cleaned)

        if admin_valid(admin_cleaned):
            print("Admin case worked")
        else:
            print("Admin case failure, got:", usr_cleaned)

if __name__ == "__main__":
    if len(argv) < 2:
        print("Defaulting to update validation")
        update_validation_test()
    else:
        e2e_test(argv[1])
