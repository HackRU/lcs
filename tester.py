import requests
import json
import config
from pymongo import MongoClient

def e2e_test(url):
    user_email = "team@nonruhackathon.notemail.com"
    passhash = 42
    usr_dict = {'email': user_email, 'password': passhash}
    auth = requests.post(url + '/authorize', json=(usr_dict))
    print("Non-existant: ", auth.text)

    user_email = "hemangandhi@gmail.com"
    usr_dict = {'email': user_email, 'password': passhash}
    auth = requests.post(url + '/authorize', json=(usr_dict))
    print("Bad password: ", auth.text)

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

    val_dict = {'email': user_email, 'authtoken': token}
    valid = requests.post(url + '/validate', json=(val_dict))
    print("From validate:", valid.text)

    rando = "the.scrub@rutgers.edu"
    val_dict = {'user_email': rando, 'auth': token, 'auth_email': user_email}
    valid = requests.post(url + '/update', json=(val_dict))
    print("From update:", valid.text)

    #trying to test MLH Callback
    mlh_url = 'https://my.mlh.io/oauth/authorize?client_id={}&redirect_uri={}&response_type={}&scope=email+education+birthday'

    #create user
    fake_user = {
            'email': 'testing@hackru.org',
            'password': 'defacto',
    }
    auth = requests.post(url + '/create', json=fake_user)
    token = auth.json()['body']
    token = json.loads(token)['auth']['token']

    query_d = {
            'email': 'testing@hackru.org',
            'token': token,
            'query': {'email': 'testing@hackru.org'}
    }
    read = requests.post(url + '/read', json=(query_d))
    print(read.text)

    upd_val = {
            'user_email': 'testing@hackru.org',
            'auth_email': 'testing@hackru.org',
            'auth': token,
            'updates': {'github': '11'}
    }
    upd = requests.post(url + '/update', json=upd_val)
    print(upd.text)

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)
    test = db['test']
    u = test.find_one({'email': 'testing@hackru.org'})
    print(u['github'])
    test.delete_one({'email': 'testing@hackru.org'})

def update_validation_test():
    from validate import validate_updates
    fake_usr = {
        "email": "doesnt@matter.horn",
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
        }
    }

    fake_auth = {
        "role": {
            "director": True
        }
    }

    def try_to_alter_key(key, usr_can, admin_can, value = "Dummy"):
        upd_dict = {key: "Dummy"}

        if usr_can:
            usr = lambda x: key in x
        else:
            usr = lambda x: key not in x

        if admin_can:
            admin = lambda x: key in x
        else:
            admin = lambda x: key not in x

        return (upd_dict, usr, admin)


    try_to_fuck_with = {
        "the role object": try_to_alter_key("role", False, False),
        "the innards of role": try_to_alter_key("role.director", False, True),
        "being a volunteer": try_to_alter_key("role.volunteer", True, True),
        "being a mentor": try_to_alter_key("role.mentor", True, True),
    }

    for name in try_to_fuck_with:
        upd, usr_valid, admin_valid = try_to_fuck_with[name]
        print("Trying to fuck with", name)
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
    from sys import argv
    if len(argv) < 2:
        print("Defaulting to update validation")
        update_validation_test()
    else:
        e2e_test(argv[1])
