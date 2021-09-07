#!/usr/bin/env python
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
# file /pulse_xmpp_master_substitute/lib/configuration.py
import sys
import os
import logging
import ConfigParser
from ConfigParser import  NoOptionError
import random

# Singleton/SingletonDecorator.py
class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance == None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


class confParameter:

    def __init__(self, namefileconfig):
        self.pathdirconffile =  os.path.dirname(os.path.realpath(namefileconfig))
        configobject = ConfigParser.ConfigParser()
        configobject.read(namefileconfig)
        if os.path.exists(namefileconfig + ".local"):
            configobject.read(namefileconfig + ".local")

        self.dbpoolrecycle = 3600
        self.dbpoolsize = 60
        self.charset = "utf8"
        if configobject.has_option("main", "dbpoolrecycle"):
            self.dbpoolrecycle = Config.getint('main', 'dbpoolrecycle')
        if configobject.has_option("main", "dbpoolsize"):
            self.dbpoolsize = Config.getint('main', 'dbpoolsize')
        if configobject.has_option("main", "charset"):
            self.charset = Config.get('main', 'charset')

        self.dbpooltimeout = 30
        if configobject.has_option("database", "dbpooltimeout"):
            self.dbpooltimeout = configobject.getint('database', 'dbpooltimeout')

        self.dbhost = "localhost"
        if configobject.has_option("database", "dbhost"):
            self.dbhost = configobject.get('database', 'dbhost')

        self.dbport = 3306
        if configobject.has_option("database", "dbport"):
            self.dbport = configobject.getint('database', 'dbport')

        self.dbname = "xmppmaster"
        if configobject.has_option("database", "dbname"):
            self.dbname = configobject.get('database', 'dbname')

        self.dbuser = "mmc"
        if configobject.has_option("database", "dbuser"):
            self.dbuser = configobject.get('database', 'dbuser')

        self.dbpasswd = "mmc"
        if configobject.has_option("database", "dbpasswd"):
            self.dbpasswd = configobject.get('database', 'dbpasswd')
