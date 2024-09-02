#!/bin/bash


rm -f ai_agents.zip
rm -rf package
pipenv requirements > requirements.txt
python3 -m pip install -r requirements.txt -t ./package

(cd package; zip -r9 ../ai_agents.zip .)

zip -r9 ai_agents.zip tools/

aws s3 cp ai_agents.zip s3://chelma-lp01-us-west-2/ai_agents.zip --region us-west-2
