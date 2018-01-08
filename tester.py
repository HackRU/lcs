import requests
import json
import config
from pymongo import MongoClient

def test(url):
    user_email = "team@nonruhackathon.notemail.com"
    passhash = 42
    usr_dict = {'email': user_email, 'password': passhash}
    auth = requests.post(url + '/authorize', json=(usr_dict))
    print("Non-existant: ", auth.text)

    user_email = "hemangandhi@gmail.com"
    usr_dict = {'email': user_email, 'password': passhash}
    auth = requests.post(url + '/authorize', json=(usr_dict))
    print("Bad password: ", auth.text)

    passhash = 12345
    usr_dict = {'email': user_email, 'password': passhash}
    auth = requests.post(url + '/authorize', json=(usr_dict))
    token = json.loads(auth.json()['body']).get('authtoken')
    print("Got token:", token)
    if token is None:
        print("Bad token")
        print("Got: ", auth.text)
        return

    val_dict = {'email': user_email, 'authtoken': token}
    valid = requests.post(url + '/validate', json=(val_dict))
    print("From validate:", valid.text)

    rando = "the.scrub@rutgers.edu"
    val_dict = {'user_email': rando, 'authtoken': token, 'auth_email': user_email}
    valid = requests.post(url + '/update', json=(val_dict))
    print("From update:", valid.text)

    #trying to test MLH Callback
    mlh_url = 'https://my.mlh.io/oauth/authorize?client_id={}&redirect_uri={}&response_type={}&scope=email+education+birthday'

    #create user
    fake_user = {
            'email': 'testing@hackru.org',
            'role': 'hacker',
            'password': 'defacto',
            'sp_pass': 'why do I exist?'
    }
    auth = requests.post(url + '/create', json=fake_user)
    print("Token for our new user:", auth.text)

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)
    test = db['test']
    test.delete_one({'email': 'testing@hackru.org'})

if __name__ == "__main__":
    from sys import argv
    if len(argv) < 2:
        print("USAGE:", argv[0], "<URL of the lambdas>")
    else:
        test(argv[1])
