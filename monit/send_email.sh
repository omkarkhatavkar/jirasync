#!/usr/bin/env bash

subject="Alert: jirasync is restarted multiple times "
hostname=$(hostname)
body="jirasync is restarted multiple times on $hostname"
from="okhatavk@redhat.com"
to="okhatavk@redhat.com, brocha@redhat.com"
echo -e "Subject:${subject}\n${body}" | sendmail -f "${from}" -t "${to}"
