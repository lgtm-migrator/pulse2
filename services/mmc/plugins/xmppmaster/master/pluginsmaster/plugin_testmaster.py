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
# file pluginsmaster/plugin_testmaster.py

from mmc.plugins.xmppmaster.master.lib.utils import pluginmastersessionaction
import logging

plugin = {"VERSION": "1.0", "NAME": "testmaster", "TYPE": "master"}


@pluginmastersessionaction("actualise", 20)
def action(xmppobject, action, sessionid, data, message, ret, objsessiondata):
    logging.getLogger().debug(plugin)
    xmppobject.session.affiche()
    pass
