source bin/activate
pip install -r requirements.txt
mkdir deploy/
cp -r lib/python3.6/site-packages/ deploy/
cp $1 deploy/
cp config.py deploy/
cd deploy/
zip -r dep.zip *
cd ..
cp deploy/dep.zip .
rm -rf deploy/
