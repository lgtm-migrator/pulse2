# -*- coding: utf-8; -*-
#
# (c) 2020 siveo, http://www.siveo.net
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

# file : mmc/plugins/urbackup/config.py

from mmc.support.config import PluginConfig
from pulse2.database.urbackup.config import UrbackupDatabaseConfig

class UrbackupConfig(PluginConfig,UrbackupDatabaseConfig):
    def __init__(self, name = 'urbackup', conffile = None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            UrbackupDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)
        #self.confOption = "option1"
        # ...

    def readConf(self):
        PluginConfig.readConf(self)
        UrbackupDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")
        # ...
        self.urbackup_url = self.get("urbackup", "url")
        self.urbackup_username = self.get("urbackup", "username")
        self.urbackup_password = self.get("urbackup", "password")

    def check(self):
        #if not self.confOption: raise ConfigException("Conf error")
        pass

    @staticmethod
    def activate():
        # Get module config from "/etc/mmc/plugins/urbackup.ini"
        UrbackupConfig("urbackup")
        return True

