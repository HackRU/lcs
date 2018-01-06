import requests
import json

def test(url):
    user_email = "team@nonruhackathon.notemail.com"
    passhash = 42
    auth = requests.post(url + '/authorize', json=json.dumps(usr_dict))
    print("Non-existant: ", auth.body)

    user_email = "hemangandhi@gmail.com"
    auth = requests.post(url + '/authorize', json=json.dumps(usr_dict))
    print("Bad password: ", auth.body)

    passhash = 12345
    usr_dict = {'email': user_email, 'password': passhash}
    auth = requests.post(url + '/authorize', json=json.dumps(usr_dict))
    token = auth.json()['authtoken']
    print("Got token:", token)

    val_dict = {'email': user_email, 'authtoken': token}
    valid = requests.get(url + '/validate', json=json.dumps(val_dict))
    print("From validate:", valid.body)

    rando = "the.scrub@rutgers.edu"
    val_dict = {'user_email': rando, 'authtoken': token, 'auth_email': user_email}
    valid = requests.get(url + '/update', json=json.dumps(val_dict))
    print("From update:", valid.body)

if __name__ == "__main__":
    import sys
    if len(argv) < 2:
        print("USAGE:", argv[0], "<URL of the lambdas>")
    else:
        test(argv[1])
