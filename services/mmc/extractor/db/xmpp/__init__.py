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

# file : pulse_xmpp_master_substitute/lib/plugins/xmpp/__init__.py
"""
xmppmaster database handler
"""

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct, not_
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.exc import DBAPIError, NoSuchTableError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.automap import automap_base
from datetime import date, datetime, timedelta
import pprint
# Imported last
import logging
import json
from mmc.extractor.configuration import confParameter
import functools
from sqlalchemy.orm import scoped_session

logger = logging.getLogger()

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class DomaineTypeDeviceError(Error):
    """
        type is not in domaine 'thermalprinter', 'nfcReader', 'opticalReader',\
        'cpu', 'memory', 'storage', 'network'
    """

    def __str__(self):
        return "{0} {1}".format(self.__doc__, Exception.__str__(self))


class DomainestatusDeviceError(Error):
    """
        status is not in domaine 'ready', 'busy', 'warning', 'error'
    """

    def __str__(self):
        return "{0} {1}".format(self.__doc__, Exception.__str__(self))


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

    # Session decorator to create and close session automatically
    @classmethod
    def _sessionm(self, func):
        @functools.wraps(func)
        def __sessionm(self, *args, **kw):
            session_factory = sessionmaker(bind=self.engine)
            sessionmultithread = scoped_session(session_factory)
            result = func(self, sessionmultithread, *args, **kw)
            sessionmultithread.remove()
            return result
        return __sessionm

# TODO: Create a Singleton
class XmppMasterDatabase(DatabaseHelper):
    """
        Singleton Class to query the xmppmaster database.
    """
    is_activated = False

    def activate(self, configfile):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None
        # This is used to automatically create the mapping.
        Base = automap_base()

        self.logger.debug("Xmpp activation")
        self.engine = None

        self.config = confParameter(configfile)
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
            self.Sessionxmpp = sessionmaker(bind=self.engine)

            Base.prepare(self.engine, reflect=True)

            self.is_activated = True
            self.logger.debug("Xmpp activation done.")
            return True
        except Exception as e:
            print(e)
            self.logger.error("We failed to connect to the Xmpp database.")
            self.logger.error("Please verify your configuration")
            self.is_activated = False
            return False


    @DatabaseHelper._sessionm
    def get_deploy(self, session, week=1):
        if week <= 0:
            week = 1

        start_week = week
        end_week = week - 1

        sql = """SELECT
    SUBSTRING(xmppmaster.deploy.jidmachine,
        2,
        6) AS UCANSS,
    DATE_SUB(NOW(), INTERVAL %s WEEK) as from_date,
    DATE_SUB(NOW(), INTERVAL %s WEEK) as to_date,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'DEPLOYMENT SUCCESS') THEN 1
        ELSE 0
    END) AS `dep_sucess`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'DEPLOYMENT ERROR') THEN 1
        ELSE 0
    END) AS `dep_error`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'DEPLOYMENT ABORT') THEN 1
        ELSE 0
    END) AS `dep_abort`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'DEPLOYMENT ERROR ON TIMEOUT') THEN 1
        ELSE 0
    END) AS `dep_timeout`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'DEPLOYMENT PARTIAL SUCCESS') THEN 1
        ELSE 0
    END) AS `dep_part_sucess`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ERROR UNKNOWN ERROR') THEN 1
        ELSE 0
    END) AS `err_unknow`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT ON TIMEOUT') THEN 1
        ELSE 0
    END) AS `abt_timeout`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT DEPLOYMENT CANCELLED BY USER') THEN 1
        ELSE 0
    END) AS `abt_cancel`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT INCONSISTENT GLPI INFORMATION') THEN 1
        ELSE 0
    END) AS `abt_id_glpi`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT MISSING AGENT') THEN 1
        ELSE 0
    END) AS `abt_missing_agent`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ERROR TRANSFER FAILED') THEN 1
        ELSE 0
    END) AS `err_transfert`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT MACHINE DISAPPEARED') THEN 1
        ELSE 0
    END) AS `abt_mach_disp`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'WAITING MACHINE ONLINE') THEN 1
        ELSE 0
    END) AS `waiting_mach`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'WOL 1') THEN 1
        ELSE 0
    END) AS `wol1`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'WOL 2') THEN 1
        ELSE 0
    END) AS `wol2`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'WOL 3') THEN 1
        ELSE 0
    END) AS `wol3`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT PACKAGE IDENTIFIER MISSING') THEN 1
        ELSE 0
    END) AS `abt_missing_identifier`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT PACKAGE EXECUTION ERROR') THEN 1
        ELSE 0
    END) AS `abt_execution`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT TRANSFER FAILED') THEN 1
        ELSE 0
    END) AS `abt_transfert`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT PACKAGE EXECUTION CANCELLED') THEN 1
        ELSE 0
    END) AS `abt_exec_cancel`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT RELAY DOWN') THEN 1
        ELSE 0
    END) AS `abt_down_ars`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'DEPLOYMENT START') THEN 1
        ELSE 0
    END) AS `depl_start`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT INFO RELAY MISSING') THEN 1
        ELSE 0
    END) AS `abt_missing_ars`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'DEPLOYMENT DELAYED') THEN 1
        ELSE 0
    END) AS `depl_delayed`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT MISSING DEPENDENCY') THEN 1
        ELSE 0
    END) AS `abt_dep_missing`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'ABORT PACKAGE WORKFLOW ERROR') THEN 1
        ELSE 0
    END) AS `abt_workflow`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = 'DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)') THEN 1
        ELSE 0
    END) AS `depl_pending`,
    SUM(CASE
        WHEN (xmppmaster.deploy.state = xmppmaster.deploy.state) THEN 1
        ELSE 0
    END) AS `total`
FROM
    xmppmaster.deploy
WHERE
    xmppmaster.deploy.start BETWEEN DATE_SUB(NOW(), INTERVAL %s WEEK) AND date_sub(now(),INTERVAL %s WEEK)
GROUP BY UCANSS;
"""%(start_week, end_week, start_week, end_week)
        result = session.execute(sql)

        datas = []
        tmp = {}
        for key in result._metadata.keys:
            if key == "UCCANS":
                tmp[key] = ''
            elif key == "from_date":
                tmp[key] = datetime.today() - timedelta(weeks=start_week)
                tmp[key] = tmp[key].strftime("%Y-%m-%d %H:%M:%S")
            elif key == "to_date":
                tmp[key] = datetime.today() - timedelta(weeks=end_week)
                tmp[key] = tmp[key].strftime("%Y-%m-%d %H:%M:%S")

            else:
                tmp[key] = '0'


        for row in result:
            index = 0
            _tmp = dict(tmp)
            for key in result._metadata.keys:
                _tmp[key] = str(row[index])
                index += 1
            datas.append(_tmp)

        if len(datas) == 0:
            datas.append(tmp)

        return datas
