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

from pulse2.version import getVersion, getRevision  # pyflakes.ignore
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
        logger.warning(
            "Plugin urbackup: an error occurred during the database initialization")
        return False
    return True


def tests():
    return UrbackupDatabase().tests()


def login():
    """
        Create a connection with urbackup.

        Returns:
           It returns a session value
           If it failed to connect it returns False.
    """
    api = UrApiWrapper()
    logged = api.login()
    logged = api.response(logged)

    if "content" in logged and "session" in logged["content"]:
    	return logged["content"]["session"]

    return False


def get_ses():
    """
        Get value of session

        Returns:
            Session key
    """
    api = UrApiWrapper()
    session = api.get_session()

    if session == "":
        return "No DATA in session"

    return session


def get_logs():
    """
        Get the logs of the server

        Returns:
            It returns the server logs.
            If no logs are available, it returns the "No DATA" string.
    """
    api = UrApiWrapper()
    _logs = api.get_logs()
    logs = api.response(_logs)
    if "content" in logs:
        return logs["content"]

    return "No DATA in logs"


def get_settings_general():
    """
        Get multiples settings value of server

        Returns:
            Array of every settings value of server
    """
    api = UrApiWrapper()
    settings = api.get_settings_general()
    settings = api.response(settings)
    if "content" in settings:
        return settings["content"]

    return "No DATA in global settings"


def get_settings_clientsettings(id_client):
    """
        Get multiples settings for one client

        Returns:
            Array of client settings
    """
    api = UrApiWrapper()
    settings = api.get_settings_clientsettings(id_client)
    settings = api.response(settings)
    if "content" in settings:
        return settings["content"]

    return "No DATA client settings"


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


def get_backups_all_client():
    """
        Get every backups for each client

        Returns:
            Array of every backup for each client
    """
    api = UrApiWrapper()
    backups = api.get_backups("0")
    backups = api.response(backups)
    if "content" in backups:
        return backups["content"]

    return "No DATA backups"

def get_backup_files(client_id, backup_id):
    """
        Get every files on backup

        Returns:
            Array of info from backup
    """
    api = UrApiWrapper()
    backup = api.get_backup_files(client_id, backup_id)
    backup = api.response(backup)
    if "content" in backup:
        return backup["content"]

    return "No DATA file on backup"

def get_backup_files_to_download(client_id, backup_id):
    """
        Get every files on backup

        Returns:
            Array of info from backup
    """
    api = UrApiWrapper()
    files = api.get_backup_files_to_download(client_id, backup_id)
    files = api.response(files)
    if "content" in files:
        return files["content"]

    return "No DATA file"


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


def get_progress():
    """
        Get progress for every backups

        Returns:
            Array of progress review for backups
    """
    api = UrApiWrapper()
    progress = api.get_progress()
    progress = api.response(progress)
    if "content" in progress:
        return progress["content"]

    return "No DATA progress"


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

def create_backup_incremental_file(client_id):
    """
    """
    api = UrApiWrapper()
    backup = api.create_backup("incr_file", client_id)
    backup = api.response(backup)

    if "content" in backup:
        return backup["content"]

    return "No DATA incremental backup file"

def create_backup_full_file(client_id):
    """
    """
    api = UrApiWrapper()
    backup = api.create_backup("full_file", client_id)
    backup = api.response(backup)

    if "content" in backup:
        return backup["content"]

    return "No DATA full backup file"

def create_backup_incremental_image(client_id):
    """
    """
    api = UrApiWrapper()
    backup = api.create_backup("incr_image", client_id)
    backup = api.response(backup)

    if "content" in backup:
        return backup["content"]

    return "No DATA incremental backup image"

def create_backup_full_image(client_id):
    """
    """
    api = UrApiWrapper()
    backup = api.create_backup("full_image", client_id)
    backup = api.response(backup)

    if "content" in backup:
        return backup["content"]

    return "No DATA full backup image"