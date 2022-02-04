# -*- coding: utf-8; -*-
#
# (c) 2022 siveo, http://www.siveo.net
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

import logging
import base64
import json

from pulse2.version import getVersion, getRevision # pyflakes.ignore
from pulse2.database.urbackup import UrbackupDatabase

from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.urbackup.config import UrbackupConfig

from mmc.plugins.urbackup.urwrapper import UrApiWrapper

VERSION = "1.0.0"
APIVERSION = "1:0:0"


logger = logging.getLogger()


# PLUGIN GENERAL FUNCTIONS

def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = UrbackupConfig("urbackup")

    if config.disable:
        logger.warning("Plugin urbackup: disabled by configuration.")
        return False

    if not UrbackupDatabase().activate(config):
        logger.warning("Plugin urbackup: an error occurred during the database initialization")
        return False
    return True

def tests():
    return UrbackupDatabase().tests()

def login():
    """
        Create connection with urbackup

        Returns:
            session value
    """
    api = UrApiWrapper()
    logged = api.login()
    logged = api.response(logged)

    if "content" in logged and "session" in logged["content"]:
    	return logged["content"]["session"]

    return False

def get_ses():
    """
        Get value of session if logged

        Returns:
            session value
    """
    api = UrApiWrapper()
    session = api.get_session()

    if session == "":
        return "No DATA in session"

    return session

def get_logs():
    """
        Get logs of server

        Returns:
            Array of logs server
    """
    api = UrApiWrapper()
    _logs = api.get_logs()
    logs = api.response(_logs)
    if "content" in logs:
        return logs["content"]

    return "No DATA"

def get_settings_general():
    """
        Get multiples server setting global

        Returns:
            Array of server settings global
    """
    api = UrApiWrapper()
    settings = api.get_settings_general()
    settings = api.response(settings)
    if "content" in settings:
        return settings["content"]

    return "No DATA settings"

def get_settings_clientsettings(id_client):
    """
        Get multiples server setting global

        Returns:
            Array of server settings global
    """
    api = UrApiWrapper()
    settings = api.get_settings_clientsettings(id_client)
    settings = api.response(settings)
    if "content" in settings:
        return settings["content"]

    return "No DATA settings"

def get_settings_clients():
    """
        Get clients groups and user on urbackup

        Returns:
            Array of every client informations
    """
    api = UrApiWrapper()
    list_clients = api.get_settings_clients()
    list_clients = api.response(list_clients)
    if "content" in list_clients:
        return list_clients["content"]

    return "No DATA listusers"

def get_backups():
    """
        Get every backups for each client

        Returns:
            Array of every backup for each client
    """
    api = UrApiWrapper()
    backups = api.get_backups()
    backups = api.response(backups)
    if "content" in backups:
        return backups["content"]

    return "No DATA backups"

def get_status():
    """
        Get server and all client status

        Returns:
            Array of server and all client status
    """
    api = UrApiWrapper()
    status = api.get_status()
    status = api.response(status)
    if "content" in status:
        return status["content"]

    return "No DATA status"

def get_status_client(clientname):
    """
        Get status for one client

        Args:
            Clientname

        Returns:
            Array status for one client
    """
    api = UrApiWrapper()
    status = api.get_status()
    status = api.response(status)

    for client in status["status"]:
        if (client["name"] == clientname):
            return client

        return "No DATA client"
