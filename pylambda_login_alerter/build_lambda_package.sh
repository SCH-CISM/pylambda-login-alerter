#!/bin/bash
rm -rf vendored
rm -rf ../login_alerter.zip
mkdir -p vendored
pip install -r requirements.txt -t ./vendored
zip -X -r ../login_alerter.zip login_alerter.py
cd vendored
zip -X -r ../../login_alerter.zip ./
cd -
