# First get a semi recent node version for serverless

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
RUN apt install python3-pip --yes

# Recognize the python3 version we are using, we should be using 3.8
RUN python3 -V

# Add all of our python files
ADD *.py /

# And our requirements, and install them
ADD requirements.txt /
RUN pip3 install -r requirements.txt


# Now install the node dependencies for serverless
RUN npm install -g serverless

ADD package.json /
ADD package-lock.json /
ADD serverless.yml /

RUN npm install

RUN sls offline start

