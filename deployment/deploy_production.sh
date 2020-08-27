bash ./deployment/setup.sh;

echo "Copying config"
#Copy the config
cp ./deployment/config.prod.py config.py

#Exporting necessary environment variables
echo "Setting up environment variables for permissions"

echo "Copying env vars to .env"
declare -a env_vars=(
 "PRODUCTION_GOOGLE_CAL_ID"
 "PRODUCTION_GOOGLE_CAL_API_KEY"
 "PRODUCTION_SPARKPOST_KEY"
 "PRODUCTION_MAPS_API_KEY"
 "PRODUCTION_DB_URI"
 "PRODUCTION_JWT_SECRET"
 "PRODUCTION_JWT_ALGO"
 "PRODUCTION_MAX_REIMBURSE"
 "PRODUCTION_TRAIN_REIMBURSE"
 "PRODUCTION_TRAVEL_BUDGET"
 "PRODUCTION_CAR_REIMBURSE"
 "PRODUCTION_BUS_REIMBURSE"
 "PRODUCTION_PLANE_REIMBURSE"
 "PRODUCTION_SLACK_API_TOKEN")

echo "For loop"
## now loop through the above env_vars
for i in "${env_vars[@]}"
do
   echo -e "$i=\c" >> .env.dev
   printenv $i >> .env.dev
done

# Deploying!
echo "Deploying!"
npx serverless deploy --stage prod 