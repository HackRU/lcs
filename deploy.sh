#! /bin/bash
source bin/activate
pip install -r requirements.txt
mkdir deploy/

if [ -d "lib/python3.6" ]; then
    cp -r lib/python3.6/site-packages/ deploy/
else
    cp -r lib/python3.5/site-packages/ deploy/
fi

cp $1 deploy/
cp config.py deploy/
cd deploy/
zip -r dep.zip *
cd ..
cp deploy/dep.zip .
rm -rf deploy/
