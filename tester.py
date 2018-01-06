import requests
import json

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
    token = auth.json().get('authtoken')
    print("Got token:", token)
    if token is None:
        print("Bad token")
        print("Got: ", auth.text)
        return

    val_dict = {'email': user_email, 'authtoken': token}
    valid = requests.get(url + '/validate', json=(val_dict))
    print("From validate:", valid.text)

    rando = "the.scrub@rutgers.edu"
    val_dict = {'user_email': rando, 'authtoken': token, 'auth_email': user_email}
    valid = requests.get(url + '/update', json=(val_dict))
    print("From update:", valid.text)

if __name__ == "__main__":
    from sys import argv
    if len(argv) < 2:
        print("USAGE:", argv[0], "<URL of the lambdas>")
    else:
        test(argv[1])
