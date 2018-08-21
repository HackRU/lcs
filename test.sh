#! /bin/bash

# 1) Now you don't always have to copy paste the damn URL
# 2) Deploys go sideways from within a venv, I think.

source venv/bin/activate
cp config.test.py config.py
# python tester.py https://m7cwj1fy7c.execute-api.us-west-2.amazonaws.com/test
python tester.py https://7c5l6v7ip3.execute-api.us-west-2.amazonaws.com/lcs-test
rm config.py
deactivate
