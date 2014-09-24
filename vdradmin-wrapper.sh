#!/bin/sh

VDR_USER=vdr
IPV6=no
VDRADMIND_OPTIONS=
[ -f /etc/sysconfig/vdr ] && . /etc/sysconfig/vdr
[ -f /etc/sysconfig/vdradmin ] && . /etc/sysconfig/vdradmin

chown -R $VDR_USER /var/lib/vdradmin /var/cache/vdradmin
OPTIONS="$VDRADMIND_OPTIONS"
[ -n "$IPV6" ] && [ "$IPV6" != "no" ] && OPTIONS="-6 $OPTIONS"
touch /var/run/vdradmind.pid
chown $VDR_USER /var/run/vdradmind.pid

su $VDR_USER -c "vdradmind $OPTIONS --nofork"
