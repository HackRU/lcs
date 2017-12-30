source bin/activate
pip install -r requirements.txt
mkdir deploy/
cp lib/python3.6/site-packages/* deploy/
cp $1 deploy/
cp config.py deploy/
cd deploy/
zip dep.zip *
