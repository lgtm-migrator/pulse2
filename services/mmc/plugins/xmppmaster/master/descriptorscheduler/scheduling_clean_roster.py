# -*- coding: utf-8 -*-
#
# (c) 2016 siveo, http://www.siveo.net
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
"""

    this plugins nettoy les roters none none dans le roster.

    file : xmppmaster/master/descriptorscheduler/scheduling_clean_roster.py
    
    # Pour utiliser ce plugin, il faut que le substitut subscribe soit sur la meme machine que ejabberd.
    
    # dans 1 cas different il faudrat prevoir 1 iq vers l ars de son dpmaine pour executer ce plugin.
"""
import json
import logging
import sys
import traceback
from utils import simplecommand

plugin = {"VERSION" : "1.0", "NAME" : "scheduling_clean_roster",  "TYPE" : "all", "SCHEDULED" : True}

SCHEDULE = {"schedule" : "5 0 * * *", "nb" : -1}# nb  -1 infinie

def schedule_main(objectxmpp):
    logging.getLogger().debug("==============Plugin scheduled==============")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("============================================")
    try:
        result = simplecommand("ejabberdctl process_rosteritems delete none none any master@pulse" % objectxmpp.boundjid.bare)
        
        logging.getLogger().debug("cmd = ejabberdctl process_rosteritems delete none none any %s" % objectxmpp.boundjid.bare)
        logging.getLogger().debug("code return command = %s"% result['code'])
        #logging.getLogger().debug("code return command = %s"% json.dumps(result['result'], indent=4))
        logging.getLogger().debug("code return command = %s"% result['result'][0])
        
        logging.getLogger().debug("============================================")
    except Exception as e:
        logging.getLogger().error("%s" % traceback.format_exc())
