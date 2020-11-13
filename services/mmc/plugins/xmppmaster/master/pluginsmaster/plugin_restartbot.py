#!/usr/bin/python3
# -*- coding: utf-8; -*-
#
# (c) 2016-2018 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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
#
# file pluginsmaster/plugin_restartbot.py
# this plugin can be called from quick action

import json
import logging

logger = logging.getLogger()

plugin = {"VERSION": "1.1", "NAME": "restartbot", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("###################################################")
    logger.debug("call %s from %s"%(plugin,message['from']))
    logger.debug("###################################################")
    command = {'action': 'restartbot',
               'base64': False,
               'sessionid': sessionid,
               'data': ''}
    xmppobject.send_message(mto=data['data'][0],
                            mbody=json.dumps(command),
                            mtype='chat')
