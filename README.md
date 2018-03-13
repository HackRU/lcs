# HackRU-Application

Checkout `Camelot-saved` for the working node thingy we used before (TODO: archive it).
We are eternally grateful, Carlin.

## What is LCS?!

The ludicrous card system is a system where
applications offer "cards" so that users
can see everything in the same page.

This is the main authentication system.
It handles a bunch.
The hope is to deploy this as a bunch of AWS
Lambdas.

## How Ludicrous?

We ran a few hackathons off it so, pretty ludicrous.

## Real-talk: the API

So, the API has a few endpoints, each unto it's own lambda.
The HTTP details and deployment facts are provided too.

| Endpoint URL | Endpoint method | Python file | Function name | Proxy integrate? | Depends on? |
| --- | --- | --- | --- | --- | --- |
| /authorize | POST | authorize.py | authorize | No | Libraries: mongo |
| /create | POST | authorize.py | create_user | No | authorize function, mongo library |
| /mlhcallback | GET | authorize.py | mlh_callback | Yes | authorize and create_user functions |
| /validate | POST | validate.py | validate | No | Mongo library |
| /update | POST | validate.py | update | No | Mongo library. There is a large helper function too |
| /qr | POST | qru.py | email2qr | Yes | Pillow. This includes a shared library that needs ubuntu to correctly install |

### The authorize endpoint

Given an unhashed password and the user's email, issues a token for the user.
This token represents that the user is logged in and can be
used to query the rest of the API on the user's behalf.

The endpoint expects the following JSON in the body of the POST:
```JSON
{
    "email": "users@email.here",
    "password": "user's password here."
}
```
Upon validity, the following JSON is returned:
```JSON
{
    "auth": {
        "token": "a mangled hash brown",
        "email": "users@email.here",
        "valid_until": "time for 3 hours from now"
    }
}
```
On failure, expect an error string we think of as informative.

### The create endpoint

Given the JSON for a user in the post, with
at least an email and a password, creates the user.
Here is some JSON:
```JSON
    {
        "email": "users@email.here",
        "password": "users password here",
        "github": "their fancy git, if you have it",
        "major": "their major, if known to you",
        "short_answer": "HackRU does an application question and the answer is stored here, if known",
        "shirt_size": "shirt size if known",
        "first_name": "their name (optional)"
        "last_name": "their last name (optional)"
        "dietary_restrictions": "what they can't eat, if known.",
        "special_needs": "Their special needs if known",
        "date_of_birth": "yyyy-mm-dd", //optional
        "school": "Which school they go to. Optional. Remember Penn State doesn't count.",
        "grad_year": "yyyy", //optional
        "gender": "their gender. Optional - both in and not in the liberal sense",
        "registration_status": "unregistered", //<- should be the default, though you can pass this in.
        "level_of_study": "What level of college they're in, what degree they want. If you know it."
    }
```
This will result in
```JSON
{
    "auth": {
        "token": "a mangled hash brown",
        "email": "users@email.here",
        "valid_until": "time for 3 hours from now"
    }
}
```
on success and a string we hope informs you on failure.
