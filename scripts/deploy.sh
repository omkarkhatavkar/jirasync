#!/bin/bash

# This script is to be ansibilized
# run as root or with sudo

# call it from main directory
# ./scripts/deploy.sh
# or use `make deploy-service`

# create directories
mkdir -p /var/lib/jirasync
mkdir -p /etc/jirasync 

# copy config files
file="/etc/jirasync/config.yaml"
if [ ! -f "$file" ]
then
    cp config_sample.yaml /etc/jirasync/config.yaml
    echo "Please Edit /etc/jirasync/config.yaml"
fi

cp jirasync.service /lib/systemd/system/jirasync.service

# enable virtualenv
virtualenv -p python2.7 /var/lib/jirasync/env
# shellcheck disable=SC1091
source /var/lib/jirasync/env/bin/activate

# install everything
/var/lib/jirasync/env/bin/python setup.py install
/var/lib/jirasync/env/bin/pip install -r requirements.txt
/var/lib/jirasync/env/bin/pip install -r requirements-another.txt 

# test it
/var/lib/jirasync/env/bin/jirasync --help

# permissions
chmod 644 /lib/systemd/system/jirasync.service
chmod 744 /var/lib/jirasync/env/bin/jirasync
chmod +x /var/lib/jirasync/env/bin/jirasync

# Selinux must be disabled
sudo setenforce 0

# systemd
systemctl daemon-reload
systemctl enable jirasync.service
systemctl restart jirasync.service
systemctl status jirasync.service
