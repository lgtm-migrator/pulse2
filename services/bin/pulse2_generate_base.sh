#!/bin/bash
#
# (c) siveo, http://siveo.net
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

nom_process=/usr/sbin/pulse2-create-base_wsusscn2.sh
lognom_process=/var/log/pulse2-create-base_wsusscn2.log
dd="$(date)"
if [ "$(ps ax | grep $nom_process | grep -v grep)" ]
then
    echo "$nom_process est deja lancé $dd"
    echo "$nom_process est lancé $dd"  >> lognom_process
else
    echo "lance programme $dd"
    echo "nohup $nom_process >> $lognom_process 2>&1 &"
    nohup $nom_process >> $lognom_process 2>&1 &
fi
echo "quit launcher"
