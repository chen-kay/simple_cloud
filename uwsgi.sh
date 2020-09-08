#!/usr/bin/env bash

uwsgi --ini uwsgi.ini
python start.py >> logs/esl_status.log 2>&1 
