#! /bin/bash

# quick argument checks: 2 args at least.
if [ $# -lt 2 ]; then
    echo "USAGE: $0 <Stage> <Files...>"
    echo "Where stage means that a 'config.stage.py' exists."
    echo "And files is at least 1  python file to deploy."
    exit 1
fi

# make sure that the stage is a stage
if [[ ! -f "config.$1.py" ]]; then
    echo "Stage $1 not found. Make sure there is a config.$1.py"
    exit 1
fi

#make the python libraries ready
source venv/bin/activate
pip install -r requirements.txt

#make the deploy folder
mkdir deploy/

#copy the py libraries
if [ -d "venv/lib/python3.6" ]; then
    cp -r venv/lib/python3.6/site-packages/. deploy/
else
    cp -r venv/lib/python3.5/site-packages/* deploy/
fi

#record the stage
STAGE=$1
shift 1

#the rest of the args are files that we want to deploy.
for var in "$@"
do
	cp $var deploy/
done

#add the relevant config
cp "config.$STAGE.py" deploy/
mv "deploy/config.$STAGE.py" deploy/config.py

#zip the package
cd deploy/
zip -r dep.zip .

#move the zip up and clear the mess.
cd ..
cp deploy/dep.zip deploy-$STAGE-$@.zip
rm -rf deploy/
