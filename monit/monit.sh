#!/usr/bin/env bash

yum -y install monit
systemctl enable monit
BASEDIR=$(dirname "$0")
cp $BASEDIR/send_email.sh /etc/jirasync
chmod +x /etc/jirasync/send_email.sh
cp $BASEDIR/jirasync_monit.conf /etc/monit.d/
systemctl restart monit
monit -t
