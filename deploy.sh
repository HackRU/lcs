#! /bin/bash
source venv/bin/activate
pip install -r requirements.txt
mkdir deploy/

if [ -d "venv/lib/python3.6" ]; then
    cp -r venv/lib/python3.6/site-packages/* deploy/
else
    cp -r venv/lib/python3.5/site-packages/* deploy/
fi

for var in "$@"
do
	cp $var deploy/
done
cp config.py deploy/
cd deploy/
zip -r dep.zip *
cd ..
cp deploy/dep.zip .
rm -rf deploy/
