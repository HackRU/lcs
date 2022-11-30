# Credit to Kirollos and Anarav for work on Dockerfile
# Commands to build and run using this Dockerfile
# docker pull nikolaik/python-nodejs:python3.9-nodejs14
# docker build -t lcs .
# docker run -p 3000:3000 -p 3001:3001 -p 3002:3002 -it --name serverless lcs

# if you make changes do not hesistate to run docker rm serverless 
# followed by the docker build and docker run commands to test out your changes!

# Setup base image for python and nodejs
FROM nikolaik/python-nodejs:python3.9-nodejs16


# And our requirements, and install them
ADD requirements.txt /
RUN pip3 install -r requirements.txt

# Add package and package-lock to determine required dependencies
ADD package.json /

# Install the node packages outlined in package-lock.json (if present) or package.json
RUN npm install
RUN npm install -g serverless

# Add serverless.yml for lambda functions
ADD serverless.yml /

# Add all of our python files
ADD *.py /
ADD ./templates /templates
ADD ./src /src  

# Run serverless offline
EXPOSE 3000
ENTRYPOINT ["node_modules/.bin/sls", "offline", "--host", "0.0.0.0", "start"]
