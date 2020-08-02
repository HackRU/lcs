echo "Setting up node"
bash setup.sh;

echo "Copying config"
#Copy the config
cp config.dev.py config.py

#Exporting necessary environment variables
echo "Setting up environment variables for permissions"

echo "Copying env vars to .env"
declare -a env_vars=( 
 "DEVELOP_GOOGLE_CAL_CLIENT_ID"
 "DEVELOP_GOOGLE_CAL_CLIENT_SECRET"
 "DEVELOP_GOOGLE_CAL_ID"
 "DEVELOP_SPARKPOST_KEY"
 "DEVELOP_MAPS_API_KEY"
 "DEVELOP_DB_URI"
 "DEVELOP_JWT_SECRET"
 "DEVELOP_JWT_ALGO"
 "DEVELOP_MAX_REIMBURSE"
 "DEVELOP_TRAIN_REIMBURSE"
 "DEVELOP_TRAVEL_BUDGET"
 "DEVELOP_CAR_REIMBURSE"
 "DEVELOP_BUS_REIMBURSE"
 "DEVELOP_PLANE_REIMBURSE"
 "DEVELOP_SLACK_API_TOKEN")

echo "For loop"
## now loop through the above env_vars
for i in "${env_vars[@]}"
do
   echo -e "$i=\c" >> .env.dev
   printenv $i >> .env.dev
done

# Deploying!
echo "Deploying!"
npx serverless deploy --stage dev 