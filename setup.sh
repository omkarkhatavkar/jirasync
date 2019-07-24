#!/bin/bash

virtualenv env
source env/bin/activate
pip install --editable .
pip install -r requirements.txt
pip install -r requirements-another.txt
eval "$(_JIRASYNC_COMPLETE=source jirasync)"
