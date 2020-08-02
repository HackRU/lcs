echo "Installing node and serverless.."
#Install npm
wget https://raw.githubusercontent.com/creationix/nvm/v0.31.0/nvm.sh -O ~/.nvm/nvm.sh;
source ~/.nvm/nvm.sh;
nvm install 7; # for Node v7
#Install serverless and created node modules
npm install
npm install -g serverless;
npm i -D serverless-dotenv-plugin;


