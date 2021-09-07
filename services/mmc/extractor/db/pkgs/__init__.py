# -*- coding: utf-8; -*-
#
# (c) 2021 siveo, http://www.siveo.net/
#
#
# This file is part of Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# file : mmc/extractor/db/xmpp/__init__.py

"""pkgs database handler"""

# standard modules
import time
import traceback
import os
# SqlAlchemy
from sqlalchemy import and_, create_engine, MetaData, Table, Column, String, \
                       Integer, ForeignKey, select, asc, or_, desc, func, not_, distinct
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import NoSuchTableError, TimeoutError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.automap import automap_base
import datetime
from mmc.extractor.configuration import confParameter
# Imported last
import logging
import functools

logger = logging.getLogger()
NB_DB_CONN_TRY = 2


class Singleton(object):

    def __new__(type, *args):
        if '_the_instance' not in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance



class DatabaseHelper(Singleton):
    # Session decorator to create and close session automatically
    @classmethod
    def _sessionm(self, func1):
        @functools.wraps(func1)
        def __sessionm(self, *args, **kw):
            session_factory  = sessionmaker(bind=self.engine)
            sessionmultithread = scoped_session(session_factory)
            result = func1(self, sessionmultithread , *args, **kw)
            sessionmultithread.remove()
            return result
        return __sessionm

# TODO need to check for useless function (there should be many unused one...)

class PkgsDatabase(DatabaseHelper):
    """
    Singleton Class to query the pkgs database.

    """
    is_activated = False

    def activate(self, configfile):
        self.logger = logging.getLogger()
        Base = automap_base()
        if self.is_activated:
            return None
        self.logger.info("Pkgs database is connecting")
        self.config = confParameter(configfile)

        self.session = None
        try:
            self.engine = create_engine('mysql://%s:%s@%s:%s/%s?charset=%s' % (self.config.dbuser,
                                                                             self.config.dbpasswd,
                                                                             self.config.dbhost,
                                                                             self.config.dbport,
                                                                             self.config.dbname,
                                                                             self.config.charset),
                                         pool_recycle=self.config.dbpoolrecycle,
                                         pool_size=self.config.dbpoolsize,
                                         pool_timeout=self.config.dbpooltimeout,
                                         convert_unicode=True)

            Base.prepare(self.engine, reflect=True)

            # Example of mapping declaration
            #try:
            #    self.Dependencies = Base.classes.dependencies
            #except:
            #    logger.error("Mapping dependencies table")


            self.session = create_session(bind=self.engine)
            if self.session is not None:
                self.is_activated = True
                self.logger.debug("Pkgs database connected")
                return True

            self.logger.error("Pkgs database connecting")
            return False
        except Exception as e:
            self.logger.error("We failed to connect to the Pkgs database.")
            self.logger.error("Please verify your configuration")
            self.is_activated = False
            return False

    ####################################

    # Here define the function to get datas from pkgs database
