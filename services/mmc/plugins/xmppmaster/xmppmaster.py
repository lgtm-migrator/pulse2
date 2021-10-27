# -*- coding: utf-8; -*-
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

import threading
import time
import logging
from master.agentmaster import MUCBot

from mmc.plugins.xmppmaster.config import xmppMasterConfig
from mmc.agent import PluginManager

logger = logging.getLogger()


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class xmppMasterthread(threading.Thread):

    def __init__(self, args=(), kwargs=None):
        threading.Thread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.disable = xmppMasterConfig().disable
        self.xmpp = None
        self.reconnectxmpp = True

    def debugvariable(self, tg):
        choix={"NOTSET" : 0,
               "DEBUG" : 10,
               "INFO" : 20,
               "LOG" : 25,
               "DEBUGPULSE" : 25,
               "WARNING" : 30,
               "ERROR" : 40,
               "CRITICAL" : 50}
        if tg.debugmode in choix:
            return choix[tg.debugmode]
        else:
            return 0

    def doTask(self):
        tg = xmppMasterConfig()
        tg.debugmode = self.debugvariable(tg)


        #logging.log(tg.debugmode,"=======================================test log")
        self.xmpp = MUCBot(tg)
        self.xmpp.register_plugin('xep_0030')  # Service Discovery
        self.xmpp.register_plugin('xep_0045')  # Multi-User Chat
        self.xmpp.register_plugin('xep_0004')  # Data Forms
        self.xmpp.register_plugin('xep_0050')  # Adhoc Commands
        self.xmpp.register_plugin('xep_0199', {'keepalive': True,
                                               'frequency': 300,
                                               'interval': 300,
                                               'timeout': 200})
        self.xmpp.register_plugin('xep_0077')  # Registration
        # xmpp.register_plugin('xep_0047') # In-band Registration
        # xmpp.register_plugin('xep_0096') # file transfer
        # xmpp.register_plugin('xep_0095') # file transfer
        self.xmpp['xep_0077'].force_registration = False
        self.xmpp.register_plugin('xep_0279')
        logging.basicConfig(level=tg.debugmode,
                            format='[%(name)s.%(funcName)s:%(lineno)d] %(message)s')
        self.reconnectxmpp=True
        while self.reconnectxmpp:

            tg = xmppMasterConfig()
            tg.debugmode = self.debugvariable(tg)
            if tg.Server == "" or tg.Port == "":
                logger.error("Parameters connection server xmpp missing. (%s : %s)"%(tg.Server,
                                                                                     tg.Port))
                logger.error("reload config")
            #jfkjfk
            address=(tg.Server, tg.Port)
            if self.xmpp.connect(address=address):
                logger.info("Connection xmpp (%s %s)."%(tg.Server,
                                                        tg.Port))
                self.xmpp.process(block=True)
                logger.warning("deconection xmpp agent")
            else:
                logger.info("Unable to connect.")
                logger.warning("Parameters connection server xmpp error. (%s : %s)"%(tg.Server,
                                                                                     tg.Port))
                logger.warning("reload config")
            if self.reconnectxmpp:
                logger.warning("waitting 15 secondes before reconnection")
                time.sleep(15)
                logger.warning("reconection agent xmpp agent")
                logger.warning("reload configuration xmpp")


        if tg.Server == "" or tg.Port == "":
            logger.error("Parameters connection server xmpp missing.")
        if self.xmpp.connect(address=(tg.Server, tg.Port)):
            self.xmpp.process(block=True)
            logger.info("done")
        else:
            logger.info("Unable to connect.")

    # todo faire class
    def stopxmpp(self):
        if self.xmpp != None:
            # _remove_schedules
            self.xmpp.scheduler.quit()
            self.xmpp.session.sessionstop()
            time.sleep(2)
            #xmpp.scheduler.remove("manage session")
            self.reconnectxmpp = False
            self.xmpp.disconnect()

    def run(self):
        logger.info("Start XmppMaster")
        self.doTask()

    def stop(self):
        self.stopxmpp()
