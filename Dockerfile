# Commands to build and run using this Dockerfile
# docker build -t lcs .
# docker run -p 3000:3000 -p 3001:3001 -p 3002:3002 -it --name serverless lcs
# Set up the base image as ubuntu
FROM ubuntu:18.04
# And update it
RUN apt-get update 

# Install node js - we are installing node js 12 via the setup file
RUN apt-get install --yes curl
RUN curl --silent --location https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install --yes nodejs
RUN apt-get install --yes build-essential

# Pip for the python version
RUN apt-get install python3-pip --yes

# Recognize the python3 version we are using, we should be using 3.8
RUN python3 -V

# And our requirements, and install them
ADD requirements.txt /
RUN pip3 install -r requirements.txt

# Add package and package-lock to determine required dependencies
ADD package.json /
ADD package-lock.json /

# Install the node packages outlined in package-lock.json (if present) or package.json
RUN npm install
RUN npm install -g serverless

# Add serverless.yml for lambda functions
ADD serverless.yml /

# Add all of our python files
ADD *.py /
ADD ./src /src

# Run serverless offline
EXPOSE 3000
ENTRYPOINT ["node_modules/.bin/sls", "offline", "--host", "0.0.0.0", "start"]