#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2017 siveo, http://www.siveo.net
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
# file pluginsmaster/plugin_resultapplicationdeploymentjson.py


import json
import logging
import traceback
import sys
from pulse2.database.xmppmaster import XmppMasterDatabase

logger = logging.getLogger()

plugin = {"VERSION": "1.3", "NAME": "resultapplicationdeploymentjson", "TYPE": "master"}

def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    try:
        if ret == 0:
            logger.debug("Succes deploy on %s Package "\
                ": %s Session : %s" % (message['from'],
                                       data['descriptor']['info']['name'],
                                       sessionid))
            XmppMasterDatabase().delete_resources(sessionid)
        else:
            msg = "Deployment error on %s [Package "\
                ": %s / Session : %s]" % (message['from'],
                                       data['descriptor']['info']['name'],
                                       sessionid)
            logger.error(msg)

            if  'status' in data and data['status'] != "":
                XmppMasterDatabase().updatedeploystate(sessionid, data['status'])
            else:
                XmppMasterDatabase().updatedeploystate(sessionid, "ABORT PACKAGE EXECUTION ERROR")
            xmppobject.xmpplog(msg,
                        type='deploy',
                        sessionname=sessionid,
                        priority=-1,
                        action="xmpplog",
                        who="",
                        how="",
                        why=xmppobject.boundjid.bare,
                        module="Deployment | Start | Creation",
                        date=None,
                        fromuser="",
                        touser="")
    except:
        logger.error("%s"%(traceback.format_exc()))
