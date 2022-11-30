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
 "PRODUCTION_SLACK_API_TOKEN"
 "PRODUCTION_SLACK_CHANNEL_ID"
 "PRODUCTION_AWS_ACCESS_KEY_ID"
 "PRODUCTION_AWS_SECRET_ACCESS_KEY"
 "PRODUCTION_REGION_NAME"
 "PRODUCTION_RESUME_BUCKET"
 "PRODUCTION_WAIVER_BUCKET"
 "PRODUCTION_VACCINE_BUCKET"
 "PRODUCTION_START_YEAR"  
 "PRODUCTION_START_MONTH" 
 "PRODUCTION_START_DAY"  
 "PRODUCTION_END_YEAR"  
 "PRODUCTION_END_MONTH" 
 "PRODUCTION_END_DAY" 
 "PRODUCTION_END_HOUR" 
 "PRODUCTION_DAY_OF_START_YEAR" 
 "PRODUCTION_DAY_OF_START_MONTH" 
 "PRODUCTION_DAY_OF_START_DAY"     
 "PRODUCTION_DAY_OF_START_HOUR"
 "PRODUCTION_DAY_OF_END_YEAR"  
 "PRODUCTION_DAY_OF_END_MONTH"
 "PRODUCTION_DAY_OF_END_DAY"  
 "PRODUCTION_DAY_OF_END_HOUR"
 "PRODUCTION_EMAIL_ADDRESS"
 "PRODUCTION_EMAIL_PASSWORD")
 
echo "For loop"
# Disabled environment variables
# "PRODUCTION_MAX_REIMBURSE"
# "PRODUCTION_TRAIN_REIMBURSE"
# "PRODUCTION_TRAVEL_BUDGET"
# "PRODUCTION_CAR_REIMBURSE"
# "PRODUCTION_BUS_REIMBURSE"
# "PRODUCTION_PLANE_REIMBURSE"

## now loop through the above env_vars
for i in "${env_vars[@]}"
do
   echo -e "$i=\c" >> .env.prod
   printenv $i >> .env.prod
done

wget https://raw.githubusercontent.com/creationix/nvm/v0.31.0/nvm.sh -O ~/.nvm/nvm.sh;
source ~/.nvm/nvm.sh;

nvm use 14

##Checking Package Versions
echo "Checking Node..."
node -v


# Deploying!
echo "Deploying!"
npx serverless deploy --stage prod 
