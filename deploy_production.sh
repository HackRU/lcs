#Copy the config
cp config.dev.py config.py
#Create token.pickle
echo $GOOGLE_CAL_TOKEN | base64 -d > token.pickle
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID_PRODUCTION};
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY_PRODUCTION};
