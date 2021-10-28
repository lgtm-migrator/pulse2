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

import subprocess
import traceback

logger = logging.getLogger()


def simplecommand(cmd):
    obj = {}
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code'] = p.wait()
    obj['result'] = result
    return obj

def test_compte_ejabberd(compte):
    cmd_test_registerd_master ="ejabberdctl registered_users pulse | grep \"^%s$\""%compte
    logger.debug("test compte %s" %  compte)
    return simplecommand(cmd_test_registerd_master)

def ejabberdOnOff():
    cmd_ejabberd_service_start = "ps aux | grep ejabberd | grep -v grep"
    eeee = simplecommand(cmd_ejabberd_service_start)
    if not eeee['result']:
        logger.warning("service ejabberd is stop")
        return False
    else:
        return True

def enregister_compte(compte, domaine, password):
    cmd = "ejabberdctl register %s %s %s"%(compte, domaine, password)
    eeee = simplecommand(cmd)
    if eeee['code'] != 0:
        logger.error("register compte missing %s : (%s)" % (compte,
                                                            eeee['result']))
    else:
        logger.info("re register compte  %s" % (compte))

def creation_compte_master(compte, password):
    try:
        result = test_compte_ejabberd(compte)
        if result['code'] == 0 :
            logger.debug("compte %s existe" % compte)
            return
        else:
            # on verifie service ejabberd lancer
            if not ejabberdOnOff():
                logger.error("you must restart ejabberd")
                return
            else:
                logger.warning("registration compte missing %s" % compte)
                enregister_compte(compte, "pulse", password)
    except:
        logger.error("%s" % traceback.format_exc())

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
                time.sleep(1)
                logger.warning("reconection agent xmpp agent")
                logger.warning("reload configuration xmpp")
                creation_compte_master("master", tg.passwordconnection)


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
