# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
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

# file : /database/xmppmaster/__init__.py

"""
xmppmaster database handler
"""

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, func, and_, desc, or_,\
                        distinct, not_  # cast, Date, select,
from sqlalchemy.orm import sessionmaker

from sqlalchemy.exc import DBAPIError
from datetime import datetime, timedelta  # date,
# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.xmppmaster.schema import Network, Machines,\
    RelayServer, Users, Has_machinesusers, \
    Has_relayserverrules, Regles, Has_guacamole, UserLog, Deploy,\
    Has_login_command, Logs, \
    Organization, Packages_list, Qa_custom_command, Qa_relay_command,\
    Qa_relay_launched, Qa_relay_result,\
    Cluster_ars,\
    Has_cluster_ars,\
    Command_action,\
    Command_qa,\
    Syncthingsync,\
    Organization_ad,\
    Cluster_resources,\
    Syncthing_ars_cluster,\
    Syncthing_machine,\
    Syncthing_deploy_group,\
    Substituteconf,\
    Agentsubscription,\
    Subscription,\
    Def_remote_deploy_status,\
    Uptime_machine, \
    Mon_machine, \
    Mon_devices, \
    Mon_device_service, \
    Mon_rules, \
    Mon_event , \
    Mon_panels_template, \
    Glpi_entity, \
    Glpi_location, \
    Glpi_Register_Keys
# Imported last
import logging
import json
import time
# topology
import os
import pwd
import traceback
import sys
import re
import uuid
import random
import copy

Session = sessionmaker()

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


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError("Unknown type")


class XmppMasterDatabase(DatabaseHelper):
    """
    Singleton Class to query the xmppmaster database.

    """
    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "xmppmaster"
        self.configfile = "xmppmaster.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None
        self.config = config
        self.db = create_engine(self.makeConnectionPath(),
                                pool_recycle=self.config.dbpoolrecycle,
                                pool_size=self.config.dbpoolsize,
                                pool_timeout=self.config.dbpooltimeout)
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM xmppmaster.version limit 1;")
        re = [x.Number for x in result]
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the xmppmaster database
        """
        # No mapping is needed, all is done on schema file
        return

    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError as e:
                logging.getLogger().error(e)
            except Exception as e:
                logging.getLogger().error(e)
            if ret:
                break
        if not ret:
            raise "Database connection error"
        return ret

    # =====================================================================
    # xmppmaster FUNCTIONS deploy syncthing
    # =====================================================================

    # xmppmaster FUNCTIONS FOR SUBSCRIPTION

    @DatabaseHelper._sessionm
    def setagentsubscription(self,
                             session,
                             name):
        """
            this functions addition a log line in table log xmpp.
        """
        try:
            new_agentsubscription = Agentsubscription()
            new_agentsubscription.name = name
            session.add(new_agentsubscription)
            session.commit()
            session.flush()
            return new_agentsubscription.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def deAgentsubscription(self,
                            session,
                            name):
        """
            del organization name
        """
        session.query(Agentsubscription).\
            filter(Agentsubscription.name == name).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def setupagentsubscription(self,
                               session,
                               name):
        """
            this functions addition ou update table in table log xmpp.
        """
        try:
            q = session.query(Agentsubscription)
            q = q.filter(Agentsubscription.name == name)
            record = q.first()
            if record:
                record.name = name
                session.commit()
                session.flush()
                return record.id
            else:
                return self.setagentsubscription(name)
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def setSubscription(self,
                        session,
                        macadress,
                        idagentsubscription):
        """
            this functions addition a log line in table log xmpp.
        """
        try:
            new_subscription = Subscription()
            new_subscription.macadress = macadress
            new_subscription.idagentsubscription = idagentsubscription
            session.add(new_subscription)
            session.commit()
            session.flush()
            return new_subscription.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def setupSubscription(self,
                          session,
                          macadress,
                          idagentsubscription):
        """
            this functions addition a log line in table log xmpp.
        """
        try:
            q = session.query(Subscription)
            q = q.filter(Subscription.macadress == macadress)
            record = q.first()
            if record:
                record.macadress = macadress
                record.idagentsubscription = idagentsubscription
                session.commit()
                session.flush()
                return record.id
            else:
                return self.setSubscription(macadress, idagentsubscription)
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def setuplistSubscription(self,
                              session,
                              listmacadress,
                              agentsubscription):
        try:
            id = self.setupagentsubscription(agentsubscription)
            if id is not None:
                for macadress in listmacadress:
                    self.setupSubscription(macadress, id)
                return id
            else:
                logger.error("setup or create record for"
                             " agent subscription %s" % agentsubscription)
                return None
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def delSubscriptionmacadress(self,
                                 session,
                                 macadress):
        """
            this functions addition a log line in table log xmpp.
        """
        try:
            q = session.query(Subscription)
            q = q.filter(Subscription.macadress == macadress).delete()
            session.commit()
            session.flush()
        except Exception as e:
            logging.getLogger().error(str(e))
            self.logger.error("\n%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def update_enable_for_agent_subscription(self,
                                             session,
                                             agentsubtitutename,
                                             status='0',
                                             agenttype='machine'):
        try:
            sql = """
            UPDATE `xmppmaster`.`machines`
                    INNER JOIN
                `xmppmaster`.`subscription` ON `xmppmaster`.`machines`.`macaddress` = `xmppmaster`.`subscription`.`macadress`
                    INNER JOIN
                `xmppmaster`.`agent_subscription` ON `xmppmaster`.`subscription`.`idagentsubscription` = `xmppmaster`.`agent_subscription`.`id`
            SET
                `xmppmaster`.`machines`.`enabled` = '%s'
            WHERE
                `xmppmaster`.`machines`.agenttype = '%s'
                    AND `xmppmaster`.`agent_subscription`.`name` = '%s';""" \
                        % (status, agenttype, agentsubtitutename)
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception:
            self.logger.error("\n%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def setSyncthing_deploy_group(self,
                                  session,
                                  namepartage,
                                  directory_tmp,
                                  packagename,
                                  cmd,
                                  grp_parent,
                                  status="C",
                                  dateend=None,
                                  deltatime=60):
        try:
            idpartage = self.search_partage_for_package(packagename)
            if idpartage == -1:
                #print "add partage"
                #il faut cree le partage.
                new_Syncthing_deploy_group = Syncthing_deploy_group()
                new_Syncthing_deploy_group.namepartage = namepartage
                new_Syncthing_deploy_group.directory_tmp = directory_tmp
                new_Syncthing_deploy_group.cmd = cmd
                new_Syncthing_deploy_group.status = status
                new_Syncthing_deploy_group.package = packagename
                new_Syncthing_deploy_group.grp_parent = grp_parent
                if dateend is None:
                    dateend = datetime.now() + timedelta(minutes=deltatime)
                else:
                    new_Syncthing_deploy_group.dateend =  dateend + timedelta(minutes=deltatime)
                session.add(new_Syncthing_deploy_group)
                session.commit()
                session.flush()
                return new_Syncthing_deploy_group.id
            else:
                return idpartage
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def incr_count_transfert_terminate(self,
                                       session,
                                       iddeploy):
        sql = """UPDATE xmppmaster.syncthing_deploy_group
                SET
                    nbtransfert = nbtransfert + 1
                WHERE
                    id = %s;""" % (iddeploy)
        #print "incr_count_transfert_terminate", sql
        result = session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def update_transfert_progress(self,
                                      session,
                                      progress,
                                      iddeploy,
                                      jidmachine):
        """ this function update this level progress"""
        sql="""
                UPDATE xmppmaster.syncthing_machine
                        INNER JOIN
                    syncthing_ars_cluster
                      ON xmppmaster.syncthing_ars_cluster.id =
                             xmppmaster.syncthing_machine.fk_arscluster
                        INNER JOIN
                    xmppmaster.syncthing_deploy_group
                      ON xmppmaster.syncthing_deploy_group.id =
                      xmppmaster.syncthing_ars_cluster.fk_deploy
                SET
                    xmppmaster.syncthing_machine.progress = IF(%s>=xmppmaster.syncthing_machine.progress,%s,xmppmaster.syncthing_machine.progress)
                WHERE
                    xmppmaster.syncthing_deploy_group.id = %s
                        AND xmppmaster.syncthing_machine.jidmachine LIKE '%s';""" % (progress,
                                                                                   progress,
                                                                                   iddeploy,
                                                                                   jidmachine)
        #print "update_transfert_progress", sql
        result = session.execute(sql)
        session.commit()
        session.flush()


    @DatabaseHelper._sessionm
    def get_ars_for_pausing_syncthing(self,
                                      session,
                                      nbtransfert = 2):
        sql = """SELECT
                    xmppmaster.syncthing_deploy_group.id,
                    xmppmaster.syncthing_ars_cluster.liststrcluster,
                    xmppmaster.syncthing_deploy_group.directory_tmp,
                    xmppmaster.syncthing_deploy_group.nbtransfert,
                    xmppmaster.syncthing_ars_cluster.id
                FROM
                    xmppmaster.syncthing_deploy_group
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster
                      ON
                         xmppmaster.syncthing_deploy_group.id =
                         xmppmaster.syncthing_ars_cluster.fk_deploy
                WHERE
                    xmppmaster.syncthing_deploy_group.nbtransfert >= %s
                    and
                    xmppmaster.syncthing_ars_cluster.keypartage != "pausing";""" % (nbtransfert)
        #print "get_ars_for_pausing_syncthing"#, sql
        result = session.execute(sql)
        session.commit()
        session.flush()
        if result is None:
            return -1
        else:
            re =  [y for y in [x for x in result]]
            for arssyncthing in re:
                self.update_ars_status(arssyncthing[4], "pausing")
        return re

    @DatabaseHelper._sessionm
    def update_ars_status( self,
                           session,
                           idars,
                           keystatus="pausing"):
        sql = """UPDATE
                    xmppmaster.syncthing_ars_cluster
                SET
                    xmppmaster.syncthing_ars_cluster.keypartage = '%s'
                WHERE
                    xmppmaster.syncthing_ars_cluster.id = '%s';""" % (keystatus, idars)
        #print "update_ars_status", sql
        result = session.execute(sql)
        session.commit()
        session.flush()


    @DatabaseHelper._sessionm
    def search_partage_for_package( self,
                                    session,
                                    packagename):
        result = -1
        sql=""" SELECT
                    xmppmaster.syncthing_deploy_group.id
                FROM
                    xmppmaster.syncthing_deploy_group
                WHERE
                    xmppmaster.syncthing_deploy_group.package LIKE '%s'
                        AND xmppmaster.syncthing_deploy_group.dateend > DATE_SUB(NOW(), INTERVAL 1 HOUR)
                limit 1;""" % (packagename)
        result = session.execute(sql)
        session.commit()
        session.flush()
        resultat =  [x for x in result]
        if not resultat:
            return -1
        else:
            return resultat[0][0]

    @DatabaseHelper._sessionm
    def search_ars_cluster_for_package( self,
                                    session,
                                    idpartage,
                                    ars):
        result = -1
        sql="""SELECT
                xmppmaster.syncthing_ars_cluster.id
                FROM
                    xmppmaster.syncthing_ars_cluster
                where xmppmaster.syncthing_ars_cluster.fk_deploy = %s and
                xmppmaster.syncthing_ars_cluster.liststrcluster like '%s'
                LIMIT 1;""" % (idpartage, ars)
        result = session.execute(sql)
        session.commit()
        session.flush()
        resultat =  [x for x in result]
        if len(resultat) == 0:
            return -1
        else:
            return resultat[0][0]

    @DatabaseHelper._sessionm
    def search_ars_master_cluster_( self,
                                    session,
                                    idpartage,
                                    numcluster):
        result = -1
        sql="""SELECT DISTINCT xmppmaster.syncthing_ars_cluster.arsmastercluster
                FROM
                    xmppmaster.syncthing_ars_cluster
                where
                    xmppmaster.syncthing_ars_cluster.fk_deploy = %s
                      and
                    xmppmaster.syncthing_ars_cluster.numcluster = %s limit 1;""" % (idpartage, numcluster)
        result = session.execute(sql)
        session.commit()
        session.flush()
        resultat =  [x for x in result]
        countresult = len(resultat)

        if countresult == 0:
            return ""
        elif countresult == 1:
            return resultat[0][0]
        else:
            #il y a plusieurs cluster dans le deployement.
            #il faut donc choisir celui correspondant au cluster
            ljidars = [x[0] for x in resultat]
            for jidars in ljidars:
                #print jidars
                if self.ars_in_num_cluster(jidars, numcluster):
                    return jidars
        return ""

    @DatabaseHelper._sessionm
    def ars_in_num_cluster(self,
                           session,
                           jidars,
                           numcluster):
        """
            test si jidars est dans le cluster number.
        """
        sql="""SELECT
                    id_ars
                FROM
                    xmppmaster.has_cluster_ars
                INNER JOIN
                    xmppmaster.relayserver
                        ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                where xmppmaster.relayserver.jid like '%s'
                  and
                  xmppmaster.has_cluster_ars.id_cluster= %s;""" % (jidars,
                                                                 numcluster )
        #print sql

        result = session.execute(sql)
        session.commit()
        session.flush()
        resultat =  [x for x in result]
        if resultat:
            return True
        else:
            return False

    @DatabaseHelper._sessionm
    def setSyncthing_ars_cluster(self,
                                 session,
                                 numcluster,
                                 namecluster,
                                 liststrcluster,
                                 arsmastercluster,
                                 fk_deploy,
                                 type_partage= "",
                                 devivesyncthing = "",
                                 keypartage=''):
        try:
            #search ars elu if exist for partage
            arsmasterclusterexist = self.search_ars_master_cluster_(fk_deploy,
                                                                    numcluster)
            ars_cluster_id = self.search_ars_cluster_for_package(fk_deploy,
                                                                 liststrcluster)
            if ars_cluster_id == -1:
                new_Syncthing_ars_cluster = Syncthing_ars_cluster()
                new_Syncthing_ars_cluster.numcluster = numcluster
                new_Syncthing_ars_cluster.namecluster = namecluster
                new_Syncthing_ars_cluster.liststrcluster = liststrcluster
                if arsmasterclusterexist == "":
                    new_Syncthing_ars_cluster.arsmastercluster = arsmastercluster
                else:
                    new_Syncthing_ars_cluster.arsmastercluster = arsmasterclusterexist
                new_Syncthing_ars_cluster.keypartage =  keypartage
                new_Syncthing_ars_cluster.fk_deploy = fk_deploy
                new_Syncthing_ars_cluster.type_partage =  type_partage
                new_Syncthing_ars_cluster.devivesyncthing = devivesyncthing
                session.add(new_Syncthing_ars_cluster)
                session.commit()
                session.flush()
                return new_Syncthing_ars_cluster.id
            else:
                return ars_cluster_id
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def setSyncthing_machine(self,
                             session,
                             jidmachine,
                             jid_relay,
                             cluster,
                             pathpackage,
                             sessionid,
                             start,
                             startcmd,
                             endcmd,
                             command,
                             group_uuid,
                             result,
                             fk_arscluster,
                             syncthing = 1,
                             state ="",
                             user ="",
                             type_partage= "",
                             title="",
                             inventoryuuid=None,
                             login=None,
                             macadress=None,
                             comment = ""):
        try:
            new_Syncthing_machine = Syncthing_machine()
            new_Syncthing_machine.jidmachine = jidmachine
            new_Syncthing_machine.cluster = cluster
            new_Syncthing_machine.jid_relay = jid_relay
            new_Syncthing_machine.pathpackage = pathpackage
            new_Syncthing_machine.state = state
            new_Syncthing_machine.sessionid = sessionid
            new_Syncthing_machine.start = start
            new_Syncthing_machine.startcmd = startcmd
            new_Syncthing_machine.endcmd = endcmd
            new_Syncthing_machine.user = user
            new_Syncthing_machine.command = command
            new_Syncthing_machine.group_uuid = group_uuid
            new_Syncthing_machine.result = result
            new_Syncthing_machine.syncthing = syncthing
            new_Syncthing_machine.type_partage = type_partage
            new_Syncthing_machine.title = title
            new_Syncthing_machine.inventoryuuid = inventoryuuid
            new_Syncthing_machine.login = login
            new_Syncthing_machine.macadress = macadress
            new_Syncthing_machine.comment = comment
            new_Syncthing_machine.fk_arscluster = fk_arscluster
            session.add(new_Syncthing_machine)
            session.commit()
            session.flush()
            return new_Syncthing_machine.id
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def stat_syncthing_distributon(self,
                                   session,
                                   idgrp,
                                   idcmd,
                                   valuecount= [0,100]):
        setvalues =" "
        if valuecount:
            setvalues = "AND xmppmaster.syncthing_machine.progress in (%s)" % ",".join([str(x) for x in valuecount])
        sql = """SELECT DISTINCT progress, COUNT(progress)
                    FROM
                        xmppmaster.syncthing_machine
                    WHERE
                        xmppmaster.syncthing_machine.group_uuid = %s
                        AND xmppmaster.syncthing_machine.command = %s
                        """ % (idgrp, idcmd)
        sql = sql + setvalues + "\nGROUP BY progress ;"

        #print sql
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [(x[0],x[1]) for x in result]

    @DatabaseHelper._sessionm
    def stat_syncthing_transfert(self,
                                 session,
                                 idgrp,
                                 idcmd):

        ddistribution = self.stat_syncthing_distributon(idgrp, idcmd)
        distibution = {'nbvalue': len(ddistribution), "data_dist": ddistribution}

        sql = """SELECT
                    pathpackage,
                    COUNT(*) AS nb,
                    CAST((SUM(xmppmaster.syncthing_machine.progress) / COUNT(*)) AS CHAR) AS progress
                FROM
                    xmppmaster.syncthing_machine
                WHERE
                    xmppmaster.syncthing_machine.group_uuid = %s
                        AND xmppmaster.syncthing_machine.command = %s;
                        """ % (idgrp, idcmd)
        result = session.execute(sql)
        session.commit()
        session.flush()
        re = [x for x in result]
        re = re[0]
        if re[0] is None:
            return {'package': "",
                    'nbmachine': 0,
                    'progresstransfert': 0,
                    'distibution': distibution
                    }
        try:
            progress = int(float(re[2]))
        except:
            progress = 0

        return { 'package': re[0],
                 'nbmachine': re[1],
                 'progresstransfert': progress ,
                 'distibution': distibution}

    @DatabaseHelper._sessionm
    def getnumcluster_for_ars(self,
                            session,
                            jidrelay):
        sql = """SELECT
                    xmppmaster.has_cluster_ars.id_cluster
                FROM
                    xmppmaster.relayserver
                        INNER JOIN
                    xmppmaster.has_cluster_ars
                      ON `has_cluster_ars`.`id_ars` = xmppmaster.relayserver.id
                WHERE
                    `relayserver`.`jid` LIKE '%s'
                LIMIT 1;""" % jidrelay
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result][0]

    @DatabaseHelper._sessionm
    def getCluster_deploy_syncthing(self,
                                    session,
                                    iddeploy):
        sql = """SELECT
                    xmppmaster.syncthing_deploy_group.namepartage,
                    xmppmaster.syncthing_deploy_group.directory_tmp,
                    xmppmaster.syncthing_deploy_group.package,
                    xmppmaster.syncthing_ars_cluster.namecluster,
                    xmppmaster.syncthing_ars_cluster.arsmastercluster,
                    xmppmaster.syncthing_ars_cluster.numcluster,
                    xmppmaster.syncthing_machine.cluster,
                    xmppmaster.syncthing_deploy_group.grp_parent,
                    xmppmaster.syncthing_deploy_group.cmd,
                    xmppmaster.syncthing_deploy_group.id
                FROM
                    xmppmaster.syncthing_deploy_group
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster ON xmppmaster.syncthing_deploy_group.id = xmppmaster.syncthing_ars_cluster.fk_deploy
                        INNER JOIN
                    xmppmaster.syncthing_machine ON xmppmaster.syncthing_ars_cluster.id = xmppmaster.syncthing_machine.fk_arscluster
                WHERE
                    xmppmaster.syncthing_deploy_group.id = %s ;""" % iddeploy
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [y for y in [x for x in result]]

    @DatabaseHelper._sessionm
    def updateMachine_deploy_Syncthing(self,
                                    session,
                                    listidmachine,
                                    statusold=2,
                                    statusnew=3):
        if isinstance(listidmachine, (int,str)):
            listidmachine = [listidmachine]
        if not listidmachine:
            return
        listidmachine = ",".join([ str(x) for x in listidmachine])

        sql = """UPDATE
                    xmppmaster.syncthing_machine
                SET
                    xmppmaster.syncthing_machine.syncthing = %s
                where
                    syncthing = %s
                    and
                    id in (%s);""" % (statusnew, statusold, listidmachine)
        #print sql
        result = session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def getMachine_deploy_Syncthing(self,
                                    session,
                                    iddeploy,
                                    ars = None,
                                    status = None):
        sql = """SELECT
                    xmppmaster.syncthing_machine.sessionid,
                    xmppmaster.syncthing_machine.jid_relay,
                    xmppmaster.syncthing_machine.jidmachine,
                    xmppmaster.machines.keysyncthing,
                    xmppmaster.syncthing_machine.result,
                    xmppmaster.syncthing_machine.id
                FROM
                    xmppmaster.syncthing_deploy_group
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster
                            ON xmppmaster.syncthing_deploy_group.id =
                                xmppmaster.syncthing_ars_cluster.fk_deploy
                        INNER JOIN
                    xmppmaster.syncthing_machine
                            ON xmppmaster.syncthing_ars_cluster.id =
                                xmppmaster.syncthing_machine.fk_arscluster
                        INNER JOIN
                    xmppmaster.machines
                            ON xmppmaster.machines.uuid_inventorymachine =
                                xmppmaster.syncthing_machine.inventoryuuid
                WHERE
                    xmppmaster.syncthing_deploy_group.id=%s """ % iddeploy
        if ars is not None:
            sql = sql + """
            and
            xmppmaster.syncthing_machine.jid_relay like '%s' """ % ars
        if status is not None:
            sql = sql + """
            and
            xmppmaster.syncthing_machine.syncthing = %s """ % status
        sql = sql +";"
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    # =====================================================================
    # xmppmaster FUNCTIONS synch syncthing
    # =====================================================================
    @DatabaseHelper._sessionm
    def setSyncthingsync( self, session, uuidpackage, relayserver_jid,
                          typesynchro = "create", watching = 'yes'):
        try:
            new_Syncthingsync = Syncthingsync()
            new_Syncthingsync.uuidpackage = uuidpackage
            new_Syncthingsync.typesynchro =  typesynchro
            new_Syncthingsync.relayserver_jid = relayserver_jid
            new_Syncthingsync.watching =  watching
            session.add(new_Syncthingsync)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def get_List_jid_ServerRelay_enable(self, session, enabled=1):
        """ return list enable server relay id """
        sql = """SELECT
                    jid
                FROM
                    xmppmaster.relayserver
                WHERE
                        `relayserver`.`enabled` = %d;""" % (enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def getRelayServerfromid(self, session, ids):
        """
            This function is used to obtain the relayservers infos
            based on the ids
            Args:
                session: The SQLAlchemy session
                ids: ids of the relayservers
            Returns:
                It returns the complete infos of the relayservers
        """
        relayserver_list = []
        if isinstance(ids, basestring):
            ids = ids.split(',')
        elif isinstance(ids, int):
            ids = [ids]

        try:
            relayservers = session.query(RelayServer).filter(RelayServer.id.in_(ids))
            relayservers = relayservers.all()
            session.commit()
            session.flush()
            for relayserver in relayservers:
                res = {'id': relayserver.id,
                       'urlguacamole': relayserver.urlguacamole,
                       'subnet': relayserver.subnet,
                       'nameserver' : relayserver.nameserver,
                       'ipserver': relayserver.ipserver,
                       'ipconnection' : relayserver.ipconnection,
                       'port': relayserver.port,
                       'portconnection': relayserver.portconnection,
                       'mask': relayserver.mask,
                       'jid': relayserver.jid,
                       'longitude': relayserver.longitude,
                       'latitude': relayserver.latitude,
                       'enabled': relayserver.enabled,
                       'switchonoff': relayserver.switchonoff,
                       'mandatory': relayserver.mandatory,
                       'classutil': relayserver.classutil,
                       'groupdeploy': relayserver.groupdeploy,
                       'package_server_ip': relayserver.package_server_ip,
                       'package_server_port': relayserver.package_server_port,
                       'moderelayserver': relayserver.moderelayserver
                    }
                relayserver_list.append(res)
            return relayserver_list
        except Exception, e:
            logging.getLogger().error(str(e))
            traceback.print_exc(file=sys.stdout)
            return relayserver_list

    @DatabaseHelper._sessionm
    def get_Arsid_list_from_clusterid_list(self,
                                           session,
                                           idscluster):
        """
            This function returns the list of the ars from a cluster id or cluster cluster list id.
            Args:
                session: The SQLAlchemy session
                idscluster: cluster id or cluster list id
            Returns:
                It returns the list of the ARS contained in the cluster(s)
        """
        if isinstance( idscluster, basestring ):
            idscluster = [ idscluster.strip() ]

        if not idscluster:
            return []
        strlistcluster = ",".join([str(x) for x in idscluster])
        sql="""SELECT
                    id_ars
                FROM
                    xmppmaster.has_cluster_ars
                WHERE
                    id_cluster IN (%s);""" % strlistcluster
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def get_List_Mutual_ARS_from_cluster_of_one_idars(self, session, idars):
        """
            This function returns the list of the ars from a cluster based
            on the id of one provided ARS.
            Args:
                session: The SQLAlchemy session
                idars: The id of the ARS
            Returns:
                It returns the list of the ARS contained in the cluster

        """
        sql = """SELECT
                    id_ars
                 FROM
                     xmppmaster.has_cluster_ars
                 WHERE
                    id_cluster IN (SELECT
                            id_cluster
                        FROM
                            xmppmaster.has_cluster_ars
                        WHERE
                            id_ars = %d);""" % idars
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x[0] for x in result]

    @DatabaseHelper._sessionm
    def get_List_Mutual_ARS_from_cluster_of_list_idars(self, session, listidars):
        """
            This function returns the list of the ars from a cluster based
            on the list id of one provided ARS.
            Args:
                session: The SQLAlchemy session
                idars: The id of the ARS
            Returns:
                It returns the list of the ARS contained in the cluster

        """
        listin = "%s"%  ",".join([str(x) for x in listidars])
        sql = """SELECT
                    id_ars
                 FROM
                     xmppmaster.has_cluster_ars
                 WHERE
                    id_cluster IN (SELECT
                            id_cluster
                        FROM
                            xmppmaster.has_cluster_ars
                        WHERE
                            id_ars in  (%s));""" % listin
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x[0] for x in result]

    @DatabaseHelper._sessionm
    def get_stat_ars_machine(self, session, listarsjid):
        listin = ",".join(["'%s'" % x for  x in listarsjid])
        sql="""
            SELECT
                groupdeploy,
                SUM(CASE
                    WHEN (LOCATE('linux', platform)) THEN 1
                    ELSE 0
                END) AS nblinuxmachine,
                SUM(CASE
                    WHEN (LOCATE('windows', platform)) THEN 1
                    ELSE 0
                END) AS nbwindows,
                SUM(CASE
                    WHEN (LOCATE('darwin', platform)) THEN 1
                    ELSE 0
                END) AS nbdarwin,
                SUM(CASE
                    WHEN (enabled = '1') THEN 1
                    ELSE 0
                END) AS mach_on,
                SUM(CASE
                    WHEN (enabled = '0') THEN 1
                    ELSE 0
                END) AS mach_off,
                SUM(CASE
                    WHEN (uuid_inventorymachine IS NULL) THEN 1
                    ELSE 0
                END) AS uninventoried,
                SUM(CASE
                    WHEN (uuid_inventorymachine IS NOT NULL) THEN 1
                    ELSE 0
                END) AS inventoried,
                SUM(CASE
                    WHEN
                        (enabled = '1'
                            AND uuid_inventorymachine IS NULL)
                    THEN
                        1
                    ELSE 0
                END) AS uninventoried_online,
                SUM(CASE
                    WHEN
                        (enabled = '0'
                            AND uuid_inventorymachine IS NULL)
                    THEN
                        1
                    ELSE 0
                END) AS uninventoried_offline,
                SUM(CASE
                    WHEN
                        (enabled = 1
                            AND uuid_inventorymachine IS NOT NULL)
                    THEN
                        1
                    ELSE 0
                END) AS inventoried_online,
                SUM(CASE
                    WHEN
                        (enabled = '0'
                            AND uuid_inventorymachine IS NOT NULL)
                    THEN
                        1
                    ELSE 0
                END) AS inventoried_offline,
                SUM(CASE
                    WHEN id THEN 1
                    ELSE 0
                END) AS nbmachine,
                SUM(CASE
                    WHEN (COALESCE(uuid_serial_machine, '') != '') THEN 1
                    ELSE 0
                END) AS with_uuid_serial,
                SUM(CASE
                    WHEN (classutil = 'both') THEN 1
                    ELSE 0
                END) AS bothclass,
                SUM(CASE
                    WHEN (classutil = 'public') THEN 1
                    ELSE 0
                END) AS publicclass,
                SUM(CASE
                    WHEN (classutil = 'private') THEN 1
                    ELSE 0
                END) AS privateclass,
                SUM(CASE
                    WHEN (COALESCE(ad_ou_user, '') != '') THEN 1
                    ELSE 0
                END) AS nb_ou_user,
                SUM(CASE
                    WHEN (COALESCE(ad_ou_machine, '') != '') THEN 1
                    ELSE 0
                END) AS nb_OU_mach,
                SUM(CASE
                    WHEN (kiosk_presence = 'True') THEN 1
                    ELSE 0
                END) AS kioskon,
                SUM(CASE
                    WHEN (kiosk_presence = 'FALSE') THEN 1
                    ELSE 0
                END) AS kioskoff,
                SUM(CASE
                    WHEN need_reconf THEN 1
                    ELSE 0
                END) AS nbmachinereconf
            FROM
                machines
            WHERE
                groupdeploy IN (%s)
                    AND agenttype = 'machine'
            GROUP BY groupdeploy;"""%listin

        result = session.execute(sql)
        session.commit()
        session.flush()
        resultatout = {}
        if result:
            for row in result:
                resultatout[row[0]]={}
                resultatout[row[0]]['nblinuxmachine'] = int(row[1])
                resultatout[row[0]]['nbwindows'] = int(row[2])
                resultatout[row[0]]['nbdarwin'] = int(row[3])
                resultatout[row[0]]['mach_on'] = int(row[4])
                resultatout[row[0]]['mach_off'] = int(row[5])
                resultatout[row[0]]['uninventoried'] = int(row[6])
                resultatout[row[0]]['inventoried'] = int(row[7])
                resultatout[row[0]]['uninventoried_online'] = int(row[8])
                resultatout[row[0]]['uninventoried_offline'] = int(row[9])
                resultatout[row[0]]['inventoried_online'] = int(row[10])
                resultatout[row[0]]['inventoried_offline'] = int(row[11])
                resultatout[row[0]]['nbmachine'] = int(row[12])
                resultatout[row[0]]['with_uuid_serial'] = int(row[13])
                resultatout[row[0]]['bothclass'] = int(row[14])
                resultatout[row[0]]['publicclass'] = int(row[15])
                resultatout[row[0]]['privateclass'] = int(row[16])
                resultatout[row[0]]['nb_ou_user'] = int(row[17])
                resultatout[row[0]]['nb_OU_mach'] = int(row[18])
                resultatout[row[0]]['kioskon'] = int(row[19])
                resultatout[row[0]]['kioskoff'] = int(row[20])
                resultatout[row[0]]['nbmachinereconf'] = int(row[21])
        return resultatout

    @DatabaseHelper._sessionm
    def get_ars_list_belongs_cluster(self, session, listidars, start, limit, filter):
        try:
            start = int(start)
        except:
            start = -1
        try:
            limit = int(limit)
        except:
            limit = -1

        resultobj ={'id': [],
                    'hostname': [],
                    'jid': [],
                    'jid_from_relayserver': [],
                    'cluster_name': [],
                    'cluster_description': [],
                    'classutil': [],
                    'macaddress': [],
                    'ip_xmpp': [],
                    'enabled': [],
                    'enabled_css': [],
                    'mandatory': [],
                    'switchonoff': []}

        count = 0
        # filter activate
        filterars = ""
        if filter != "":
            filterars = """ AND (relayserver.subnet LIKE '%%%s%%' OR
                relayserver.nameserver LIKE '%%%s%%' OR
                relayserver.ipserver LIKE '%%%s%%' OR
                relayserver.ipconnection LIKE '%%%s%%' OR
                relayserver.port LIKE '%%%s%%' OR
                relayserver.portconnection LIKE '%%%s%%' OR
                relayserver.mask LIKE '%%%s%%' OR
                relayserver.jid LIKE '%%%s%%' OR
                relayserver.longitude LIKE '%%%s%%' OR
                relayserver.latitude LIKE '%%%s%%' OR
                relayserver.classutil LIKE '%%%s%%' OR
                relayserver.groupdeploy LIKE '%%%s%%' OR
                relayserver.package_server_ip LIKE '%%%s%%' OR
                relayserver.package_server_port LIKE '%%%s%%' OR
                relayserver.syncthing_port LIKE '%%%s%%') """ % (filter,filter,filter,filter,filter,
                                                                 filter,filter,filter,filter,filter,
                                                                 filter,filter,filter,filter,filter)

        if listidars:
            listin = "%s"%  ",".join([str(x) for x in listidars if x != ""])
            sql="""
                SELECT SQL_CALC_FOUND_ROWS
                    relayserver.id AS relayserver_id,
                    relayserver.ipserver AS relayserver_ipserver,
                    relayserver.nameserver AS relayserver_nameserver,
                    relayserver.moderelayserver AS relayserver_moderelayserver,
                    relayserver.jid AS jid_from_relayserver,
                    relayserver.classutil AS relayserver_classutil,
                    relayserver.enabled AS relayserver_enabled,
                    relayserver.switchonoff AS relayserver_switchonoff,
                    relayserver.mandatory AS relayserver_mandatory,
                    machines.jid AS machines_jid,
                    cluster_ars.name AS cluster_name,
                    cluster_ars.description AS cluster_description,
                    cluster_ars.id AS cluster_id,
                    machines.macaddress AS macaddress
                FROM
                    relayserver
                        LEFT OUTER JOIN
                    has_cluster_ars ON has_cluster_ars.id_ars = relayserver.id
                        LEFT OUTER JOIN
                    cluster_ars ON cluster_ars.id = has_cluster_ars.id_cluster
                        LEFT OUTER JOIN
                    machines ON SUBSTRING_INDEX(machines.jid, '@', 1) = SUBSTRING_INDEX(relayserver.jid, '@', 1)
                WHERE
                    relayserver.moderelayserver = 'static' %s
                    AND relayserver.id in(	 SELECT
                                                has_cluster_ars.id_ars
                                            FROM
                                                xmppmaster.has_cluster_ars
                                            WHERE
                                                has_cluster_ars.id_cluster IN (
                                                                                SELECT
                                                                                        id_cluster
                                                                                    FROM
                                                                                        xmppmaster.has_cluster_ars
                                                                                    WHERE
                                                                                        id_ars in  (%s))

                    )""" %  (filterars,listin)
            if start != -1 and limit != -1:
                sql = sql+"LIMIT %s OFFSET %s"%(limit, start)
            sql=sql+";"
            result = session.execute(sql)

            #  Count the ARS
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            count = ret_count.first()[0]

            session.commit()
            session.flush()

            if result:
                for row in result:
                    resultobj['id'].append(row[0])
                    resultobj['hostname'].append(row[2])
                    resultobj['jid'].append(row[9])
                    resultobj['jid_from_relayserver'].append(row[4])
                    resultobj['cluster_name'].append(row[10])
                    resultobj['cluster_description'].append(row[11])
                    resultobj['classutil'].append(row[3])
                    resultobj['ip_xmpp'].append(row[1])
                    resultobj['macaddress'].append(row[13])
                    resultobj['enabled'].append(row[6])
                    resultobj['enabled_css'].append("machineNamepresente" if (row[6] == "1" or row[6] == 1) else "machineName")
                    resultobj['mandatory'].append(row[8])
                    resultobj['switchonoff'].append(row[7])

        resultobj["count"] = count
        return resultobj

    @DatabaseHelper._sessionm
    def getRelayServer(self, session, enable = None ):
        relayserver_list = []
        if enable is not None:
            relayservers = session.query(RelayServer).\
                filter(and_(RelayServer.enabled == enable)).all()
        else:
            relayservers = session.query(RelayServer).all()
        session.commit()
        session.flush()
        try:
            for relayserver in relayservers:
                res = { 'id': relayserver.id,
                        'urlguacamole': relayserver.urlguacamole,
                        'subnet': relayserver.subnet,
                        'nameserver' : relayserver.nameserver,
                        'ipserver': relayserver.ipserver,
                        'ipconnection' : relayserver.ipconnection,
                        'port': relayserver.port,
                        'portconnection': relayserver.portconnection,
                        'mask': relayserver.mask,
                        'jid': relayserver.jid,
                        'longitude': relayserver.longitude,
                        'latitude': relayserver.latitude,
                        'enabled': relayserver.enabled,
                        'switchonoff': relayserver.switchonoff,
                        'mandatory': relayserver.mandatory,
                        'classutil': relayserver.classutil,
                        'groupdeploy': relayserver.groupdeploy,
                        'package_server_ip': relayserver.package_server_ip,
                        'package_server_port': relayserver.package_server_port,
                        'moderelayserver': relayserver.moderelayserver
                    }
                relayserver_list.append(res)
            return relayserver_list
        except Exception, e:
            logging.getLogger().error(str(e))
            traceback.print_exc(file=sys.stdout)
            return relayserver_list

    @DatabaseHelper._sessionm
    def get_relayservers_no_sync_for_packageuuid(self, session, uuidpackage):
        result_list = []
        try:
            relayserversync = session.query(Syncthingsync).\
                filter(and_(Syncthingsync.uuidpackage == uuidpackage)).all()
            session.commit()
            session.flush()
            for relayserver in relayserversync:
                res={}
                res['uuidpackage'] = relayserver.uuidpackage
                res['typesynchro'] = relayserver.typesynchro
                res['relayserver_jid'] = relayserver.relayserver_jid
                res['watching'] = relayserver.watching
                res['date'] = relayserver.date
                result_list.append(res)
            return result_list
        except Exception, e:
            logging.getLogger().error(str(e))
            traceback.print_exc(file=sys.stdout)
            return []

    @DatabaseHelper._sessionm
    def xmpp_regiter_synchro_package(self, session, uuidpackage, typesynchro ):
        #list id server relay
        list_server_relay = self.get_List_jid_ServerRelay_enable(enabled=1)
        for jid in list_server_relay:
            #exclude local package server
            if jid[0].startswith("rspulse@pulse/"):
                continue
            self.setSyncthingsync(uuidpackage, jid[0], typesynchro, watching='yes')

    # =====================================================================
    # xmppmaster FUNCTIONS
    # =====================================================================

    @DatabaseHelper._sessionm
    def setlogxmpp( self,
                    session,
                    text,
                    type = "noset",
                    sessionname='',
                    priority = 0,
                    who = '',
                    how = '',
                    why = '',
                    module = '',
                    action = '',
                    touser =  '',
                    fromuser = ''):
        """
            this functions addition a log line in table log xmpp.
        """
        try:
            new_log = Logs()
            new_log.text = text
            new_log.type = type
            new_log.sessionname = sessionname
            new_log.priority = priority
            new_log.who = who
            new_log.how = how
            new_log.why = why
            new_log.module = module
            new_log.action = action
            new_log.touser = touser
            new_log.fromuser = fromuser
            session.add(new_log)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def getQAforMachine(self, session, cmd_id, uuidmachine):
        try:
            command_action = session.query(Command_action).\
                    filter(and_(Command_action.command_id == cmd_id,
                                Command_action.target == uuidmachine))
            #print command_action
            #print cmd_id
            #print uuidmachine
            command_action = command_action.all()
            listcommand = []
            for command in command_action:
                action = []
                action.append( command.command_id )
                action.append( str(command.date) )
                action.append( command.session_id )
                action.append( command.typemessage )
                action.append( command.command_result )
                listcommand.append(action)
            return listcommand
        except Exception, e:
            logging.getLogger().error(str(e))
            traceback.print_exc(file=sys.stdout)
            return []

    @DatabaseHelper._sessionm
    def getCommand_action_time(self, session, during_the_last_seconds, start, stop, filter = None):
        try:
            command_qa = session.query(distinct(Command_qa.id).label("id"),
                                       Command_qa.command_name.label("command_name"),
                                       Command_qa.command_login.label("command_login"),
                                       Command_qa.command_os.label("command_os"),
                                       Command_qa.command_start.label("command_start"),
                                       Command_qa.command_grp.label("command_grp"),
                                       Command_qa.command_machine.label("command_machine"),
                                       Command_action.target.label("target")).join(Command_action,
                                                                        Command_qa.id == Command_action.command_id)
            ##si on veut passer par les groupe avant d'aller sur les machine.
            ## command_qa = command_qa.group_by(Command_qa.id)
            command_qa = command_qa.order_by(desc(Command_qa.id))
            if during_the_last_seconds:
                command_qa = command_qa.\
                    filter( Command_qa.command_start >= (datetime.now() - timedelta(seconds=during_the_last_seconds)))
            #nb = self.get_count(deploylog)
        #lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]

            nbtotal = self.get_count(command_qa)
            if start != "" and stop != "":
                command_qa = command_qa.offset(int(start)).limit(int(stop)-int(start))
            command_qa = command_qa.all()
            session.commit()
            session.flush()
            ## creation des list pour affichage web organiser par colone
            result_list = []
            command_id_list = []
            command_name_list = []
            command_login_list = []
            command_os_list = []
            command_start_list = []
            command_grp_list = []
            command_machine_list = []
            command_target_list = []
            for command in command_qa:
                command_id_list.append(command.id)
                command_name_list.append(command.command_name)
                command_login_list.append(command.command_login)
                command_os_list.append(command.command_os)
                command_start_list.append(command.command_start)
                command_grp_list.append(command.command_grp)
                command_machine_list.append(command.command_machine)
                command_target_list.append(command.target)
            result_list.append(command_id_list)
            result_list.append(command_name_list)
            result_list.append(command_login_list)
            result_list.append(command_os_list)
            result_list.append(command_start_list)
            result_list.append(command_grp_list)
            result_list.append(command_machine_list)
            result_list.append(command_target_list)
            return {"nbtotal": nbtotal, "result": result_list}
        except Exception, e:
            logging.getLogger().debug("getCommand_action_time error %s->" % str(e))
            traceback.print_exc(file=sys.stdout)
            return {"nbtotal": 0, "result": result_list}


    @DatabaseHelper._sessionm
    def setCommand_qa(self, session, command_name, command_action,
                      command_login, command_grp='', command_machine='', command_os=''):
        try:
            new_Command_qa = Command_qa()
            new_Command_qa.command_name = command_name
            new_Command_qa.command_action = command_action
            new_Command_qa.command_login = command_login
            new_Command_qa.command_grp = command_grp
            new_Command_qa.command_machine = command_machine
            new_Command_qa.command_os = command_os
            session.add(new_Command_qa)
            session.commit()
            session.flush()
            return new_Command_qa.id
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def getCommand_qa_by_cmdid(self, session, cmdid):
        try:
            command_qa = session.query(Command_qa).filter( Command_qa.id == cmdid)
            command_qa = command_qa.first()
            session.commit()
            session.flush()
            return {"id": command_qa.id,
                    "command_name": command_qa.command_name,
                    "command_action": command_qa.command_action,
                    "command_login": command_qa.command_login,
                    "command_os": command_qa.command_os,
                    "command_start": str(command_qa.command_start),
                    "command_grp": command_qa.command_grp,
                    "command_machine": command_qa.command_machine}
        except Exception, e:
            logging.getLogger().error("getCommand_qa_by_cmdid error %s->" % str(e))
            traceback.print_exc(file=sys.stdout)
            return {"id":  "",
                    "command_name": "",
                    "command_action": "",
                    "command_login": "",
                    "command_os": "",
                    "command_start": "",
                    "command_grp": "",
                    "command_machine": ""}

    @DatabaseHelper._sessionm
    def setCommand_action(self, session, target, command_id, sessionid, command_result="", typemessage="log"):
        try:
            new_Command_action = Command_action()
            new_Command_action.session_id = sessionid
            new_Command_action.command_id = command_id
            new_Command_action.typemessage = typemessage
            new_Command_action.command_result = command_result
            new_Command_action.target = target
            session.add(new_Command_action)
            session.commit()
            session.flush()
            return new_Command_action.id
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def updateaddCommand_action(self, session, command_result, sessionid , typemessage = "result"):
        try:
            sql="""UPDATE `xmppmaster`.`command_action`
                    SET
                        `typemessage` = '%s',
                        `command_result` = CONCAT(`command_result`, ' ', '%s')
                    WHERE
                        (`session_id` = '%s');"""%(typemessage,
                                                command_result,
                                                sessionid)
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception, e:
            logging.getLogger().error(str(e))
            return False

    @DatabaseHelper._sessionm
    def logtext(self, session, text, sessionname='', type="noset", priority=0, who=''):
        try:
            new_log = Logs()
            new_log.text = text
            new_log.sessionname = sessionname
            new_log.type = type
            new_log.priority = priority
            new_log.who = who
            session.add(new_log)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))


    @DatabaseHelper._sessionm
    def log(self, session, msg, type = "info"):
        try:
            new_log = UserLog()
            new_log.msg = msg
            new_log.type = type
            session.add(new_log)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    #
    @DatabaseHelper._sessionm
    def getlistpackagefromorganization( self,
                                        session,
                                        organization_name = None,
                                        organization_id   = None):
        """
            return list package an organization
            eg call function example:
            XmppMasterDatabase().getlistpackagefromorganization( organization_id = 1)
            or
            XmppMasterDatabase().getlistpackagefromorganization( organization_name = "name")
        """
         # recupere id organization
        idorganization = -1
        try:
            if organization_id != None:
                try:
                    result_organization = session.query(Organization).filter(Organization.id == organization_id)
                    result_organization = result_organization.one()
                    session.commit()
                    session.flush()
                    idorganization = result_organization.id

                except Exception, e:
                    logging.getLogger().debug("organization id : %s does not exists" % organization_id)
                    return -1
            elif organization_name != None:
                idorganization = self.getIdOrganization(organization_name)
                if idorganization == -1:
                    return {"nb" : 0, "packageslist" : []}
            else:
                return {"nb" : 0, "packageslist" : []}
            result = session.query(Packages_list.id.label("id"),
                                Packages_list.packageuuid.label("packageuuid"),
                                Packages_list.organization_id.label("idorganization"),
                                Organization.name.label("name")).join(Organization,
                                                                        Packages_list.organization_id == Organization.id).\
                                                                filter(Organization.id == idorganization)
            nb = self.get_count(result)
            result = result.all()

            list_result = [{"id" : x.id ,
                            "packageuuid": x.packageuuid,
                            "idorganization": x.idorganization,
                            "name":  x.name} for x in result]
            return {"nb": nb, "packageslist": list_result}
        except Exception, e:
            logging.getLogger().debug("load packages for organization id : %s is error : %s" % (organization_id, str(e)))
            return {"nb": 0, "packageslist": []}

    #
    @DatabaseHelper._sessionm
    def getIdOrganization(  self,
                            session,
                            name_organization):
        """
            return id organization suivant le Name
            On error return -1
        """
        try:
            result_organization = session.query(Organization).filter(Organization.name == name_organization)
            result_organization=result_organization.one()
            session.commit()
            session.flush()
            return result_organization.id
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().debug("organization name : %s does not exists" % name_organization)
            return -1

    @DatabaseHelper._sessionm
    def addOrganization( self,
                          session,
                          name_organization):
        """
            creation d'une organization
        """
        id = self.getIdOrganization(name_organization)
        if id == -1:
            organization = Organization()
            organization.name = name_organization
            session.add(organization)
            session.commit()
            session.flush()
            return organization.id
        else :
            return id

    @DatabaseHelper._sessionm
    def delOrganization( self,
                          session,
                          name_organization):
        """
            del organization name
        """
        idorganization = self.getIdOrganization(name_organization)
        if idorganization != -1:
            session.query(Organization).\
                filter(Organization.name == name_organization).delete()
            session.commit()
            session.flush()
            q = session.query(Packages_list).\
                filter(Packages_list.organization_id == idorganization)
            q.delete()
            session.commit()
            session.flush()

    # Custom Command Quick Action################################
    @DatabaseHelper._sessionm
    def create_Qa_custom_command( self,
                                  session,
                                  user,
                                  osname,
                                  namecmd,
                                  customcmd,
                                  description = ""):
        """
            create Qa_custom_command
        """
        try:
            qa_custom_command = Qa_custom_command()
            qa_custom_command.namecmd = namecmd
            qa_custom_command.user = user
            qa_custom_command.os = osname
            qa_custom_command.customcmd = customcmd
            qa_custom_command.description = description
            session.add(qa_custom_command)
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().debug("qa_custom_command error")
            return -1

    @DatabaseHelper._sessionm
    def update_Glpi_entity( self,
                           session,
                           glpi_id,
                           complete_name = None,
                           name = None):
        try:
            result_entity = session.query(Glpi_entity).filter( Glpi_entity.glpi_id == glpi_id ).one()
            if result_entity:
                if complete_name is not None:
                    result_entity.complete_name = complete_name
                if name is not None:
                    result_entity.name = name
                session.commit()
                session.flush()
                return result_entity.get_data()
            else:
                logging.getLogger().debug("id entity no exist for update")
        except Exception:
            logging.getLogger().error("update Glpi_entity ")
        return None

    @DatabaseHelper._sessionm
    def update_Glpi_location( self,
                           session,
                           glpi_id,
                           complete_name = None,
                           name = None):
        try:
            result_location = session.query(Glpi_location).filter( Glpi_location.glpi_id == glpi_id ).one()
            if result_location:
                if complete_name is not None:
                    result_location.complete_name = complete_name
                if name is not None:
                    result_location.name = name
                session.commit()
                session.flush()
                return result_location.get_data()
            else:
                logging.getLogger().debug("id location no exist for update")
        except Exception:
            logging.getLogger().error("update Glpi_location ")
        return None

    @DatabaseHelper._sessionm
    def update_Glpi_register_key(self,
                                 session,
                                 machines_id,
                                 name,
                                 value,
                                 comment=""):
        try:
            if name is not None and name != "":
                result_register_key = session.query(Glpi_Register_Keys).\
                                            filter(or_( Glpi_Register_Keys.machines_id == machines_id,
                                                Glpi_Register_Keys.name == name)).one()
                session.commit()
                session.flush()
                if result_register_key:
                    return result_register_key.get_data()
                else:
                    logging.getLogger().debug("id registration no exist for update")
        except Exception:
            logging.getLogger().error("update Glpi_Register_Keys  : %s for machine %s does not exists" % (name,
                                                                                 machines_id))
        return None

    @DatabaseHelper._sessionm
    def get_Glpi_entity( self,
                         session,
                         glpi_id):
        """
            get Glpi_entity by glpi id machine
        """
        #logging.getLogger().error("get_Glpi_entity")
        try:
            result_entity = session.query(Glpi_entity).\
                filter( Glpi_entity.glpi_id == glpi_id ).one()
            session.commit()
            session.flush()
            if result_entity:
               return result_entity.get_data()
            else:
                logging.getLogger().debug("Glpi_entity id : %s does not exists" % glpi_id)
        except Exception, e:
            logging.getLogger().error("Glpi_entity id : %s does not exists" % glpi_id)
        return None

    @DatabaseHelper._sessionm
    def get_Glpi_location(self,
                          session,
                          glpi_id):
        """
            get Glpi_location by glpi id machine
        """
        #logging.getLogger().error("get_Glpi_location")
        try:
            result_location = session.query(Glpi_location).\
                filter( Glpi_location.glpi_id == glpi_id ).one()
            session.commit()
            session.flush()
            if result_location:
               return result_location.get_data()
            else:
                logging.getLogger().debug("Glpi_location id : %s des not exists" % glpi_id)
        except Exception, e:
            logging.getLogger().error("Glpi_location id : %s does not exists" % glpi_id)
        return None

    @DatabaseHelper._sessionm
    def get_Glpi_register_key( self,
                               session,
                               machines_id,
                               name):
        """
            get Glpi_register_key by glpi id machine and name key reg
        """
        #logging.getLogger().error("get_Glpi_register_key %s %s" %(machines_id, name) )
        try:
            result_register_key = session.query(Glpi_Register_Keys).\
                filter(and_( Glpi_Register_Keys.machines_id == machines_id,
                             Glpi_Register_Keys.name == name)).one()
            result_register_key=result_register_key
            session.commit()
            session.flush()
            if result_register_key:
               return result_register_key.get_data()
            else:
                logging.getLogger().debug("Glpi_Register_Keys  : %s"\
                    " for machine %s does not exists" % (name,
                                                      machines_id))
        except Exception, e:
                logging.getLogger().error("Glpi_Register_Keys  : %s "\
                    "for machine %s does not exists" % (name,
                                                     machines_id))
        return None

    @DatabaseHelper._sessionm
    def create_Glpi_entity( self,
                            session,
                            complete_name,
                            name,
                            glpi_id):
        """
            create Glpi_entity
        """
        if glpi_id is None or glpi_id == '':
            logging.getLogger().warning("create_Glpi_entity glpi_id missing")
            return None
        ret = self.get_Glpi_entity(glpi_id)
        if ret is None:
            # Creation of this entity
            try:
                # We create it if it does not exists
                new_glpi_entity = Glpi_entity()
                new_glpi_entity.complete_name = complete_name
                new_glpi_entity.name = name
                new_glpi_entity.glpi_id = glpi_id
                session.add(new_glpi_entity)
                session.commit()
                session.flush()
                return new_glpi_entity.get_data()
            except Exception, e:
                logging.getLogger().error(str(e))
                logging.getLogger().error("glpi_entity error")
        else:
            if ret['name'] == name and ret['complete_name'] == complete_name:
                return ret
            else:
                # update entity
                logging.getLogger().warning("update entity exist")
                return self.update_Glpi_entity(glpi_id,
                                        complete_name,
                                        name)
        return None
    @DatabaseHelper._sessionm
    def create_Glpi_location(self,
                             session,
                             complete_name,
                             name,
                             glpi_id):
        """
            create Glpi_location
        """
        if glpi_id is None or glpi_id == '':
            logging.getLogger().warning("create_Glpi_location glpi_id missing")
            return None

        ret = self.get_Glpi_location(glpi_id)
        if ret is None:
            try:
                new_glpi_location = Glpi_location()
                new_glpi_location.complete_name = complete_name
                new_glpi_location.name = name
                new_glpi_location.glpi_id = glpi_id
                session.add(new_glpi_location)
                session.commit()
                session.flush()
                return new_glpi_location.get_data()
            except Exception, e:
                logging.getLogger().error(str(e))
                logging.getLogger().error("create_Glpi_location error")
        else:
            if ret['name'] == name and ret['complete_name'] == complete_name:
                return ret
            else:
                logging.getLogger().debug("We update the location")
                return self.update_Glpi_location(glpi_id,
                                        complete_name,
                                        name)
        return None

    @DatabaseHelper._sessionm
    def create_Glpi_register_keys( self,
                                  session,
                                  machines_id,
                                  name,
                                  value=0,
                                  comment=''):
        """
            create Glpi_Register_Keys
        """

        #logging.getLogger().error("create %s = %s" %(name, value))


        if machines_id is None or machines_id == '' or name is None or name == "":
            return None
        ret = self.get_Glpi_register_key(machines_id, name)
        if ret is None:
            # creation de cette register_keys
            try:
                # creation si cette entite n'existe pas.
                new_glpi_register_keys = Glpi_Register_Keys()
                new_glpi_register_keys.name = name
                new_glpi_register_keys.value = value
                new_glpi_register_keys.machines_id = machines_id
                new_glpi_register_keys.comment = comment
                session.add(new_glpi_register_keys)
                session.commit()
                session.flush()
                return new_glpi_register_keys.get_data()
            except Exception, e:
                logging.getLogger().error(str(e))
                logging.getLogger().error("Glpi_register_keys error")
        else:
            if ret['name'] == name and ret['value'] == value:
                return ret
            else:
                logging.getLogger().warning("We update the register_keys")
                return self.update_Glpi_register_key(machines_id,
                                                     name,
                                                     value,
                                                     comment)
        return None

    @DatabaseHelper._sessionm
    def updateMachineGlpiInformationInventory(self,
                                              session,
                                              glpiinformation,
                                              idmachine,
                                              data):
        retentity = self.create_Glpi_entity(glpiinformation['data']['complete_entity'][0],
                                      glpiinformation['data']['entity'][0],
                                      glpiinformation['data']['entity_glpi_id'][0])
        if retentity is None:
            entity_id_xmpp = "NULL"
        else:
            entity_id_xmpp = retentity['id']

        retlocation = self.create_Glpi_location(glpiinformation['data']['complete_location'][0],
                                      glpiinformation['data']['location'][0],
                                      glpiinformation['data']['location_glpi_id'][0])
        if retlocation is None:
            location_id_xmpp = "NULL"
        else:
            location_id_xmpp = retlocation['id']
        if 'win' in data['information']['info']['platform'].lower():
            for regwindokey in glpiinformation['data']['reg']:
                if glpiinformation['data']['reg'][regwindokey][0] is not None:
                    self.create_Glpi_register_keys( idmachine,
                                                    regwindokey,
                                                    value=glpiinformation['data']['reg'][regwindokey][0])
        updatedb=-1
        try:
            sql = '''
                UPDATE `machines`
                SET
                    `uuid_inventorymachine` = '%s',
                    `glpi_description`  = '%s',
                    `glpi_owner_firstname` = '%s',
                    `glpi_owner_realname` = '%s',
                    `glpi_owner` = '%s',
                    `model` = '%s',
                    `manufacturer` = '%s',
                    `glpi_entity_id` = %s,
                    `glpi_location_id` = %s
                WHERE
                    `id` = '%s';''' % ("UUID%s" % glpiinformation['data']['uuidglpicomputer'][0],
                                    glpiinformation['data']['description'][0].replace('"','\\"').replace("'","\\'"),
                                    glpiinformation['data']['owner_firstname'][0],
                                    glpiinformation['data']['owner_realname'][0],
                                    glpiinformation['data']['owner'][0],
                                    glpiinformation['data']['model'][0],
                                    glpiinformation['data']['manufacturer'][0],
                                    entity_id_xmpp,
                                    location_id_xmpp,
                                    idmachine)
            updatedb = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return updatedb

    @DatabaseHelper._sessionm
    def updateName_Qa_custom_command( self,
                                     session,
                                     user,
                                     osname,
                                     namecmd,
                                     customcmd,
                                     description):
        """
            update updateName_Qa_custom_command
        """

        try:
            session.query(Qa_custom_command).filter( Qa_custom_command.namecmd == namecmd).\
                                            update( { Qa_custom_command.customcmd : customcmd ,
                                                        Qa_custom_command.description : description,
                                                        Qa_custom_command.os : osname })
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().debug("updateName_Qa_custom_command error %s->" % str(e))
            return -1


    @DatabaseHelper._sessionm
    def delQa_custom_command( self,
                              session,
                              user,
                              osname,
                              namecmd):
        """
            del Qa_custom_command
        """
        try:
            session.query(Qa_custom_command).filter(and_(Qa_custom_command.user == user,
                                                        Qa_custom_command.os == osname,
                                                        Qa_custom_command.namecmd == namecmd)
                                                        ).delete()
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().debug("delQa_custom_command error %s ->" % str(e))
            return -1


    @DatabaseHelper._sessionm
    def get_list_of_users_for_shared_qa(self, session, namecmd):
        """Return the list of users who are owning the specified QA.
        Param:
            str: namecmd the name of the quickaction
        Returns :
            list of users"""

        query = session.query(Qa_custom_command.user).filter( Qa_custom_command.namecmd == namecmd)

        if query is not None:
            user_list = [user[0] for user in query]
            return user_list
        else:
            return []


    @DatabaseHelper._sessionm
    def getlistcommandforuserbyos( self,
                                   session,
                                   user,
                                   osname  = None,
                                   min = None,
                                   max = None,
                                   filt = None,
                                   edit = None):
        ret={ 'len'     : 0,
              'nb'      : 0,
              'limit'   : 0,
              'max'     : 0,
              'min'     : 0,
              'filt'    : '',
              'command' : []}
        try:
            if edit is not None:
                # We are in the edition view
                result = session.query(Qa_custom_command).filter(and_(Qa_custom_command.user == user))
            elif osname is None:
                # We are displaying the list of QAs for use where OS is not defined (view list of QAs)
                result = session.query(Qa_custom_command).filter(or_(Qa_custom_command.user == user, Qa_custom_command.user == 'allusers'))
            else:
                # We are displaying the list of QAs for use where OS is defined (list QAs for specific machine)
                result = session.query(Qa_custom_command).filter(and_(or_(Qa_custom_command.user == user, Qa_custom_command.user == 'allusers'),
                                                                      Qa_custom_command.os == osname))

            total =  self.get_count(result)
            #todo filter
            if filt is not None:
                result = result.filter(or_(result.namecmd.like('%%%s%%' % (filt)),
                                           result.os.like('%%%s%%' % (filt)),
                                           result.description.like('%%%s%%' % (filt))
                                        )
                        )

            nbfilter =  self.get_count(result)

            if min is not None and max is not None:
                result = result.offset(int(min)).limit(int(max)-int(min))
                ret['limit'] = int(max)-int(min)

            if min:
                ret['min'] = min
            if max:
                ret['max'] = max
            if filt:
                ret['filt'] = filt
            result = result.all()
            session.commit()
            session.flush()
            ret['len'] = total
            ret['nb'] = nbfilter

            arraylist = []
            for t in result:
                obj={}
                obj['user']=t.user
                obj['os']=t.os
                obj['namecmd']=t.namecmd
                obj['customcmd']=t.customcmd
                obj['description']=t.description
                arraylist.append(obj)
            ret['command']= arraylist
            return ret
        except Exception, e:
            logging.getLogger().debug("getlistcommandforuserbyos error %s->" % str(e))
            return ret
################################################

    @DatabaseHelper._sessionm
    def addPackageByOrganization( self,
                                  session,
                                  packageuuid,
                                  organization_name = None,
                                  organization_id   = None ):
        """
        addition reference package in packages table for organization id
            the organization input parameter is either organization name or either organization id
            return -1 if not created
        """
        # recupere id organization
        idorganization = -1
        try:
            if organization_id != None:
                try:
                    result_organization = session.query(Organization).\
                        filter(Organization.id == organization_id)
                    result_organization = result_organization.one()
                    session.commit()
                    session.flush()
                    idorganization = result_organization.id
                except Exception, e:
                    logging.getLogger().debug("organization id : %s does not exist" % organization_id)
                    return -1
            elif organization_name != None:
                idorganization = self.getIdOrganization(organization_name)
                if idorganization == -1:
                    return -1
            else:
                return -1

            # addition reference package in listpackages for attribut organization id.
            packageslist = Packages_list()
            packageslist.organization_id = idorganization
            packageslist.packageuuid = packageuuid
            session.add(packageslist)
            session.commit()
            session.flush()
            return packageslist.id
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().debug("add Package [%s] for Organization : %s %s does not exists" % (packageuuid,
                                                                                                     self.__returntextisNone__(organization_name),
                                                                                                     self.__returntextisNone__(organization_id)))
            return -1

    def __returntextisNone__(para, text = ""):
        if para == None:
            return text
        else:
            return para


    ##########gestion packages###############

    ################################
    @DatabaseHelper._sessionm
    def resetPresenceMachine(self, session):
        session.query(Machines).update({Machines.enabled : '0'})
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def getIdMachineFromMacaddress(self, session, macaddress):
        presence = session.query(Machines.id).\
            filter( Machines.macaddress.like(macaddress+'%')).first()
        session.commit()
        session.flush()
        return presence

    @DatabaseHelper._sessionm
    def getMachinefrommacadress(self, session, macaddress, agenttype=None):
        """ information machine"""
        if agenttype is None:
            machine = session.query(Machines).\
                filter(Machines.macaddress.like(macaddress) ).first()
        elif agenttype=="machine":
            machine = session.query(Machines).\
                filter(and_(Machines.macaddress.like(macaddress),
                            Machines.agenttype.like("machine")) ).first()
        elif agenttype=="relayserver":
            machine = session.query(Machines).\
                filter(and_(Machines.macaddress.like(macaddress),
                            Machines.agenttype.like("relayserver")) ).first()
        session.commit()
        session.flush()
        result = {}
        if machine:
            result = {  "id" : machine.id,
                        "jid" : machine.jid,
                        "platform" : machine.platform,
                        "archi" : machine.archi,
                        "hostname" : machine.hostname,
                        "uuid_inventorymachine" : machine.uuid_inventorymachine,
                        "ip_xmpp" : machine.ip_xmpp,
                        "ippublic" : machine.ippublic,
                        "macaddress" : machine.macaddress,
                        "subnetxmpp" : machine.subnetxmpp,
                        "agenttype" : machine.agenttype,
                        "classutil" : machine.classutil,
                        "groupdeploy" : machine.groupdeploy,
                        "urlguacamole" : machine.urlguacamole,
                        "picklekeypublic" : machine.picklekeypublic,
                        'ad_ou_user': machine.ad_ou_user,
                        'ad_ou_machine': machine.ad_ou_machine,
                        'kiosk_presence': machine.kiosk_presence,
                        'lastuser': machine.lastuser,
                        'keysyncthing' : machine.keysyncthing,
                        'enabled' : machine.enabled,
                        'uuid_serial_machine' : machine.uuid_serial_machine}
        return result

    @DatabaseHelper._sessionm
    def getMachinefromuuidsetup(self, session, uuid_serial_machine, agenttype=None):
        """ information machine"""
        if agenttype is None:
            machine = session.query(Machines).\
                filter(Machines.uuid_serial_machine.like(uuid_serial_machine) ).first()
        elif agenttype=="machine":
            machine = session.query(Machines).\
                filter(and_(Machines.uuid_serial_machine.like(uuid_serial_machine),
                            Machines.agenttype.like("machine")) ).first()
        elif agenttype=="relayserver":
            machine = session.query(Machines).\
                filter(and_(Machines.uuid_serial_machine.like(uuid_serial_machine),
                            Machines.agenttype.like("relayserver")) ).first()
        session.commit()
        session.flush()
        result = {}
        if machine:
            result = {  "id" : machine.id,
                        "jid" : machine.jid,
                        "platform" : machine.platform,
                        "archi" : machine.archi,
                        "hostname" : machine.hostname,
                        "uuid_inventorymachine" : machine.uuid_inventorymachine,
                        "ip_xmpp" : machine.ip_xmpp,
                        "ippublic" : machine.ippublic,
                        "macaddress" : machine.macaddress,
                        "subnetxmpp" : machine.subnetxmpp,
                        "agenttype" : machine.agenttype,
                        "classutil" : machine.classutil,
                        "groupdeploy" : machine.groupdeploy,
                        "urlguacamole" : machine.urlguacamole,
                        "picklekeypublic" : machine.picklekeypublic,
                        'ad_ou_user': machine.ad_ou_user,
                        'ad_ou_machine': machine.ad_ou_machine,
                        'kiosk_presence': machine.kiosk_presence,
                        'lastuser': machine.lastuser,
                        'keysyncthing' : machine.keysyncthing,
                        'enabled' : machine.enabled,
                        'uuid_serial_machine' : machine.uuid_serial_machine}
        return result

    @DatabaseHelper._sessionm
    def addPresenceMachine(self,
                           session,
                           jid,
                           platform,
                           hostname,
                           archi,
                           uuid_inventorymachine,
                           ip_xmpp,
                           subnetxmpp,
                           macaddress,
                           agenttype,
                           classutil='private',
                           urlguacamole="",
                           groupdeploy="",
                           objkeypublic=None,
                           ippublic=None,
                           ad_ou_user="",
                           ad_ou_machine="",
                           kiosk_presence="False",
                           lastuser="",
                           keysyncthing="",
                           uuid_serial_machine="",
                           glpi_description="",
                           glpi_owner_firstname="",
                           glpi_owner_realname="",
                           glpi_owner="",
                           model="",
                           manufacturer="",
                           json_re="",
                           glpi_entity_id=1,
                           glpi_location_id=None,
                           glpi_regkey_id=None):

        if uuid_inventorymachine is None:
            uuid_inventorymachine = ""
        msg ="Create Machine"
        pe = -1
        if uuid_serial_machine != "":
            machineforupdate = self.getMachinefromuuidsetup(uuid_serial_machine,
                                                            agenttype=agenttype)
        else:
            machineforupdate = self.getMachinefrommacadress(macaddress,
                                                            agenttype=agenttype)
        if machineforupdate:
            pe = machineforupdate['id']
        if pe != -1:
            # update
            maxlenhostname = max([len(machineforupdate['hostname']), len(hostname)])
            maxlenjid = max([len(machineforupdate['jid']), len(jid)])
            maxmacadress = max([len(machineforupdate['macaddress']), len(macaddress)])
            maxip_xmpp = max([len(machineforupdate['ip_xmpp']), len(ip_xmpp),len("ip_xmpp")])
            maxsubnetxmpp = max([len(machineforupdate['subnetxmpp']), len(subnetxmpp), len("subnetxmpp")])
            maxonoff = 6
            uuidold = str(machineforupdate['uuid_inventorymachine'])
            if uuid_inventorymachine is None:
                uuidnew = "None"
            else:
                uuidnew = str(uuid_inventorymachine)
            maxuuid=max([len(uuidold), len(uuidnew)])
            msg ="Update Machine %8s (%s)\n" \
                "|%*s|%*s|%*s|%*s|%*s|%*s|%*s|\n" \
                "|%*s|%*s|%*s|%*s|%*s|%*s|%*s|\n" \
                "by\n" \
                "|%*s|%*s|%*s|%*s|%*s|%*s|%*s|"%(
                    machineforupdate['id'], uuid_serial_machine,
                    maxlenhostname, "hostname",
                    maxlenjid, "jid",
                    maxmacadress, "macaddress",
                    maxip_xmpp, "ip_xmpp",
                    maxsubnetxmpp, "subnetxmpp",
                    maxonoff, "On/OFF",
                    maxuuid,"UUID",
                    maxlenhostname, machineforupdate['hostname'],
                    maxlenjid, machineforupdate['jid'],
                    maxmacadress, machineforupdate['macaddress'],
                    maxip_xmpp, machineforupdate['ip_xmpp'],
                    maxsubnetxmpp, machineforupdate['subnetxmpp'],
                    maxonoff, machineforupdate['enabled'],
                    maxuuid, uuidold,
                    maxlenhostname, hostname,
                    maxlenjid, jid,
                    maxmacadress, macaddress,
                    maxip_xmpp, ip_xmpp,
                    maxsubnetxmpp, subnetxmpp,
                    maxonoff, "1",
                    6,uuidnew)
            self.logger.warning(msg)
            session.query(Machines).filter( Machines.id == pe).\
                       update({ Machines.jid: jid,
                                Machines.platform: platform,
                                Machines.hostname: hostname,
                                Machines.archi: archi,
                                Machines.uuid_inventorymachine: uuid_inventorymachine,
                                Machines.ippublic: ippublic,
                                Machines.ip_xmpp: ip_xmpp,
                                Machines.subnetxmpp: subnetxmpp,
                                Machines.macaddress: macaddress,
                                Machines.agenttype: agenttype,
                                Machines.classutil: classutil,
                                Machines.urlguacamole: urlguacamole,
                                Machines.groupdeploy: groupdeploy,
                                Machines.picklekeypublic: objkeypublic,
                                Machines.ad_ou_user: ad_ou_user,
                                Machines.ad_ou_machine: ad_ou_machine,
                                Machines.kiosk_presence: kiosk_presence,
                                Machines.lastuser: lastuser,
                                Machines.keysyncthing: keysyncthing,
                                Machines.enabled: '1',
                                Machines.uuid_serial_machine: uuid_serial_machine
                                })
            session.commit()
            session.flush()
            return pe, msg
        else:
            #create
            lenhostname = len(hostname)
            lenjid = len(jid)
            lenmacadress = len(macaddress)
            lenip_xmpp = len(ip_xmpp)
            lensubnetxmpp = len(subnetxmpp)
            lenonoff = 6
            msg ="creat Machine (%s)\n" \
                "|%*s|%*s|%*s|%*s|%*s|%*s|\n" \
                "|%*s|%*s|%*s|%*s|%*s|%*s|\n" % (
                    uuid_serial_machine,
                    lenhostname, "hostname",
                    lenjid, "jid",
                    lenmacadress, "macaddress",
                    lenip_xmpp, "ip_xmpp",
                    lensubnetxmpp, "subnetxmpp",
                    lenonoff, "On/OFF",
                    lenhostname, hostname,
                    lenjid, jid,
                    lenmacadress, macaddress,
                    lenip_xmpp, ip_xmpp,
                    lensubnetxmpp, subnetxmpp,
                    lenonoff, "1")
            self.logger.debug(msg)
            try:
                new_machine = Machines()
                new_machine.jid = jid
                new_machine.platform = platform
                new_machine.hostname = hostname
                new_machine.archi = archi
                new_machine.uuid_inventorymachine = uuid_inventorymachine
                new_machine.ippublic = ippublic
                new_machine.ip_xmpp = ip_xmpp
                new_machine.subnetxmpp = subnetxmpp
                new_machine.macaddress = macaddress
                new_machine.agenttype = agenttype
                new_machine.classutil = classutil
                new_machine.urlguacamole = urlguacamole
                new_machine.groupdeploy = groupdeploy
                new_machine.picklekeypublic = objkeypublic
                new_machine.ad_ou_user = ad_ou_user
                new_machine.ad_ou_machine = ad_ou_machine
                new_machine.kiosk_presence = kiosk_presence
                new_machine.lastuser = lastuser
                new_machine.keysyncthing = keysyncthing
                new_machine.glpi_description = glpi_description
                new_machine.glpi_owner_firstname = glpi_owner_firstname
                new_machine.glpi_owner_realname = glpi_owner_realname
                new_machine.glpi_owner = glpi_owner
                new_machine.model = model
                new_machine.manufacturer = manufacturer
                new_machine.json_re = json_re
                new_machine.glpi_entity_id = glpi_entity_id
                new_machine.glpi_location_id = glpi_location_id
                new_machine.glpi_regkey_id = glpi_regkey_id
                new_machine.enabled = '1'
                new_machine.uuid_serial_machine = uuid_serial_machine
                session.add(new_machine)
                session.commit()
                session.flush()
                if agenttype == "relayserver":
                    sql = "UPDATE `xmppmaster`.`relayserver` \
                                SET `enabled`='1' \
                                WHERE `xmppmaster`.`relayserver`.`nameserver`='%s';" % hostname
                    session.execute(sql)
                    session.commit()
                    session.flush()
                else:
                    self.checknewjid(jid)
            except Exception, e:
                logging.getLogger().error(str(e))
                msg=str(e)
                return -1, msg
            return new_machine.id, msg

    @DatabaseHelper._sessionm
    def checknewjid(self, session, newjidmachine):
        try:
            # on appelle la procedure stocke
            sql = """call afterinsertmachine('%s');"""%newjidmachine
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error("sql : %s"%traceback.format_exc())

    @DatabaseHelper._sessionm
    def is_jiduser_organization_ad(self, session, jiduser):
        """ if user exist return True"""
        sql = """SELECT COUNT(jiduser) AS nb
            FROM
                 xmppmaster.organization_ad
             WHERE
              jiduser LIKE ('%s');""" % (jiduser)
        req = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in req]
        if ret[0] == 0 :
            return False
        return True

    def uuidtoid(self, uuid):
        if uuid.strip().lower().startswith("uuid"):
            return uuid[4:]
        else:
            return uuid

    @DatabaseHelper._sessionm
    def is_id_inventory_organization_ad(self, session, id_inventory):
        """ if id_inventory exist return True"""
        sql = """SELECT COUNT(id_inventory) AS nb
            FROM
                 xmppmaster.organization_ad
             WHERE
              jiduser LIKE ('%s');""" % (self.uuidtoid(id_inventory))
        req = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in req]
        if ret[0] == 0 :
            return False
        return True

    @DatabaseHelper._sessionm
    def is_id_inventory_jiduser_organization_ad(self, session, id_inventory, jiduser):
        """ if id_inventory exist return True"""
        sql = """SELECT COUNT(id_inventory) AS nb
            FROM
                 xmppmaster.organization_ad
             WHERE
              jiduser LIKE ('%s')
              and
              id_inventory LIKE ('%s')
              ;""" % (jiduser, self.uuidtoid(id_inventory))
        req = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in req]
        if ret[0] == 0 :
            return False
        return True

    @DatabaseHelper._sessionm
    def getAllOUuser(self, session, ctx, filt = ''):
        """
        @return: all ou defined in the xmpp database
        """
        query = session.query(Organization_ad)
        if filter != '':
            query = query.filter(Organization_ad.ouuser.like('%'+filt+'%'))
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getAllOUmachine(self, session, ctx, filt = ''):
        """
        @return: all ou defined in the xmpp database
        """
        query = session.query(Organization_ad)
        if filter != '':
            query = query.filter(Organization_ad.oumachine.like('%'+filt+'%'))
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def replace_Organization_ad_id_inventory(self,
                                session,
                                old_id_inventory,
                                new_id_inventory):
        if old_id_inventory is None :
            logging.getLogger().warning("Organization AD id inventory is not exits")
            return -1
        try:
            session.query(Organization_ad).\
                filter( Organization_ad.id_inventory ==  self.uuidtoid(old_id_inventory)).\
                    update({ Organization_ad.id_inventory : self.uuidtoid(new_id_inventory) })
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updateOrganization_ad_id_inventory(self,
                                session,
                                id_inventory,
                                jiduser,
                                ouuser="",
                                oumachine="",
                                hostname="",
                                username=""):
        """
            update Organization_ad table in base xmppmaster
        """
        try:
            session.query(Organization_ad).\
                filter(Organization_ad.id_inventory ==  self.uuidtoid(id_inventory)).\
                       update({Organization_ad.jiduser: jiduser,
                              Organization_ad.id_inventory: self.uuidtoid(id_inventory),
                              Organization_ad.ouuser: ouuser,
                              Organization_ad.oumachine: oumachine,
                              Organization_ad.hostname: hostname,
                              Organization_ad.username: username})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updateOrganization_ad_jiduser(self,
                                session,
                                id_inventory,
                                jiduser,
                                ouuser="",
                                oumachine="",
                                hostname="",
                                username=""):
        """
            update Organization_ad table in base xmppmaster
        """
        try:
            session.query(Organization_ad).\
                filter( Organization_ad.jiduser ==  jiduser).\
                    update({ Organization_ad.jiduser : jiduser,
                             Organization_ad.id_inventory : self.uuidtoid(id_inventory),
                             Organization_ad.ouuser : ouuser,
                             Organization_ad.oumachine : oumachine,
                             Organization_ad.hostname : hostname,
                             Organization_ad.username : username})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def addOrganization_ad(self,
                           session,
                           id_inventory,
                           jiduser,
                           ouuser="",
                           oumachine="",
                           hostname="",
                           username=""):

        id = self.uuidtoid(id_inventory)
        new_Organization = Organization_ad()
        new_Organization.id_inventory = id
        new_Organization.jiduser = jiduser
        new_Organization.ouuser = ouuser
        new_Organization.oumachine = oumachine
        new_Organization.hostname = hostname
        new_Organization.username = username
        boolexistuserjid = self.is_jiduser_organization_ad(jiduser)
        if not boolexistuserjid:
            # creation de organization for machine jiduser
            if self.is_id_inventory_organization_ad(id):
                #delete for uuid
                self.delOrganization_ad(id_inventory = id)
            try:
                session.add(new_Organization)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error("creation Organisation_ad for jid user %s inventory uuid : %s" % (jiduser, id ))
                logging.getLogger().error("ouuser=%s\noumachine = %s\nhostname=%s\nusername=%s" % (ouuser, oumachine, hostname, username))
                logging.getLogger().error(str(e))
                return -1
            return new_Organization.id_inventory
        else:
            #update fiche
            self.updateOrganization_ad_jiduser( id_inventory,
                                                jiduser,
                                                ouuser=ouuser,
                                                oumachine=oumachine,
                                                hostname=hostname,
                                                username=username)
        return new_Organization.id_inventory

    @DatabaseHelper._sessionm
    def delOrganization_ad( self,
                            session,
                            id_inventory = None,
                            jiduser = None):
        """
            supp organization ad
        """
        req = session.query(Organization_ad)
        if id_inventory is not None and jiduser is not None:
            req=req.filter(and_(Organization_ad.id_inventory == id_inventory,
                                Organization_ad.jiduser == jiduser))
        elif id_inventory is not None and jiduser is None:
            req=req.filter(Organization_ad.id_inventory == id_inventory)
        elif jiduser is not None and id_inventory is None:
            req=req.filter(Organization_ad.jiduser == jiduser)
        else:
            return False
        try:
            req.delete()
            session.commit()
            session.flush()
            return True
        except Exception, e:
            logging.getLogger().error("delOrganization_ad : %s " % str(e))
            return False

    @DatabaseHelper._sessionm
    def loginbycommand(self, session, idcommand):
        sql = """SELECT
                    login
                FROM
                    xmppmaster.has_login_command
                WHERE
                    command = %s
                    LIMIT 1 ;""" % idcommand
        try:
            result = session.execute(sql)
            session.commit()
            session.flush()
            l = [x[0] for x in result][0]
            return l
        except Exception, e:
            logging.getLogger().error(str(e))
            return ""

    @DatabaseHelper._sessionm
    def updatedeployinfo(self, session, idcommand):
        """
        this function allows to update the counter of deployments in pause
        """
        try:
            session.query(Has_login_command).\
                filter(and_(Has_login_command.command == idcommand)).\
                    update({ Has_login_command.count_deploy_progress : Has_login_command.count_deploy_progress + 1})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            return -1

    def convertTimestampToSQLDateTime(self, value):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(value))

    def convertSQLDateTimeToTimestamp(self, value):
        return time.mktime(time.strptime(value, '%Y-%m-%d %H:%M:%S'))

    @DatabaseHelper._sessionm
    def checkstatusdeploy(self, session, idcommand):
        """
        this function is used to determine the state of the deployment when the deployemnet is scheduled and scheduler
        """
        nowtime = datetime.now()
        try:
            result = session.query(Has_login_command).filter(and_(Has_login_command.command == idcommand)).order_by(desc(Has_login_command.id)).limit(1).one()
            deployresult = session.query(Deploy).filter(and_(Deploy.command == idcommand)).order_by(desc(Deploy.id)).limit(1).one()
        except :
            # error case command supp base nunualy
            return 'abandonmentdeploy'
            pass
        if not (deployresult.startcmd <= nowtime and \
                deployresult.endcmd >= nowtime):
            #we are more in the range of deployments.
            #abandonmentdeploy
            for id in  self.sessionidforidcommand(idcommand):
                self.updatedeploystate(id,"ERROR UNKNOWN ERROR")
            return 'abandonmentdeploy'

        if not (result.start_exec_on_time is None or \
                str(result.start_exec_on_time) == '' or \
                str(result.start_exec_on_time) == "None"):
            #time processing
            if nowtime > result.start_exec_on_time:
                return 'run'
        if not (result.start_exec_on_nb_deploy is None or \
                result.start_exec_on_nb_deploy == ''):
            #nb of deploy processing
            if result.start_exec_on_nb_deploy <= result.count_deploy_progress:
                return 'run'
        for id in  self.sessionidforidcommand(idcommand):
                self.updatedeploystate(id,"DEPLOYMENT DELAYED")
        return "pause"

    @DatabaseHelper._sessionm
    def clean_syncthing_deploy(self, session, iddeploy, jid_relay):
        """
            analyse table deploy syncthing and search the shared folders which must be terminated.
        """
        datenow = datetime.datetime.now()
        sql = """SELECT
                    xmppmaster.syncthing_machine.sessionid,
                    xmppmaster.syncthing_deploy_group.directory_tmp,
                    xmppmaster.syncthing_machine.jidmachine
                FROM
                    xmppmaster.syncthing_deploy_group
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster
                            ON xmppmaster.syncthing_deploy_group.id =
                                xmppmaster.syncthing_ars_cluster.fk_deploy
                        INNER JOIN
                    xmppmaster.syncthing_machine
                            ON xmppmaster.syncthing_ars_cluster.id =
                                xmppmaster.syncthing_machine.fk_arscluster
                        INNER JOIN
                    xmppmaster.machines
                            ON xmppmaster.machines.uuid_inventorymachine =
                                xmppmaster.syncthing_machine.inventoryuuid
                WHERE
                    xmppmaster.syncthing_deploy_group.id=%s """ % iddeploy
        if jid_relay is not None:
            sql = sql + """
            and
            xmppmaster.syncthing_machine.jid_relay like '%s'""" % jid_relay
        sql = sql +";"
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def deploysyncthingxmpp(self, session):
        """
            analyse the deploy table and creates the sharing syncthing
        """
        # todo: get ARS device
        datenow = datetime.now()
        result = session.query(Deploy).filter( and_( Deploy.startcmd <= datenow,
                                                     Deploy.syncthing == 1)).all()
        id_deploylist = set()
        # TODO: search keysyncthing in table machine.
        session.commit()
        session.flush()
        if not result:
            return list(id_deploylist)
        list_id_ars = {}
        list_ars = set()
        list_cluster = set()
        # syncthing and set stat to 2
        self.chang_status_deploy_syncthing(datenow)
        cluster = self.clusterlistars()
        ###### keysyncthing  = getMachinefromjid(jid)
        cluster_pris_encharge = []
        gr_pris_en_charge = -1
        command_pris_en_charge = -1

        for t in result:
            if t.group_uuid == "":
                #machine doit faire partie d un grp
                continue
            #if command_pris_en_charge == -1:
                ##on deploy qu'une commande sur 1 group a la fois en syncthing
                #command_pris_en_charge = t.command
                #gr_pris_en_charge = t.group_uuid
            #if t.command != command_pris_en_charge or \
               #t.group_uuid != gr_pris_en_charge:
                #continue
            #if t.inventoryuuid.startswith("UUID"):
                #inventoryid = int(t.inventoryuuid[4:])
            #else:
                #inventoryid = int(t.inventoryuuid)

            e = json.loads(t.result)
            package = os.path.basename( e['path'])
            # We create the share if it does not exist.
            id_deploy = self.setSyncthing_deploy_group(t.title,
                                                       uuid.uuid4(),
                                                       package,
                                                       t.command,
                                                       t.group_uuid,
                                                       dateend=t.endcmd)
            id_deploylist.add(id_deploy)
            clu =  self.clusternum(t.jid_relay)
            ars_cluster_id = self.setSyncthing_ars_cluster( clu['numcluster'],
                                                            clu['namecluster'],
                                                            t.jid_relay,
                                                            clu['choose'],
                                                            id_deploy,
                                                            type_partage="cluster",
                                                            devivesyncthing="",
                                                            keypartage='')
            cluster = self.clusterlistars()
            clusterdata = {}
            for z in cluster:
                if t.jid_relay in cluster[z]['listarscluster']:
                    # on trouve le cluster qui possede ars
                    clusterdata = cluster[z]
            self.setSyncthing_machine(t.jidmachine,
                                      t.jid_relay,
                                      json.dumps(clusterdata),
                                      package,
                                      t.sessionid,
                                      t.start,
                                      t.startcmd,
                                      t.endcmd,
                                      t.command,
                                      t.group_uuid,
                                      t.result,
                                      ars_cluster_id,
                                      syncthing=t.syncthing,
                                      state=t.state,
                                      user=t.user,
                                      type_partage= "",
                                      title=t.title,
                                      inventoryuuid=t.inventoryuuid,
                                      login=t.login,
                                      macadress=t.macadress,
                                      comment="%s_%s" % (t.command,
                                                         t.group_uuid,))

        return list(id_deploylist)

    @DatabaseHelper._sessionm
    def clusternum(self, session, jidars):
        jidars = jidars.split("/")[0]
        sql = """SELECT
                    relayserver.jid,
                    xmppmaster.has_cluster_ars.id_cluster,
                    xmppmaster.cluster_ars.name
                FROM
                    xmppmaster.relayserver
                        INNER JOIN
                    xmppmaster.has_cluster_ars ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                        INNER JOIN
                    xmppmaster.cluster_ars ON xmppmaster.cluster_ars.id = xmppmaster.has_cluster_ars.id_cluster
                WHERE
                    xmppmaster.has_cluster_ars.id_cluster = (SELECT
                            has_cluster_ars.id_cluster
                        FROM
                            xmppmaster.relayserver
                                INNER JOIN
                            xmppmaster.has_cluster_ars ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                                INNER JOIN
                            xmppmaster.cluster_ars ON xmppmaster.cluster_ars.id = xmppmaster.has_cluster_ars.id_cluster
                        WHERE
                            relayserver.jid like '%s%%'
                            AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
                            LIMIT 1);""" % jidars
        listars = session.execute(sql)
        session.commit()
        session.flush()
        cluster={"ars": [], "numcluster" : -1 , "namecluster" :"","choose" : ""}
        n = 0
        for z in listars:
            cluster['ars'].append(z[0])
            cluster['numcluster']=z[1]
            cluster['namecluster']=z[2]
            n=n+1
        if n != 0:
            nb = random.randint(0, n-1)
            cluster['choose'] = cluster['ars'][nb]
        return cluster

    @DatabaseHelper._sessionm
    def clusterlistars(self, session, enabled = 1):
        sql = """SELECT
            GROUP_CONCAT(`jid`) AS 'listarsincluster',
            cluster_ars.name AS 'namecluster',
            cluster_ars.id AS 'numcluster',
            GROUP_CONCAT(`keysyncthing`) AS 'ksync'
        FROM
            xmppmaster.relayserver
                INNER JOIN
            xmppmaster.has_cluster_ars ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                INNER JOIN
            xmppmaster.cluster_ars ON xmppmaster.cluster_ars.id = xmppmaster.has_cluster_ars.id_cluster"""

        if enabled is not None:
            sql="""%s WHERE
            `relayserver`.`enabled` = %s
            AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)           """ % (sql, enabled)

        sql=sql+" GROUP BY xmppmaster.has_cluster_ars.id_cluster;"
        listars = session.execute(sql)
        session.commit()
        session.flush()
        cluster={}
        for z in listars:
            if z[3] is None:
                za =""
            else:
                za = z[3]
            cluster[z[2]] = { 'listarscluster' : z[0].split(","),
                             'namecluster' : z[1],
                             'numcluster' : z[2],
                             'keysyncthing' : za.split(",")}
        return cluster

    @DatabaseHelper._sessionm
    def chang_status_deploy_syncthing(self, session, datenow= None):
        if datenow is None:
            datenow = datetime.now()
        sql =""" UPDATE `xmppmaster`.`deploy` SET `syncthing`='2'
                WHERE `startcmd`<= "%s" and syncthing = 1;""" % datenow
        session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def change_end_deploy_syncthing(self, session, iddeploy, offsettime=60):

        dateend = datetime.now() + timedelta(minutes=offsettime)
        sql =""" UPDATE `xmppmaster`.`syncthing_deploy_group` SET `dateend`=%s
                WHERE `id`= "%s";""" % (dateend, iddeploy)

        session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def update_status_deploy_end(self, session):
        """ this function schedued by xmppmaster """
        datenow = datetime.now()
        result = session.query(Deploy).filter( and_( Deploy.endcmd < datenow,
                                            Deploy.state.like('DEPLOYMENT START%%'))
        ).all()
        session.flush()
        session.close()
        for t in result:
            try:
                sql = """UPDATE `xmppmaster`.`deploy`
                                SET `state`='ERROR UNKNOWN ERROR'
                                WHERE `id`='%s';""" % t.id
                session.execute(sql)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def sessionidforidcommand(self, session, idcommand):
        result = session.query(Deploy.sessionid).\
            filter(Deploy.command == idcommand).all()
        if result:
            a= [m[0] for m in result]
            return a
        else:
            return []

    @DatabaseHelper._sessionm
    def datacmddeploy(self, session, idcommand):
        try:
            result = session.query(Has_login_command).\
                filter(and_(Has_login_command.command == idcommand)).\
                    order_by(desc(Has_login_command.id)).limit(1).one()
            session.commit()
            session.flush()
            obj={
                    'countnb': 0,
                    'exec' : True
                 }
            if result.login != '':
                obj['login'] = result.login
            obj['idcmd'] = result.command
            if not (result.start_exec_on_time is None or \
                    str(result.start_exec_on_time) == '' or \
                    str(result.start_exec_on_time) == "None"):
                obj['exectime'] = str(result.start_exec_on_time)
                obj['exec'] = False

            if result.grpid != '':
                obj['grp'] = result.grpid
            if result.nb_machine_for_deploy != '':
                obj['nbtotal'] = result.nb_machine_for_deploy
            if not (result.start_exec_on_nb_deploy is None or result.start_exec_on_nb_deploy == ''):
                obj['consignnb'] = result.start_exec_on_nb_deploy
                obj['exec'] = False
            obj['rebootrequired'] = result.rebootrequired
            obj['shutdownrequired'] = result.shutdownrequired
            obj['limit_rate_ko'] = result.bandwidth
            obj['syncthing'] = result.syncthing
            if result.params_json is not None:
                try:
                    params_json = json.loads(result.params_json)
                    if 'spooling' in params_json:
                        obj['spooling'] = params_json['spooling']
                except Exception, e:
                    logging.getLogger().error("[the avanced parameters from msc] : "+str(e))

            if result.parameters_deploy is not None:
                try:
                    params = str(result.parameters_deploy)
                    if params == '':
                        return obj
                    if not params.startswith('{'):
                        params = '{' + params
                    if not params.endswith('}'):
                        params = params + '}'
                    obj['paramdeploy'] = json.loads(params)
                except Exception, e:
                    logging.getLogger().error("[the avanced parameters must be"\
                        " declared in a json dictionary] : "+ str(e))
            return obj
        except Exception, e:
            logging.getLogger().error("[ obj commandid missing] : " + str(e))
            return {}

    @DatabaseHelper._sessionm
    def adddeploy(self,
                  session,
                  idcommand,
                  jidmachine,
                  jidrelay,
                  host,
                  inventoryuuid,
                  uuidpackage,
                  state,
                  sessionid,
                  user="",
                  login="",
                  title="",
                  group_uuid = None,
                  startcmd = None,
                  endcmd = None,
                  macadress = None,
                  result = None,
                  syncthing = None
                  ):
        """
        parameters
        startcmd and endcmd  int(timestamp) either str(datetime)
        """
        createcommand = datetime.now()
        try:
            start=int(startcmd)
            end=int(endcmd)
            startcmd = datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
            endcmd = datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            #logger.error(str(e))
            pass
        # del doublon macadess
        if macadress is not None:
            adressemac = str(macadress).split("||")
            adressemac = list(set(adressemac))
            macadress = "||".join(adressemac)
        #recupere login command
        if login == "":
            login = self.loginbycommand(idcommand)[0]
        try:
            new_deploy = Deploy()
            new_deploy.group_uuid = group_uuid
            new_deploy.jidmachine = jidmachine
            new_deploy.jid_relay = jidrelay
            new_deploy.host = host
            new_deploy.inventoryuuid = inventoryuuid
            new_deploy.pathpackage =uuidpackage
            new_deploy.state = state
            new_deploy.sessionid = sessionid
            new_deploy.user = user
            new_deploy.command = idcommand
            new_deploy.login = login
            new_deploy.startcmd =startcmd
            new_deploy.endcmd = endcmd
            new_deploy.start = createcommand
            new_deploy.macadress = macadress
            new_deploy.title = title
            if result is not None:
                new_deploy.result = result
            if syncthing is not None:
                new_deploy.syncthing = syncthing
            session.add(new_deploy)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return new_deploy.id

    @DatabaseHelper._sessionm
    def deploy_machine_partage_exist(self,
                                    session,
                                    jidmachine,
                                    uidpackage):
        sql = """SELECT
                    *
                FROM
                    xmppmaster.syncthing_machine
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster ON xmppmaster.syncthing_ars_cluster.id = xmppmaster.syncthing_machine.fk_arscluster
                        INNER JOIN
                    xmppmaster.syncthing_deploy_group ON xmppmaster.syncthing_deploy_group.id = xmppmaster.syncthing_ars_cluster.fk_deploy
                WHERE
                    xmppmaster.syncthing_machine.jidmachine LIKE '%s'
                        AND xmppmaster.syncthing_deploy_group.package LIKE '%s'
                LIMIT 1;""" % (jidmachine, uidpackage)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result][0]

    @DatabaseHelper._sessionm
    def addcluster_resources(self,
                             session,
                             jidmachine,
                             jidrelay,
                             hostname,
                             sessionid,
                             login="",
                             startcmd = None,
                             endcmd = None
                            ):
        """
            add ressource for cluster ressource
        """
        self.clean_resources(jidmachine)
        try:
            new_cluster_resources = Cluster_resources()
            new_cluster_resources.jidmachine = jidmachine
            new_cluster_resources.jidrelay = jidrelay
            new_cluster_resources.hostname = hostname
            new_cluster_resources.sessionid = sessionid
            new_cluster_resources.login = login
            new_cluster_resources.startcmd =startcmd
            new_cluster_resources.endcmd = endcmd
            session.add(new_cluster_resources)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return new_cluster_resources.id

    @DatabaseHelper._sessionm
    def getcluster_resources(self, session, jidmachine):
        clusterresources = session.query(Cluster_resources).filter( Cluster_resources.jidmachine == str(jidmachine)).all()
        session.commit()
        session.flush()
        ret = { 'len' : len(clusterresources) }
        arraylist=[]
        for t in clusterresources:
            obj = {}
            obj['jidmachine'] = t.jidmachine
            obj['jidrelay'] = t.jidrelay
            obj['hostname'] = t.hostname
            obj['sessionid'] = t.sessionid
            obj['login'] = t.login
            obj['startcmd'] = str(t.startcmd)
            obj['endcmd'] = str(t.endcmd)
            arraylist.append(obj)
        ret['resource']= arraylist
        self.clean_resources(jidmachine)
        return ret

    @DatabaseHelper._sessionm
    def clean_resources(self, session, jidmachine):
        session.query(Cluster_resources).filter( Cluster_resources.jidmachine == str(jidmachine) ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def delete_resources(self, session, sessionid):
        session.query(Cluster_resources).filter( Cluster_resources.sessionid == str(sessionid) ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def getlinelogswolcmd(self, session, idcommand, uuid):
        log = session.query(Logs).filter(and_(Logs.sessionname == str(idcommand) ,
                                              Logs.type == 'wol',
                                              Logs.who == uuid)).order_by(Logs.id)
        log = log.all()
        session.commit()
        session.flush()
        ret={}
        ret['len']= len(log)
        arraylist=[]
        for t in log:
            obj={}
            obj['type']=t.type
            obj['date']=t.date
            obj['text']=t.text
            obj['sessionname']=t.sessionname
            obj['priority']=t.priority
            obj['who']=t.who
            arraylist.append(obj)
        ret['log']= arraylist
        return ret

    @DatabaseHelper._sessionm
    def get_machine_stop_deploy(self, session, cmdid , inventoryuuid):
        """
            this function return the machines list for  1 command_id and 1 uuid
        """
        query = session.query(Deploy).filter(and_( Deploy.inventoryuuid == inventoryuuid,
                                                   Deploy.command == cmdid))
        query = query.one()
        session.commit()
        session.flush()
        machine={}
        machine['len'] = 0
        try :
            machine['len'] = 1
            machine['title'] = query.title
            machine['pathpackage'] = query.pathpackage
            machine['jid_relay'] = query.jid_relay
            machine['inventoryuuid'] = query.inventoryuuid
            machine['jidmachine'] = query.jidmachine
            machine['state'] = query.state
            machine['sessionid']=query.sessionid
            machine['start'] = query.start
            machine['startcmd'] = query.startcmd
            machine['endcmd'] = query.endcmd
            machine['host'] = query.host
            machine['user'] = query.user
            machine['login'] = str(query.login)
            machine['command'] = query.command
            machine['group_uuid'] = query.group_uuid
            machine['macadress'] = query.macadress
            machine['syncthing'] = query.syncthing
        except Exception as e:
            logging.getLogger().error(str(e))
        return machine

    @DatabaseHelper._sessionm
    def get_group_stop_deploy(self, session, grpid, cmdid):
        """
            this function return the machines list for 1 group id and 1 command id
        """
        machine = session.query(Deploy).filter(and_(Deploy.group_uuid == grpid,
                                                        Deploy.command == cmdid))
        machine = machine.all()
        session.commit()
        session.flush()
        ret={}
        ret['len']= len(machine)
        arraylist = []
        for t in machine:
            obj={}
            obj['title'] = t.title
            obj['pathpackage'] = t.pathpackage
            obj['jid_relay'] = t.jid_relay
            obj['inventoryuuid'] = t.inventoryuuid
            obj['jidmachine'] = t.jidmachine
            obj['state'] = t.state
            obj['sessionid']=t.sessionid
            obj['start'] = t.start
            obj['startcmd'] = t.startcmd
            obj['endcmd'] = t.endcmd
            obj['host'] = t.host
            obj['user'] = t.user
            obj['login'] = str(t.login)
            obj['command'] = t.command
            obj['group_uuid'] = t.group_uuid
            obj['macadress'] = t.macadress
            obj['syncthing'] = t.syncthing
            arraylist.append(obj)
        ret['objectdeploy'] = arraylist
        return ret

    @DatabaseHelper._sessionm
    def getstatdeployfromcommandidstartdate(self, session, command_id, datestart):
        try:
            machinedeploy =session.query(Deploy.state,
                                         func.count(Deploy.state)).\
                                             filter(and_( Deploy.command == command_id,
                                                            Deploy.startcmd == datestart
                                                        )
                                                ).group_by(Deploy.state)
            machinedeploy = machinedeploy.all()
            ret = {'totalmachinedeploy': 0,
                   'deploymentsuccess': 0,
                   'abortontimeout': 0,
                   'abortmissingagent': 0,
                   'abortinconsistentglpiinformation': 0,
                   'abortrelaydown': 0,
                   'abortalternativerelaysdown': 0,
                   'abortinforelaymissing': 0,
                   'errorunknownerror': 0,
                   'abortpackageidentifiermissing': 0,
                   'abortpackagenamemissing': 0,
                   'abortpackageversionmissing': 0,
                   'abortpackageworkflowerror': 0,
                   'abortdescriptormissing': 0,
                   'abortmachinedisappeared': 0,
                   'abortdeploymentcancelledbyuser': 0,
                   'aborttransferfailed': 0,
                   'abortpackageexecutionerror': 0,
                   'deploymentstart': 0,
                   'wol1': 0,
                   'wol2': 0,
                   'wol3': 0,
                   'waitingmachineonline': 0,
                   'deploymentpending': 0,
                   'deploymentdelayed': 0,
                   'deploymentspooled': 0,
                   'otherstatus': 0,
                  }
            dynamic_status_list = self.get_log_status()
            dynamic_label = []
            dynamic_status = []
            if dynamic_status_list != []:
                for status in dynamic_status_list:
                    ret[status['label']] = 0
                    dynamic_label.append(status['label'])
                    dynamic_status.append(status['status'])

            liststatus = { x[0] : x[1] for x in machinedeploy}
            totalmachinedeploy = 0
            for t in liststatus:
                ret['totalmachinedeploy'] += liststatus[t]

                if t == 'DEPLOYMENT SUCCESS':
                    ret['deploymentsuccess'] = liststatus[t]
                elif t == 'ABORT ON TIMEOUT':
                    ret['abortontimeout'] = liststatus[t]
                elif t == 'ABORT MISSING AGENT':
                    ret['abortmissingagent'] = liststatus[t]
                elif t == 'ABORT INCONSISTENT GLPI INFORMATION':
                    ret['abortinconsistentglpiinformation'] = liststatus[t]
                elif t == 'ABORT RELAY DOWN':
                    ret['abortrelaydown'] = liststatus[t]
                elif t == 'ABORT ALTERNATIVE RELAYS DOWN':
                    ret['abortalternativerelaysdown'] = liststatus[t]
                elif t == 'ABORT INFO RELAY MISSING':
                    ret['abortinforelaymissing'] = liststatus[t]
                elif t == 'ERROR UNKNOWN ERROR':
                    ret['errorunknownerror'] = liststatus[t]
                elif t == 'ABORT PACKAGE IDENTIFIER MISSING':
                    ret['abortpackageidentifiermissing'] = liststatus[t]
                elif t == 'ABORT PACKAGE NAME MISSING':
                    ret['abortpackagenamemissing'] = liststatus[t]
                elif t == 'ABORT PACKAGE VERSION MISSING':
                    ret['abortpackageversionmissing'] = liststatus[t]
                elif t == 'ABORT PACKAGE WORKFLOW ERROR':
                    ret['abortpackageworkflowerror'] = liststatus[t]
                elif t == 'ABORT DESCRIPTOR MISSING':
                    ret['abortdescriptormissing'] = liststatus[t]
                elif t == 'ABORT MACHINE DISAPPEARED':
                    ret['abortmachinedisappeared'] = liststatus[t]
                elif t == 'ABORT DEPLOYMENT CANCELLED BY USER':
                    ret['abortdeploymentcancelledbyuser'] = liststatus[t]
                elif t == 'ABORT PACKAGE EXECUTION ERROR':
                    ret['abortpackageexecutionerror'] = liststatus[t]
                elif t == 'DEPLOYMENT START':
                    ret['deploymentstart'] = liststatus[t]
                elif t == 'WOL 1':
                    ret['wol1'] = liststatus[t]
                elif t == 'WOL 2':
                    ret['wol2'] = liststatus[t]
                elif t == 'WOL 3':
                    ret['wol3'] = liststatus[t]
                elif t == 'WAITING MACHINE ONLINE':
                    ret['waitingmachineonline'] = liststatus[t]
                elif t == 'DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)':
                    ret['deploymentpending'] = liststatus[t]
                elif t == 'DEPLOYMENT DELAYED':
                    ret['deploymentdelayed'] = liststatus[t]

                elif t in dynamic_status:
                    index = dynamic_status.index(t)
                    ret[dynamic_label[index]] = liststatus[t]
                else:
                    ret['otherstatus'] = liststatus[t]
            return ret
        except Exception:
            return ret

    @DatabaseHelper._sessionm
    def getstatdeploy_from_command_id_and_title(self, session, command_id, title):
        """
        Retrieve the deploy statistics based on the command_id and name
        Args:
            session: The SQL Alchemy session
            command_id: id of the deploy
            title: The name of deploy
        Return:
            It returns the number of machines per status.
        """
        try:
            machinedeploy = session.query(Deploy.state,
                                          func.count(Deploy.state)).\
                                              filter(and_(Deploy.command == command_id,
                                                          Deploy.title == title)
                                                    ).group_by(Deploy.state)
            machinedeploy = machinedeploy.all()
            ret = {'totalmachinedeploy': 0,
                   'deploymentsuccess': 0,
                   'abortontimeout': 0,
                   'abortmissingagent': 0,
                   'abortinconsistentglpiinformation': 0,
                   'abortrelaydown': 0,
                   'abortalternativerelaysdown': 0,
                   'abortinforelaymissing': 0,
                   'errorunknownerror': 0,
                   'abortpackageidentifiermissing': 0,
                   'abortpackagenamemissing': 0,
                   'abortpackageversionmissing': 0,
                   'abortpackageworkflowerror': 0,
                   'abortdescriptormissing': 0,
                   'abortmachinedisappeared': 0,
                   'abortdeploymentcancelledbyuser': 0,
                   'aborttransferfailed': 0,
                   'abortpackageexecutionerror': 0,
                   'deploymentstart': 0,
                   'wol1': 0,
                   'wol2': 0,
                   'wol3': 0,
                   'waitingmachineonline': 0,
                   'deploymentpending': 0,
                   'deploymentdelayed': 0,
                   'deploymentspooled': 0,
                   'otherstatus': 0,
                  }
            dynamic_status_list = self.get_log_status()
            dynamic_label = []
            dynamic_status = []
            if dynamic_status_list != []:
                for status in dynamic_status_list:
                    ret[status['label']] = 0
                    dynamic_label.append(status['label'])
                    dynamic_status.append(status['status'])

            liststatus = { x[0] : x[1] for x in machinedeploy}
            totalmachinedeploy = 0
            for t in liststatus:
                ret['totalmachinedeploy'] += liststatus[t]

                if t == 'DEPLOYMENT SUCCESS':
                    ret['deploymentsuccess'] = liststatus[t]
                elif t == 'ABORT ON TIMEOUT':
                    ret['abortontimeout'] = liststatus[t]
                elif t == 'ABORT MISSING AGENT':
                    ret['abortmissingagent'] = liststatus[t]
                elif t == 'ABORT INCONSISTENT GLPI INFORMATION':
                    ret['abortinconsistentglpiinformation'] = liststatus[t]
                elif t == 'ABORT RELAY DOWN':
                    ret['abortrelaydown'] = liststatus[t]
                elif t == 'ABORT ALTERNATIVE RELAYS DOWN':
                    ret['abortalternativerelaysdown'] = liststatus[t]
                elif t == 'ABORT INFO RELAY MISSING':
                    ret['abortinforelaymissing'] = liststatus[t]
                elif t == 'ERROR UNKNOWN ERROR':
                    ret['errorunknownerror'] = liststatus[t]
                elif t == 'ABORT PACKAGE IDENTIFIER MISSING':
                    ret['abortpackageidentifiermissing'] = liststatus[t]
                elif t == 'ABORT PACKAGE NAME MISSING':
                    ret['abortpackagenamemissing'] = liststatus[t]
                elif t == 'ABORT PACKAGE VERSION MISSING':
                    ret['abortpackageversionmissing'] = liststatus[t]
                elif t == 'ABORT PACKAGE WORKFLOW ERROR':
                    ret['abortpackageworkflowerror'] = liststatus[t]
                elif t == 'ABORT DESCRIPTOR MISSING':
                    ret['abortdescriptormissing'] = liststatus[t]
                elif t == 'ABORT MACHINE DISAPPEARED':
                    ret['abortmachinedisappeared'] = liststatus[t]
                elif t == 'ABORT DEPLOYMENT CANCELLED BY USER':
                    ret['abortdeploymentcancelledbyuser'] = liststatus[t]
                elif t == 'ABORT PACKAGE EXECUTION ERROR':
                    ret['abortpackageexecutionerror'] = liststatus[t]
                elif t == 'DEPLOYMENT START':
                    ret['deploymentstart'] = liststatus[t]
                elif t == 'WOL 1':
                    ret['wol1'] = liststatus[t]
                elif t == 'WOL 2':
                    ret['wol2'] = liststatus[t]
                elif t == 'WOL 3':
                    ret['wol3'] = liststatus[t]
                elif t == 'WAITING MACHINE ONLINE':
                    ret['waitingmachineonline'] = liststatus[t]
                elif t == 'DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)':
                    ret['deploymentpending'] = liststatus[t]
                elif t == 'DEPLOYMENT DELAYED':
                    ret['deploymentdelayed'] = liststatus[t]

                elif t in dynamic_status:
                    index = dynamic_status.index(t)
                    ret[dynamic_label[index]] = liststatus[t]
                else:
                    ret['otherstatus'] = liststatus[t]
            return ret
        except Exception:
            return ret

    @DatabaseHelper._sessionm
    def getdeployment_cmd_and_title(self,
                                    session,
                                    command_id,
                                    title,
                                    filter="",
                                    start=0,
                                    limit=-1):
        """
        Get the list of deploys based on the command_id and title of the packages.

        Arg:
            sesion: The SQL Alchemy session
            command_id: The id the package
            title: Name of the package
            filter: Used filters in the web page
            start: Number of the first package to show.
            limit: Maximum number of deploys sent at once.
        Return:
            It returns the list of the deploys

        """
        criterion = filter['criterion']
        filter = filter['filter']

        start = int(start)
        limit = int(limit)

        query = session.query(Deploy).filter(and_(Deploy.command == command_id,
                                                  Deploy.title == title))
        if filter == "status" and criterion != "":
            query = query.filter(or_(Deploy.state.contains(criterion),
                                     Deploy.inventoryuuid.contains(criterion),))
        if filter != 'infos':
            count = query.count()
            if limit != -1:
                query = query.offset(start).limit(limit)
        else:
            count = 0
        result = query.all()
        elements = {"id": [],
                    "uuid": [],
                    "status": []
                   }

        for deployment in result:
            elements['id'].append(deployment.inventoryuuid.replace("UUID", ""))
            elements['uuid'].append(deployment.inventoryuuid)
            elements['status'].append(deployment.state)
        return {"total": count, "datas": elements}

    @DatabaseHelper._sessionm
    def getdeployment(self, session, command_id, filter="", start=0, limit=-1):

        criterion = filter['criterion']
        filter = filter['filter']

        start = int(start)
        limit = int(limit)

        query = session.query(Deploy).filter(Deploy.command == command_id)
        if filter == "status" and criterion != "":
            query = query.filter(or_(
                Deploy.state.contains(criterion),
                Deploy.inventoryuuid.contains(criterion),
            ))

        elif filter == "relays" and criterion != "":
            query = query.filter(Deploy.jid_relay.contains(criterion))

        if filter != 'infos':
            count = query.count()
            if limit != -1:
                query = query.offset(start).limit(limit)
        else:
            count = 0
        result = query.all()
        elements = {
        "id" : [],
        "uuid" : [],
        "status" : []
        }
        for deployment in result:
            elements['id'].append(deployment.inventoryuuid.replace("UUID", ""))
            elements['uuid'].append(deployment.inventoryuuid)
            elements['status'].append(deployment.state)

        return {"total": count, "datas":elements}

    @DatabaseHelper._sessionm
    def getdeployfromcommandid(self, session, command_id, uuid):
        if (uuid == "UUID_NONE"):
            relayserver = session.query(Deploy).filter(and_(Deploy.command == command_id))
            #,Deploy.result .isnot(None)
        else:
            relayserver = session.query(Deploy).\
                filter(and_( Deploy.inventoryuuid == uuid, Deploy.command == command_id))
            #, Deploy.result .isnot(None)
        #print relayserver
        relayserver = relayserver.all()
        session.commit()
        session.flush()
        ret={}
        ret['len']= len(relayserver)
        arraylist=[]
        for t in relayserver:
            obj={}
            obj['pathpackage']=t.pathpackage
            obj['jid_relay']=t.jid_relay
            obj['inventoryuuid']=t.inventoryuuid
            obj['jidmachine']=t.jidmachine
            obj['state']=t.state
            obj['sessionid']=t.sessionid
            obj['start']=t.start
            if t.result is None:
                obj['result']=""
            else:
                obj['result']=t.result
            obj['host']=t.host
            obj['user']=t.user
            obj['login']=str(t.login)
            obj['command']=t.command
            arraylist.append(obj)
        ret['objectdeploy']= arraylist
        return ret


    @DatabaseHelper._sessionm
    def getlinelogssession(self, session, sessionnamexmpp):
        log = session.query(Logs).filter(and_( Logs.sessionname == sessionnamexmpp, Logs.type == 'deploy')).order_by(Logs.id)
        log = log.all()
        session.commit()
        session.flush()
        ret={}
        ret['len']= len(log)
        arraylist=[]
        for t in log:
            obj={}
            obj['type']=t.type
            obj['date']=t.date
            obj['text']=t.text
            obj['sessionname']=t.sessionname
            obj['priority']=t.priority
            obj['who']=t.who
            arraylist.append(obj)
        ret['log']= arraylist
        return ret

    @DatabaseHelper._sessionm
    def addlogincommand(self,
                        session,
                        login,
                        commandid,
                        grpid,
                        nb_machine_in_grp,
                        instructions_nb_machine_for_exec,
                        instructions_datetime_for_exec,
                        parameterspackage,
                        rebootrequired,
                        shutdownrequired,
                        bandwidth,
                        syncthing,
                        params):
        try:
            new_logincommand = Has_login_command()
            new_logincommand.login = login
            new_logincommand.command = commandid
            new_logincommand.count_deploy_progress = 0
            new_logincommand.bandwidth = int(bandwidth)
            if grpid != "":
                new_logincommand.grpid = grpid
            if instructions_datetime_for_exec != "":
                new_logincommand.start_exec_on_time = instructions_datetime_for_exec
            if nb_machine_in_grp != "":
                new_logincommand.nb_machine_for_deploy = nb_machine_in_grp
            if instructions_nb_machine_for_exec != "":
                new_logincommand.start_exec_on_nb_deploy =instructions_nb_machine_for_exec
            if parameterspackage != "":
                new_logincommand.parameters_deploy = parameterspackage
            if rebootrequired == 0:
                new_logincommand.rebootrequired = False
            else:
                new_logincommand.rebootrequired = True
            if shutdownrequired == 0:
                new_logincommand.shutdownrequired = False
            else:
                new_logincommand.shutdownrequired = True
            if syncthing == 0:
                new_logincommand.syncthing = False
            else:
                new_logincommand.syncthing = True
            if (type(params) is list or type(params) is dict) and len(params) != 0:
                new_logincommand.params_json = json.dumps(params)

            session.add(new_logincommand)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return new_logincommand.id

    @DatabaseHelper._sessionm
    def getListPresenceRelay(self, session):
        sql = """SELECT
                    jid, agenttype, hostname
                FROM
                    xmppmaster.machines
                WHERE
                    `machines`.`enabled` = '1' and
                    `machines`.`agenttype` = 'relayserver'
                ORDER BY hostname;"""
        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a=[]
            for t in presencelist:
                a.append({'jid':t[0],'type': t[1], 'hostname':t[2]})

            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def deploylog(self,session,nblastline):
        """ return les machines en fonction du RS """
        sql = """SELECT
                    *
                FROM
                    xmppmaster.deploy
                ORDER BY id DESC
                LIMIT %s;""" % nblastline
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def updatedeploystate1(self, session, sessionid, state):
        try:
            sql="""UPDATE `xmppmaster`.`deploy`
                SET
                    `state` = '%s'
                WHERE
                    (deploy.sessionid = '%s'
                        AND ( `state` NOT IN ('DEPLOYMENT SUCCESS' ,
                                              'ABORT DEPLOYMENT CANCELLED BY USER')
                                OR
                              `state` REGEXP '^(\?!ERROR)^(\?!SUCCESS)^(\?!ABORT)'));
                """ % (state, sessionid)
            result = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updatemachineAD(self, session, idmachine, lastuser, ou_machine, ou_user):
        """
            update Machine table in base xmppmaster
            data AD
        """
        try:
            session.query(Machines).filter(and_( Machines.id == idmachine,
                                                 Machines.enabled == '1')).\
                    update({ Machines.ad_ou_machine : ou_machine,
                             Machines.ad_ou_user : ou_user,
                             Machines.lastuser : lastuser})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updatedeploystate(self, session, sessionid, state):
        """
        update status deploy
        """
        try:
            deploysession = session.query(Deploy).filter(Deploy.sessionid == sessionid).one()
            if deploysession:
                # les status commençant par error, success, abort ne peuvent plus être modifiés.
                regexpexlusion = re.compile("^(?!abort)^(?!success)^(?!error)",re.IGNORECASE)
                if regexpexlusion.match(state) is None:
                    return
                if state == "DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)":
                    if deploysession.state in ["WOL 1",
                                               "WOL 2",
                                               "WOL 3",
                                               "WAITING MACHINE ONLINE"]:
                        #STATUS NE CHANGE PAS
                        return 0
                #update status
                deploysession.state = state
                session.commit()
                session.flush()
                return 1
        except Exception:
            logging.getLogger().error("sql : %s" % traceback.format_exc())
            return -1
        finally:
            session.close()

    @DatabaseHelper._sessionm
    def delNetwork_for_machines_id(self,session, machines_id):
        sql = """DELETE FROM `xmppmaster`.`network`
                WHERE
                    (`machines_id` = '%s');""" % machines_id
        result = session.execute(sql)
        session.commit()
        session.flush()
        return result

    @DatabaseHelper._sessionm
    def addPresenceNetwork(self, session, macaddress, ipaddress, broadcast, gateway, mask, mac, id_machine):
        #self.delNetwork_for_machines_id(id_machine)
        try:
            new_network = Network()
            new_network.macaddress=macaddress
            new_network.ipaddress=ipaddress
            new_network.broadcast=broadcast
            new_network.gateway=gateway
            new_network.mask=mask
            new_network.mac=mac
            new_network.machines_id=id_machine
            session.add(new_network)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        #return new_network.toDict()

    @DatabaseHelper._sessionm
    def addServerRelay(self, session,
                       urlguacamole,
                       subnet,
                       nameserver,
                       groupdeploy,
                       ipserver,
                       ipconnection,
                       portconnection,
                       port,
                       mask,
                       jid,
                       longitude="",
                       latitude="",
                       enabled=False,
                       classutil="private",
                       packageserverip="",
                       packageserverport="",
                       moderelayserver="static",
                       keysyncthing="",
                       syncthing_port=23000
                       ):
        sql = "SELECT count(*) as nb FROM xmppmaster.relayserver where `relayserver`.`nameserver`='%s';" % nameserver
        nb = session.execute(sql)
        session.commit()
        session.flush()
        result=[x for x in nb][0][0]
        if result == 0 :
            try:
                new_relayserver = RelayServer()
                new_relayserver.urlguacamole = urlguacamole
                new_relayserver.subnet = subnet
                new_relayserver.nameserver = nameserver
                new_relayserver.groupdeploy = groupdeploy
                new_relayserver.ipserver = ipserver
                new_relayserver.port = port
                new_relayserver.mask = mask
                new_relayserver.jid = jid
                new_relayserver.ipconnection = ipconnection
                new_relayserver.portconnection = portconnection
                new_relayserver.longitude = longitude
                new_relayserver.latitude = latitude
                new_relayserver.enabled = enabled
                new_relayserver.classutil = classutil
                new_relayserver.package_server_ip = packageserverip
                new_relayserver.package_server_port = packageserverport
                new_relayserver.moderelayserver = moderelayserver
                new_relayserver.keysyncthing = keysyncthing
                new_relayserver.syncthing_port = syncthing_port
                session.add(new_relayserver)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error(str(e))
        else:
            try:
                sql = "UPDATE `xmppmaster`.`relayserver`\
                        SET `enabled`=%s, `classutil`='%s'\
                      WHERE `xmppmaster`.`relayserver`.`nameserver`='%s';" % (enabled,
                                                                            classutil,
                                                                            nameserver)
                session.execute(sql)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def getCountPresenceMachine(self, session):
        return session.query(func.count(Machines.id)).\
            filter(Machines.enabled == '1').\
            scalar()


    @DatabaseHelper._sessionm
    def getIdUserforHostname(self, session, namesession, hostname):
        idresult = session.query(Users.id).filter(and_( Users.namesession == namesession,\
                                                        Users.hostname == hostname)).first()
        session.commit()
        session.flush()
        return idresult

    @DatabaseHelper._sessionm
    def adduser(self,
                session,
                namesession,
                hostname,
                city = "",
                region_name = "",
                time_zone = "",
                longitude = "",
                latitude = "",
                postal_code = "",
                country_code = "",
                country_name = "",
                creation_user="",
                last_modif=""):
        city = city.decode('iso-8859-1').encode('utf8')
        region_name = region_name.decode('iso-8859-1').encode('utf8')
        time_zone = time_zone.decode('iso-8859-1').encode('utf8')
        postal_code = postal_code.decode('iso-8859-1').encode('utf8')
        country_code = country_code.decode('iso-8859-1').encode('utf8')
        country_name = country_name.decode('iso-8859-1').encode('utf8')
        createuser = datetime.now()
        id = self.getIdUserforHostname(namesession, hostname)
        if id is None :
            try:
                new_user = Users()
                new_user.namesession = namesession
                new_user.hostname = hostname
                new_user.city = city
                new_user.region_name = region_name
                new_user.time_zone = time_zone
                new_user.longitude = longitude
                new_user.latitude = latitude
                new_user.postal_code = postal_code
                new_user.country_code = country_code
                new_user.country_name = country_name
                new_user.creation_user = createuser
                new_user.last_modif = createuser
                session.add(new_user)
                session.commit()
                session.flush()
                return new_user.id
            except Exception, e:
                logging.getLogger().error(str(e))
                return -1
        else:
            try:
                session.query(Users).filter(and_(Users.namesession == namesession,\
                                                 Users.hostname == hostname)).\
                    update({Users.city: city,
                            Users.region_name:region_name,
                            Users.time_zone:time_zone,
                            Users.longitude:longitude,
                            Users.latitude:latitude,
                            Users.postal_code:postal_code,
                            Users.country_code:country_code,
                            Users.country_name:country_name,
                            Users.last_modif:createuser })
                session.commit()
                session.flush()
                return id
            except Exception, e:
                logging.getLogger().error(str(e))
        return -1

    def get_count(self, q):
        count_q = q.statement.with_only_columns([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count

    def get_count1(self, q):
        return q.with_entities(func.count()).scalar()

    @DatabaseHelper._sessionm
    def getdeploybyuserlen(self, session, login=None):
        if login is not None:
            return self.get_count(session.query(Deploy).filter(Deploy.login == login))

        return self.get_count(session.query(Deploy))

    @DatabaseHelper._sessionm
    def syncthingmachineless(self,session, grp, cmd):
        mach = session.query(Syncthing_machine.jidmachine,
                             Syncthing_machine.progress,
                             Syncthing_machine.startcmd,
                             Syncthing_machine.endcmd,
                             Syncthing_machine.cluster
                             ).filter(
                                        and_(Syncthing_machine.group_uuid == grp,
                                            Syncthing_machine.command == cmd))
        result = mach.all()
        session.commit()
        session.flush()
        ret = {"data": []}

        for linemach in result:
            listchamp = []
            try:
                machime = linemach.jidmachine.split('/')[1]
            except:
                machime = linemach.jidmachine
            try:
                cluster = json.loads(linemach.cluster)
                ars = [ x.split('@')[0] for x in cluster["listarscluster"]]
                ###clusterlist = ",".join(cluster["listarscluster"])
                clusterlist = ",".join(ars)
                nbclustermachine = str(cluster["numcluster"])
            except:
                clusterlist = ""
                nbclustermachine =""
            listchamp.append(clusterlist)
            listchamp.append(nbclustermachine)
            listchamp.append(machime)
            if linemach.progress is None:
                progress = "000%"
            else:
                progress = "%03d%%" % linemach.progress
            listchamp.append(progress)
            listchamp.append(str(linemach.startcmd))
            listchamp.append(str(linemach.endcmd))
            ret["data"].append(listchamp)
        return ret

    @DatabaseHelper._sessionm
    def getLogxmpp( self,
                    session,
                    start_date,
                    end_date,
                    typelog,
                    action,
                    module,
                    user,
                    how,
                    who,
                    why,
                    headercolumn):
        ##labelheader = [x.strip() for x in headercolumn.split("|") if x.strip() != "" and x is not "None"]
        logs = session.query(Logs)
        if headercolumn == "":
            headercolumn = "date@fromuser@who@text"

        if start_date != "":
            logs = logs.filter( Logs.date > start_date)
        if end_date != "":
            logs = logs.filter( Logs.date < end_date)
        if not (typelog == "None" or typelog == ""):
            logs = logs.filter( Logs.type == typelog)
        if not (action == "None" or action == ""):
            logs = logs.filter( Logs.action == action)
        if not (module == "None" or module == ""):
            #plusieurs criteres peuvent se trouver dans ce parametre.
            criterformodule = [x.strip() for x in module.split("|") if x.strip() != "" and x != "None"]
            for x in criterformodule:
                stringsearchinmodule = "%"+x+"%"
                logs = logs.filter( Logs.module.like(stringsearchinmodule))
        if not (user == "None" or user == ""):
            logs = logs.filter( func.lower(Logs.fromuser).like(func.lower(user)) )
        if not (how == "None" or how == ""):
            logs = logs.filter( Logs.how == how)
        if not (who == "None" or who == ""):
            logs = logs.filter( Logs.who == who)
        if not (why == "None" or why == ""):
            logs = logs.filter( Logs.why == why)
        logs = logs.order_by(desc(Logs.id)).limit(1000)
        result = logs.all()
        session.commit()
        session.flush()
        ret = {"data": []}
        index = 0
        for linelogs in result:
            listchamp = []
            #listchamp.append(index)
            if headercolumn != "" and "date" in headercolumn:
                listchamp.append(str(linelogs.date))
            if headercolumn != "" and "fromuser" in headercolumn:
                listchamp.append(linelogs.fromuser)
            if headercolumn != "" and "type" in headercolumn:
                listchamp.append(linelogs.type)
            if headercolumn != "" and "action" in headercolumn:
                listchamp.append(linelogs.action)
            if headercolumn != "" and "module" in headercolumn:
                listchamp.append(linelogs.module)
            if headercolumn != "" and "how" in headercolumn:
                listchamp.append(linelogs.how)
            if headercolumn != "" and "who" in headercolumn:
                listchamp.append(linelogs.who)
            if headercolumn != "" and "why" in headercolumn:
                listchamp.append(linelogs.why)
            if headercolumn != "" and "priority" in headercolumn:
                listchamp.append(linelogs.priority)
            if headercolumn != "" and "touser" in headercolumn:
                listchamp.append(linelogs.touser)
            if headercolumn != "" and "sessionname" in headercolumn:
                listchamp.append(linelogs.sessionname)
            if headercolumn != "" and "text" in headercolumn:
                listchamp.append(linelogs.text)


            ##listchamp.append(linelogs.type)
            ##listchamp.append(linelogs.action)
            ##listchamp.append(linelogs.module)
            ##listchamp.append(linelogs.how)
            #listchamp.append(linelogs.who)
            ##listchamp.append(linelogs.why)
            ##listchamp.append(linelogs.priority)
            ##listchamp.append(linelogs.touser)
            #listchamp.append(linelogs.sessionname)
            #listchamp.append(linelogs.text)
            ret['data'].append(listchamp)
            #index = index + 1
        return ret

    @DatabaseHelper._sessionm
    def getdeploybymachinegrprecent(self, session, group_uuid, state, duree, min , max, filt):
        deploylog = session.query(Deploy)
        if group_uuid:
            deploylog = deploylog.filter( Deploy.group_uuid == group_uuid)
        if duree:
            deploylog = deploylog.filter( Deploy.start >= (datetime.now() - timedelta(seconds=duree)))
        if state:
            deploylog = deploylog.filter( Deploy.state == state)

        #todo filter
        #if filt:
            #deploylog = deploylog.filter( or_(  Deploy.state.like('%%%s%%'%(filt)),
                                                #Deploy.pathpackage.like('%%%s%%'%(filt)),
                                                #Deploy.start.like('%%%s%%'%(filt)),
                                                #Deploy.login.like('%%%s%%'%(filt)),
                                                #Deploy.host.like('%%%s%%'%(filt))))
        nb = self.get_count(deploylog)
        lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]
        ##deploylog = deploylog.group_by(Deploy.title)
        deploylog = deploylog.order_by(desc(Deploy.id))

        nb = self.get_count(deploylog)
        if min and max:
            deploylog = deploylog.offset(int(min)).limit(int(max)-int(min))

        result = deploylog.all()
        session.commit()
        session.flush()
        ret = {'lentotal': 0,
               'lenquery': 0,
               'tabdeploy': {'len': [],
                             'state': [],
                             'pathpackage': [],
                             'sessionid': [],
                             'inventoryuuid': [],
                             'command': [],
                             'start': [],
                             'login': [],
                             'host': [],
                             'macadress': [],
                             'group_uuid': [],
                             'startcmd': [],
                             'endcmd': [],
                             'jidmachine': [],
                             'jid_relay': [],
                             'title': []
                }
        }
        ret['lentotal'] = lentaillerequette[0]
        ret['lenquery'] = nb
        for linedeploy in result:
            #ret['tabdeploy']['len'].append(linedeploy[1])
            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            ret['tabdeploy']['start'].append(str(linedeploy.start))
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['host'].append(linedeploy.host.split("@")[0][:-4])
            ret['tabdeploy']['macadress'].append(linedeploy.macadress)
            if linedeploy.group_uuid == None:
                linedeploy.group_uuid = ""
            ret['tabdeploy']['group_uuid'].append(linedeploy.group_uuid)
            ret['tabdeploy']['startcmd'].append(linedeploy.startcmd)
            ret['tabdeploy']['endcmd'].append(linedeploy.endcmd)
            ret['tabdeploy']['jidmachine'].append(linedeploy.jidmachine)
            ret['tabdeploy']['jid_relay'].append(linedeploy.jid_relay)
            ret['tabdeploy']['title'].append(linedeploy.title)
        return ret

    @DatabaseHelper._sessionm
    def getdeploybymachinerecent(self, session, uuidinventory, state, duree, min , max, filt):
        deploylog = session.query(Deploy)
        if uuidinventory:
            deploylog = deploylog.filter( Deploy.inventoryuuid == uuidinventory)
        if duree:
            deploylog = deploylog.filter( Deploy.start >= (datetime.now() - timedelta(seconds=duree)))
        if state:
            deploylog = deploylog.filter( Deploy.state == state)
        #else:
            #deploylog = deploylog.filter( Deploy.state == "DEPLOYMENT START")

        #if filt:
    #deploylog = deploylog.filter( or_(  Deploy.state.like('%%%s%%'%(filt)),
                                        #Deploy.pathpackage.like('%%%s%%'%(filt)),
                                        #Deploy.start.like('%%%s%%'%(filt)),
                                        #Deploy.login.like('%%%s%%'%(filt)),
                                        #Deploy.host.like('%%%s%%'%(filt))))

        nb = self.get_count(deploylog)

        lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]
        ##deploylog = deploylog.group_by(Deploy.title)
        #deploylog = deploylog.add_column(func.count(Deploy.title))
        deploylog = deploylog.order_by(desc(Deploy.id))

        nb = self.get_count(deploylog)
        if min and max:
            deploylog = deploylog.offset(int(min)).limit(int(max)-int(min))
        result = deploylog.all()
        session.commit()
        session.flush()
        ret = {'lentotal': 0,
               'lenquery': 0,
               'tabdeploy': {'len': [],
                             'state': [],
                             'pathpackage': [],
                             'sessionid': [],
                             'inventoryuuid': [],
                             'command': [],
                             'start': [],
                             'login': [],
                             'host': [],
                             'macadress': [],
                             'group_uuid': [],
                             'startcmd': [],
                             'endcmd': [],
                             'jidmachine': [],
                             'jid_relay': [],
                             'title': []
                }
        }
        ret['lentotal'] = lentaillerequette[0]
        ret['lenquery'] = nb
        for linedeploy in result:
            #ret['tabdeploy']['len'].append(linedeploy[1])
            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            ret['tabdeploy']['start'].append(str(linedeploy.start))
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['host'].append(linedeploy.host.split("/")[-1])
            ret['tabdeploy']['macadress'].append(linedeploy.macadress)
            ret['tabdeploy']['group_uuid'].append(linedeploy.group_uuid)
            ret['tabdeploy']['startcmd'].append(linedeploy.startcmd)
            ret['tabdeploy']['endcmd'].append(linedeploy.endcmd)
            ret['tabdeploy']['jidmachine'].append(linedeploy.jidmachine)
            ret['tabdeploy']['jid_relay'].append(linedeploy.jid_relay)
            ret['tabdeploy']['title'].append(linedeploy.title)
        return ret

    @DatabaseHelper._sessionm
    def delDeploybygroup( self,
                          session,
                          numgrp):
        """
            creation d'une organization
        """
        session.query(Deploy).filter(Deploy.group_uuid == numgrp).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def getdeploybyuserrecent(self, session, login , state, duree, min=None , max=None, filt=None):
        deploylog = session.query(Deploy)
        if login:
            deploylog = deploylog.filter( Deploy.login == login)
        if state:
            deploylog = deploylog.filter( Deploy.state == state)

        if duree:
            deploylog = deploylog.filter( Deploy.start >= (datetime.now() - timedelta(seconds=duree)))

        count = """select count(*) as nb from (
        select count(id) as nb
        from deploy
        where start >= DATE_SUB(NOW(),INTERVAL 24 HOUR)
        group by title
        ) as x;"""

        if filt is not None:
            deploylog = deploylog.filter( or_(  Deploy.state.like('%%%s%%'%(filt)),
                                                Deploy.pathpackage.like('%%%s%%'%(filt)),
                                                Deploy.start.like('%%%s%%'%(filt)),
                                                Deploy.login.like('%%%s%%'%(filt)),
                                                Deploy.host.like('%%%s%%'%(filt))))
            count = """select count(*) as nb from (
              select count(id) as nb
              from deploy
              where start >= DATE_SUB(NOW(),INTERVAL 24 HOUR)
              AND (state LIKE "%%%s%%"
              or pathpackage LIKE "%%%s%%"
              or start LIKE "%%%s%%"
              or login LIKE "%%%s%%"
              or host LIKE "%%%s%%"
              )
              group by title
              ) as x;""" % (filt, filt, filt, filt, filt,)


        lentaillerequette = self.get_count(deploylog)

        result = session.execute(count)
        session.commit()
        session.flush()
        lenrequest = [x for x in result]

        #lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]
        deploylog = deploylog.group_by(Deploy.title)

        deploylog = deploylog.order_by(desc(Deploy.id))

        ##deploylog = deploylog.add_column(func.count(Deploy.title))
        if min is not None and max is not None:
            deploylog = deploylog.offset(int(min)).limit(int(max)-int(min))
        result = deploylog.all()
        session.commit()
        session.flush()
        ret ={'total_of_rows' : 0,
              'lentotal' : 0,
              'tabdeploy' : {
                                'state' : [],
                                'pathpackage' : [],
                                'sessionid' : [],
                                'start' : [],
                                'inventoryuuid' : [],
                                'command' : [],
                                'login' : [],
                                'host' : [],
                                'macadress' : [],
                                'group_uuid' : [],
                                'startcmd' : [],
                                'endcmd' : [],
                                'jidmachine' : [],
                                'jid_relay' : [],
                                'title' : []}}

        ret['lentotal'] = lentaillerequette#[0]
        ret['total_of_rows'] = lenrequest[0][0]
        reg = "(.*)\.(.*)@(.*)\/(.*)"
        for linedeploy in result:
            if re.match(reg, linedeploy.host):
                # New jid : name.salt@relay/macaddress
                hostname = linedeploy.host.split('.')[0]
            else:
                try:
                    # Old jid : macaddress@relay/name
                    hostname = linedeploy.host.split('/')[1]
                except Exception as e:
                    hostname = linedeploy.host.split('.')[0]
            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            ret['tabdeploy']['start'].append(str(linedeploy.start))
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['host'].append(hostname)
            ret['tabdeploy']['macadress'].append(linedeploy.macadress)
            ret['tabdeploy']['group_uuid'].append(linedeploy.group_uuid)
            ret['tabdeploy']['startcmd'].append(linedeploy.startcmd)
            ret['tabdeploy']['endcmd'].append(linedeploy.endcmd)
            ret['tabdeploy']['jidmachine'].append(linedeploy.jidmachine)
            ret['tabdeploy']['jid_relay'].append(linedeploy.jid_relay)
            ret['tabdeploy']['title'].append(linedeploy.title)
        return ret


    @DatabaseHelper._sessionm
    def getdeploybyuserpast(self, session, login, duree, min=None, max=None, filt=None):

        deploylog = session.query(Deploy)
        if login:
            deploylog = deploylog.filter( Deploy.login == login)

        if duree:
            deploylog = deploylog.filter( Deploy.start >= (datetime.now() - timedelta(seconds=duree)))

        if filt is not None:
            deploylog = deploylog.filter( or_(  Deploy.state.like('%%%s%%'%(filt)),
                                                Deploy.pathpackage.like('%%%s%%' % (filt)),
                                                Deploy.start.like('%%%s%%' % (filt)),
                                                Deploy.login.like('%%%s%%' % (filt)),
                                                Deploy.host.like('%%%s%%' % (filt))))

        deploylog = deploylog.filter( or_(  Deploy.state == 'DEPLOYMENT SUCCESS',
                                            Deploy.state.startswith('ERROR'),
                                            Deploy.state.startswith('ABORT')))

        lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]

        # It is the same as deploylog, but for unknown reason, the count doesn't works with ORM
        count = """select count(*) as nb from (
          select count(id) as nb
          from deploy
          where start >= DATE_SUB(NOW(),INTERVAL 3 MONTH)
          AND (state LIKE "%%%s%%"
          or pathpackage LIKE "%%%s%%"
          or start LIKE "%%%s%%"
          or login LIKE "%%%s%%"
          or host LIKE "%%%s%%"
          )
          group by title
          ) as x;"""%(filt,filt,filt,filt,filt,)
        count = session.execute(count)
        count = [nbcount for nbcount in count]

        deploylog = deploylog.group_by(Deploy.title)

        deploylog = deploylog.order_by(desc(Deploy.id))

        #deploylog = deploylog.add_column(func.count(Deploy.title))

        nbfilter =  self.get_count(deploylog)

        if min is not None and max is not None:
            deploylog = deploylog.offset(int(min)).limit(int(max)-int(min))
        result = deploylog.all()
        session.commit()
        session.flush()
        ret ={'lentotal' : 0,
              'tabdeploy' : {   'len': [],
                                'state' : [],
                                'pathpackage' : [],
                                'sessionid' : [],
                                'start' : [],
                                'inventoryuuid' : [],
                                'command' : [],
                                'login' : [],
                                'host' : [],
                                'macadress' : [],
                                'group_uuid' : [],
                                'startcmd' : [],
                                'endcmd' : [],
                                'jidmachine' : [],
                                'jid_relay' : [],
                                'title' : []}}

        #ret['lentotal'] = nbfilter
        ret['lentotal'] = count[0][0]
        reg = "(.*)\.(.*)@(.*)\/(.*)"
        for linedeploy in result:
            if re.match(reg, linedeploy.host):
                # New jid : name.salt@relay/macaddress
                hostname = linedeploy.host.split('.')[0]
            else:
                try:
                    # Old jid : macaddress@relay/name
                    hostname = linedeploy.host.split('/')[1]
                except Exception as e:
                    hostname = linedeploy.host.split('.')[0]

            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            ret['tabdeploy']['start'].append(str(linedeploy.start))
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['host'].append(hostname)
            ret['tabdeploy']['macadress'].append(linedeploy.macadress)
            ret['tabdeploy']['group_uuid'].append(linedeploy.group_uuid)
            ret['tabdeploy']['startcmd'].append(linedeploy.startcmd)
            ret['tabdeploy']['endcmd'].append(linedeploy.endcmd)
            ret['tabdeploy']['jidmachine'].append(linedeploy.jidmachine)
            ret['tabdeploy']['jid_relay'].append(linedeploy.jid_relay)
            ret['tabdeploy']['title'].append(linedeploy.title)
        return ret


    @DatabaseHelper._sessionm
    def getdeploybyuser(self, session, login = None, numrow = None, offset=None):
        if login is not None:
            deploylog = session.query(Deploy).filter(Deploy.login == login).order_by(desc(Deploy.id))
        else:
            deploylog = session.query(Deploy).order_by(desc(Deploy.id))
        if numrow is not None:
            deploylog = deploylog.limit(numrow)
            if offset is not None:
                deploylog = deploylog.offset(offset)
        deploylog = deploylog.all()
        session.commit()
        session.flush()
        ret ={'len': len(deploylog),'tabdeploy': {'state': [], 'pathpackage': [], 'sessionid': [], 'inventoryuuid': [], 'command': [], 'start': [], 'login': [],  'host': []}}
        for linedeploy in deploylog:
            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            starttime_formated = str(linedeploy.start.strftime('%Y-%m-%d %H:%M'))
            ret['tabdeploy']['start'].append(starttime_formated)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['host'].append(linedeploy.host.split("/")[-1])
        return ret

    @DatabaseHelper._sessionm
    def showmachinegrouprelayserver(self,session):
        """ return les machines en fonction du RS """
        sql = """SELECT
                `jid`,
                `agenttype`,
                `platform`,
                `groupdeploy`,
                `hostname`,
                `uuid_inventorymachine`,
                `ip_xmpp`,
                `subnetxmpp`
            FROM
                xmppmaster.machines
            WHERE
                machines.enabled = '1'
            order BY `groupdeploy` ASC, `agenttype` DESC;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def get_qaction(self, session, namecmd, user, grp, completename):
        """
            return quick actions informations
        """
        if grp == 0:
            qa_custom_command = session.query(Qa_custom_command).filter(and_(Qa_custom_command.namecmd==namecmd, Qa_custom_command.user==user))
            qa_custom_command = qa_custom_command.first()
        else:
            osdetection = ""
            if completename != "":
                if completename.endswith('(windows)'):
                    osdetection = "windows"
                elif completename.endswith('(macos)'):
                    osdetection = "macos"
                elif completename.endswith('(linux)'):
                    osdetection = "linux"
            if osdetection == "":
                qa_custom_command = session.query(Qa_custom_command).\
                    filter(and_(Qa_custom_command.customcmd==namecmd,
                                or_(Qa_custom_command.user==user,
                                    Qa_custom_command.user=="allusers")))
            else:
                qa_custom_command = session.query(Qa_custom_command).\
                    filter(and_(Qa_custom_command.customcmd==namecmd,
                                Qa_custom_command.os== osdetection,
                                or_(Qa_custom_command.user==user,
                                    Qa_custom_command.user=="allusers")))
            qa_custom_command = qa_custom_command.first()
        if qa_custom_command:
            result = {  "user" : qa_custom_command.user,
                        "os" : qa_custom_command.os,
                        "namecmd" : qa_custom_command.namecmd,
                        "customcmd" : qa_custom_command.customcmd,
                        "description" : qa_custom_command.description
                        }
            return result
        else:
            result = {}

    @DatabaseHelper._sessionm
    def listjidRSdeploy(self,session):
        """ return les RS pour le deploiement """
        sql = """SELECT
                    groupdeploy
                FROM
                    xmppmaster.machines
                WHERE
                    machines.enabled = '1' and
                    machines.agenttype = 'relayserver';"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def listmachinesfromRSdeploy( self, session, groupdeploy ):
        """ return les machine suivie par un RS """
        sql = """SELECT
                    *
                FROM
                    xmppmaster.machines
                WHERE
                    machines.enabled = '1' and
                    machines.agenttype = 'machine'
                        AND machines.groupdeploy = '%s';""" % groupdeploy
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def listmachinesfromdeploy( self, session, groupdeploy ):
        """ return toutes les machines pour un deploy """
        sql = """SELECT
                        *
                    FROM
                        xmppmaster.machines
                    WHERE
                    machines.enabled = '1' and
                    machines.groupdeploy = '%s'
                    order BY  `agenttype` DESC;""" % groupdeploy
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def ipfromjid(self, session, jid, enable = 1):
        """ return ip xmpp for JID """
        user = str(jid).split("@")[0]
        if enable is None:
            sql = """SELECT
                        ip_xmpp
                    FROM
                        xmppmaster.machines
                    WHERE
                        jid LIKE ('%s%%')
                                    LIMIT 1;""" % user
        else:
            sql = """SELECT
                        ip_xmpp
                    FROM
                        xmppmaster.machines
                    WHERE
                        enabled = '%s' and
                        jid LIKE ('%s%%')
                                    LIMIT 1;""" % (enable, user)

        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def groupdeployfromjid(self, session, jid):
        """ return groupdeploy xmpp for JID """
        user = str(jid).split("@")[0]
        sql = """SELECT
                    groupdeploy
                FROM
                    xmppmaster.machines
                WHERE
                    enabled = '1' and
                    jid LIKE ('%s%%')
                                LIMIT 1;""" % user
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def ippackageserver(self, session, jid):
        """ return ip xmpp for JID """
        user = str(jid).split("@")[0]
        sql = """SELECT
                    package_server_ip
                FROM
                    xmppmaster.relayserver
                WHERE
                    jid LIKE ('%s@%%')
                                LIMIT 1;""" % user
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def portpackageserver(self, session, jid):
        """ return ip xmpp for JID """
        user = str(jid).split("@")[0]
        sql = """SELECT
                    package_server_port
                FROM
                    xmppmaster.relayserver
                WHERE
                    jid LIKE ('%s%%')
                                LIMIT 1;""" % user
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def ipserverARS(self, session, jid):
        """ return ip xmpp for JID """
        user = str(jid).split("@")[0]
        sql = """SELECT
                    ipserver
                FROM
                    xmppmaster.relayserver
                WHERE
                    jid LIKE ('%s%%')
                                LIMIT 1;""" % user
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def getUuidFromJid(self, session, jid):
        """
            This function return the UUID based on the jid

            Args:
                session:    The sqlalchemy session
                jid:        The jid of the machine we want to determine the UUID

            Returns:
                It returns the UUID based on the jid, False otherwise
        """
        uuid_inventorymachine = session.query(Machines).filter_by(jid=jid).first().uuid_inventorymachine
        if uuid_inventorymachine:
            return uuid_inventorymachine.strip('UUID')

        return False

    @DatabaseHelper._sessionm
    def algoruleadorganisedbyusers(self, session, userou, classutilMachine = "both", rule = 8, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 8 by organization users
            Field "subject" is used to define the organisation by user OU eg Computers/HeadQuarter/Locations
            Field "relayserver_id" is used to define the Relayserver associe a ce name user
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """

        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (rule, userou, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (rule, userou, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algoruleadorganisedbymachines(self,
                                      session,
                                      machineou,
                                      classutilMachine = "both",
                                      rule = 7,
                                      enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 7 by organization machine
            Field "subject" is used to define the organisation by machine OU eg Computers/HeadQuarter/Locations
            Field "relayserver_id" is used to define the Relayserver associe a this organization
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (rule, machineou, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (rule, machineou, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]


    @DatabaseHelper._sessionm
    def algoruleuser(self, session, username, classutilMachine = "both", rule = 1, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 1 for user name
            Field "subject" is used to define the name of the user in this rule
            Field "relayserver_id" is used to define the Relayserver associe a ce name user
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
            limit 1;""" % (rule, username, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
            limit 1;""" % (rule, username, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulehostname(self, session, hostname, classutilMachine = "both", rule = 2, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search
                              only to the rule designated. rule_id = 2 for hostname
            Field "subject" is used to define the hostname in this rule
            enabled = 1 Only on active relayserver.
            If classutilMachine is private then the choice of relayserver will be
              in the relayservers reserved for machines where [global].agent_space
              configuration is set to private.
            # hostname regex
                #hostname matches subject of has_relayserverrules table
                #-- subject is the regex.
                #-- eg : ^machine_win_.*1$
                #-- eg : ^machine_win_.*[2-9]{1,3}$
                Tip: For cheching the regex using Mysql use
                    select "hostname_for_test" REGEXP "^hostname.*";  => result  1
                    select "hostname_for_test" REGEXP "^(?!hostname).*"; => result 0
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id` , `has_relayserverrules`.`subject`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            order by `has_relayserverrules`.`order`
            limit 1;""" % (rule, hostname, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id` , `has_relayserverrules`.`subject`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            order by `has_relayserverrules`.`order`
            limit 1;""" % (rule, hostname, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        ret = [y for y in result]
        if ret:
            logging.getLogger().debug("Matched hostname rule with "\
                "hostname \"%s\# by regex \#%s\"" % (hostname, ret[0].subject))
        return ret

    @DatabaseHelper._sessionm
    def algoruleloadbalancer(self, session):
        sql = """
            SELECT
                COUNT(*) AS nb, `machines`.`groupdeploy`, `relayserver`.`id`
            FROM
                xmppmaster.machines
                    INNER JOIN
                xmppmaster.`relayserver` ON `relayserver`.`groupdeploy` = `machines`.`groupdeploy`
            WHERE
                enabled = '1' and
                agenttype = 'machine'
                AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            GROUP BY `machines`.`groupdeploy`
            ORDER BY nb DESC
            LIMIT 1;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulesubnet(self, session, subnetmachine, classutilMachine = "both",  enabled=1):
        """
            To associate relay server that is on same networks...
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
            where
                        `relayserver`.`enabled` = %d
                    AND `relayserver`.`subnet` ='%s'
                    AND `relayserver`.`classutil` = '%s'
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (enabled, subnetmachine, classutilMachine)
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
            where
                        `relayserver`.`enabled` = %d
                    AND `relayserver`.`subnet` ='%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (enabled, subnetmachine)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulebynetmaskaddress(self, session, netmaskaddress, classutilMachine = "both", rule = 10, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 10 by network mask
            Field "netmaskaddress" is used to define the net mask address for association
            Field "relayserver_id" is used to define the Relayserver to be assigned to the machines matching that rule
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (rule, netmaskaddress, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (rule, netmaskaddress, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulebynetworkaddress(self,
                                 session,
                                 subnetmachine,
                                 classutilMachine = "both",
                                 rule = 9, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 9 by network address
            Field "subject" is used to define the subnet for association
            Field "relayserver_id" is used to define the Relayserver to be assigned to the machines matching that rule
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
            subnetmachine CIDR machine.
                CIDR matching with subject of table has_relayserverrules
                -- subject is the expresseion relationel.
                -- eg : ^55\.171\.[5-6]{1}\.[0-9]{1,3}/24$
                -- eg : ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/24$ all adress mask 255.255.255.255
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            order by `has_relayserverrules`.`order`
            limit 1;""" % (rule, subnetmachine, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            order by `has_relayserverrules`.`order`
            limit 1;""" % (rule, subnetmachine, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def IpAndPortConnectionFromServerRelay(self, session, id):
        """ return ip et port server relay for connection"""
        sql = """SELECT
                    ipconnection, port, jid, urlguacamole
                 FROM
                    xmppmaster.relayserver
                 WHERE
                    id = %s;""" % id
        result = session.execute(sql)
        session.commit()
        session.flush()
        return list( [x for x in result][0])

    @DatabaseHelper._sessionm
    def jidrelayserverforip(self, session, ip ):
        """ return jid server relay for connection"""
        sql ="""SELECT
                    ipconnection, port, jid, urlguacamole
                FROM
                    xmppmaster.relayserver
                WHERE
                    ipconnection = '%s';""" % ip
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def IdlonglatServerRelay(self, session, classutilMachine = "both",  enabled=1):
        """ return long and lat server relay"""
        if classutilMachine == "private":
            sql = """SELECT
                        id, longitude, latitude
                    FROM
                        xmppmaster.relayserver
                    WHERE
                            `relayserver`.`enabled` = %d
                        AND `relayserver`.`classutil` = '%s'
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`);""" % (enabled,
                                                                                        classutilMachine)
        else:
            sql = """SELECT
                        id,longitude,latitude
                    FROM
                        xmppmaster.relayserver
                    WHERE
                            `relayserver`.`enabled` = %d
                            AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`);""" % (enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    #@DatabaseHelper._sessionm
    #def algoruledefault(self, session, subnetmachine, classutilMachine = "private",  enabled=1):
        #pass

    #@DatabaseHelper._sessionm
    #def algorulegeo(self, session, subnetmachine, classutilMachine = "private",  enabled=1):
        #pass

    @DatabaseHelper._sessionm
    def Orderrules(self, session):
        sql = """SELECT
                    *
                FROM
                    xmppmaster.rules
                ORDER BY level;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def hasmachineusers(self, session, machines_id, users_id):
        result = session.query(Has_machinesusers.machines_id).\
           filter(and_( Has_machinesusers.machines_id == machines_id,\
                        Has_machinesusers.users_id == users_id)).first()
        session.commit()
        session.flush()
        if result is None:
            new_machineuser = Has_relayserverrules()
            new_machineuser.machines_id = machines_id
            new_machineuser.users_id = users_id
            session.commit()
            session.flush()
            return True
        return False

    @DatabaseHelper._sessionm
    def addguacamoleidformachineid(self, session, machine_id, idguacamole):
        try:
            hasguacamole = Has_guacamole()
            hasguacamole.idguacamole=idguacamole
            hasguacamole.machine_id=machine_id
            session.add(hasguacamole)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def addlistguacamoleidformachineid(self, session, machine_id, connection):
        # objet connection: {u'VNC': 60, u'RDP': 58, u'SSH': 59}}
        if not connection:
            # on ajoute 1 protocole inexistant pour signaler que guacamle est configure.
            connection['INF'] = 0

        sql  = """DELETE FROM `xmppmaster`.`has_guacamole`
                    WHERE
                        `xmppmaster`.`has_guacamole`.`machine_id` = '%s';""" % machine_id
        session.execute(sql)
        session.commit()
        session.flush()

        for idguacamole in connection:
            try:
                hasguacamole = Has_guacamole()
                hasguacamole.idguacamole=connection[idguacamole]
                hasguacamole.machine_id=machine_id
                hasguacamole.protocol=idguacamole
                session.add(hasguacamole)
                session.commit()
                session.flush()
            except Exception, e:
                #logging.getLogger().error("addPresenceNetwork : %s " % new_network)
                logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def listserverrelay(self, session, moderelayserver = "static"):
        sql = """SELECT
                    jid
                FROM
                    xmppmaster.relayserver
                WHERE
                    `xmppmaster`.`relayserver`.`moderelayserver` = '%s'
                    ;""" % moderelayserver
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def column_list_table(self, session, tablename, basename="xmppmaster" ):
        """
            This function returns the list of column titles in the table,
            where the name of this table is passed as a parameter.
        """
        try:
            sql = """SELECT
                        column_name
                    FROM
                        information_schema.columns WHERE table_name = '%s'
                        AND
                        table_schema='%s';""" % (tablename, basename)
            result = session.execute(sql)
            session.commit()
            session.flush()
            return [x[0] for x in result]
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().error("\n%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def random_list_ars_relay_one_only_in_cluster(self, session, sessiontype_return="dict"):
        """
            this function search 1 list ars.
            1 only ars by cluster.
            the ars of cluster is randomly selected

            return object is 1 list organize per row found.
                following the sessiontype_return parameter:
                    - sessiontype_return is "dict"
                        the rows are expressed in the form of dictionary (column name, value column)
                    - sessiontype_return is "list"
                        the rows are expressed as a list of values.
        """
        sql = """SELECT
                    *
                FROM
                    xmppmaster.relayserver
                WHERE
                    `xmppmaster`.`relayserver`.`id` IN (
                        SELECT
                            id
                        FROM
                            (SELECT
                                id
                            FROM
                                (SELECT
                                    xmppmaster.relayserver.id AS id,
                                    xmppmaster.has_cluster_ars.id_cluster AS cluster
                                FROM
                                    xmppmaster.relayserver
                                INNER JOIN xmppmaster.has_cluster_ars
                                        ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                                ORDER BY RAND()) selectrandonlistars
                            GROUP BY cluster) selectcluster);"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        a = []
        if result:
            if sessiontype_return == "dict":
                columnlist = self.column_list_table("relayserver")
                for ligneresult in [x for x in result]:
                    obj = {}
                    for index, value in enumerate(columnlist):
                        obj[value] = ligneresult[index]
                    a.append(obj)
                return a
            else:
                return [x[0] for x in result]
        else:
            return []

    @DatabaseHelper._sessionm
    def listmachines(self, session, enable = '1'):
        sql = """SELECT
                    jid
                FROM
                    xmppmaster.machines
                WHERE
                    xmppmaster.machines.enabled = '%s' and
                    xmppmaster.machines.agenttype="machine";""" % enable
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def clearMachine(self, session):
        session.execute('TRUNCATE TABLE xmppmaster.machines;')
        session.execute('TRUNCATE TABLE xmppmaster.network;')
        session.execute('TRUNCATE TABLE xmppmaster.has_machinesusers;')
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def listMacAdressforMachine(self, session, id_machine, infomac = False):
        try:
            sql = """SELECT
                        GROUP_CONCAT(DISTINCT mac ORDER BY mac ASC  SEPARATOR ',') AS listmac
                    FROM
                        xmppmaster.network
                    WHERE
                        machines_id = '%s';""" % (id_machine)
            if infomac:
                logging.getLogger().debug("SQL request to get the mac addresses list "\
                                        "for the presence machine #%s" % id_machine)
            listMacAdress = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        result=[x for x in listMacAdress][0]
        if infomac:
            logging.getLogger().debug("Result list MacAdress for Machine : %s" % result[0])
        return result

    @DatabaseHelper._sessionm
    def getjidMachinefromuuid(self, session, uuid):
        try:
            sql = """SELECT
                        jid
                    FROM
                        xmppmaster.machines
                    WHERE
                        enabled = '1' and
                        uuid_inventorymachine = '%s'
                        LIMIT 1;""" % uuid
            jidmachine = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
            return ""
        try :
            result=[x for x in jidmachine][0]
        except:
            return ""
        return result[0]

    @DatabaseHelper._sessionm
    def updateMachineidinventory(self, session, id_machineinventory, idmachine):
        updatedb=-1
        try:
            sql = """UPDATE `machines`
                    SET
                        `uuid_inventorymachine` = '%s'
                    WHERE
                        `id` = '%s';""" % (id_machineinventory, idmachine)
            updatedb = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return updatedb

    def datetimetotimestamp(self, date):
        return int(time.mktime(date.timetuple()))

    def query_to_array_of_dict(self, ret,
                               timestmp = False,
                               list_colonne_name = True,
                               bycolumn=True,
                               nbelement = True,
                               listexclude= []):
        """ convert sql objet to list of dict"""
        result = []
        if ret is not None:
            countelt = ret.rowcount
            columns_name = ret.keys()
            columns_name = [x for x in columns_name if x not in listexclude]
            if not bycolumn:
                for row in ret:
                    if row is not None:
                        dictresult = {}
                        for key, value in row.items():
                            if key in listexclude:
                                continue
                            logger.warning("value type %s" % type(value))
                            if value is  None :
                                dictresult[key] = ''
                            elif isinstance(value, datetime):
                                dictresult[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                                if timestmp:
                                    dictresult["%s_stmp"%key] = self.datetimetotimestamp(value)
                            else:
                                dictresult[key] = value
                        logger.warning("value type %s" % type(value))
                        result.append(dictresult)

            else: # by column
                # create list by name.
                # initialisation structure result
                if ret:
                    result = {"data":{index : [] for index in columns_name}}
                    if nbelement :
                        result["count"] = countelt
                    if list_colonne_name:
                        result['data']['columns_name'] = columns_name
                    for row in ret:
                        if row is not None:
                            for key, value in row.items():
                                if key in listexclude:
                                    continue
                                if value is  None :
                                    result['data'][key].append('')
                                elif isinstance(value, datetime):
                                    result['data'][key].append(value.strftime("%Y-%m-%d %H:%M:%S"))
                                    #if timestmp:
                                        #dictresult["%s_stmp"%key] = self.datetimetotimestamp(value)
                                else:
                                    result['data'][key].append(value)
        else:
            result =[{}]
        return result

    @DatabaseHelper._sessionm
    def get_machines_list(self, session, start, end, ctx):
        def _likecriterium(field, filter):
            return  " AND %s like '%%%s%%'"% (field,filter)
        # fiel for table mach
        machinefield = ['id', 'jid',
                        'uuid_serial_machine',
                        'enabled', 'platform',
                        'archi','hostname',
                        'uuid_inventorymachine','ippublic',
                        'ip_xmpp', 'macaddress',
                        'subnetxmpp', 'agenttype',
                        'classutil', 'groupdeploy',
                        'urlguacamole', 'picklekeypublic',
                        'ad_ou_machine', 'ad_ou_user',
                        'glpi_description',
                        'lastuser', 'keysyncthing',
                        'glpi_owner_firstname', 'glpi_owner_realname',
                        'glpi_owner', 'glpi_entity_id',
                        'glpi_location_id','model',
                        'manufacturer','need_reconf', 'kiosk_presence']
        # fiel for table ent and alias
        entityfield =   {'entityname': "name",
                         'entitypath': "complete_name",
                         'entityid': "glpi_id"}
        # fiel for table location and alias
        locationfield = {'locationname': "name",
                         'locationpath': "complete_name",
                         'locationid': "glpi_id"}
        debugfunction = 0
        recherchefild = ""
        ctx['field']=ctx['field'].strip()
        ctx['filter']=ctx['filter'].strip()
        if "@@@DEBUG@@@" in ctx['filter']:
            debugfunction = 1
            ctx['filter']  = ctx['filter'].replace("@@DEBUG@@", "").strip()

        if 'field' in ctx and ctx['field'].strip() != '':
            if 'filter' in ctx and ctx['filter'].strip() != '':
                if ctx['field'] == "allchamp":
                    tabelt=[]
                    for indexchamp in machinefield:
                        elt = "mach.%s" % indexchamp
                        tabelt.append( "COALESCE(%s, '')"%elt)
                    for indexchamp in entityfield:
                        elt = "ent.%s" % entityfield[indexchamp]
                        tabelt.append( "COALESCE(%s, '')"%elt)
                    for indexchamp in locationfield:
                        elt = "loc.%s" % locationfield[indexchamp]
                        tabelt.append( "COALESCE(%s, '')"%elt)
                    tabelt = ",'~',".join(tabelt)
                    ## logger.warning("tabelt %s" % tabelt)
                    recherchefild = " AND ( concat(%s) like '%%%s%%')"% (tabelt, ctx['filter'])
                else:
                    #traitement des boolean posssible value
                    if ctx['field'] in ['need_reconf', 'kiosk_presence']:
                        reply = str(ctx['filter']).lower().strip()
                        if reply[0] in ['y', 'o', 't', 'v', '1' ]:
                            ctx['filter'] = '1'
                        elif reply[0] in ['n', 'f', '0' ]:
                            ctx['filter'] = '0'
                    if ctx['field'] in machinefield:
                        ctx['field'] = "mach.%s"%ctx['field']
                    elif ctx['field'] in entityfield:
                       ctx['field'] = "ent.%s"%entityfield[ctx['field']]
                    elif ctx['field'] in locationfield:
                       ctx['field'] = "loc.%s"%locationfield[ctx['field']]
                    if ctx['filter'].lower().strip() == "null":
                        recherchefild = " AND %s IS NULL "%ctx['field']
                    elif ctx['field'] in ['mach.id', 'mach.glpi_entity_id',
                                            'mach.glpi_location_id',
                                            'ent.glpi_id', 'loc.glpi_id']:
                        recherchefild = " AND %s = '%s'"% (ctx['field'], ctx['filter'])
                    else:
                        recherchefild = _likecriterium(ctx['field'], ctx['filter'])
        r=re.compile(r'reg_key_.*')
        regs=filter(r.search, self.config.summary)
        list_reg_columns_name = [getattr( self.config, regkey).split("|")[0].split("\\")[-1] \
                        for regkey in regs]
        entity = ""
        if 'location' in ctx and ctx['location'] != "":
            entity = " AND ent.glpi_id in (%s) "% str(ctx['location']).replace('UUID',"")

        computerpresence = ""
        if 'computerpresence' in ctx:
            if ctx['computerpresence'] == 'presence':
                computerpresence = " AND enabled > 0 "
            elif ctx['computerpresence'] == 'no_presence':
                computerpresence = " AND enabled = 0 "
        sql = """
                SELECT SQL_CALC_FOUND_ROWS
                    mach.*,
                    GROUP_CONCAT(DISTINCT CONCAT(reg.name, '|', reg.value)
                        SEPARATOR '@@@') AS regedit,
                    loc.name AS locationname,
                    loc.complete_name AS locationpath,
                    loc.glpi_id AS locationid,
                    ent.name AS entityname,
                    ent.complete_name AS entitypath,
                    ent.glpi_id AS entityid,
                    GROUP_CONCAT(DISTINCT IF( netw.ipaddress='', null,netw.ipaddress) SEPARATOR ',') AS listipadress,
                    GROUP_CONCAT(DISTINCT IF( netw.broadcast='', null,netw.broadcast) SEPARATOR ',') AS broadcast,
                    GROUP_CONCAT(DISTINCT IF( netw.gateway='', null,netw.gateway) SEPARATOR ',') AS gateway,
                    GROUP_CONCAT(DISTINCT IF( netw.mask='', null, netw.mask) SEPARATOR ',') AS mask
                FROM
                    xmppmaster.machines mach
                        LEFT OUTER JOIN
                    glpi_location loc ON loc.id = mach.glpi_location_id
                        LEFT OUTER JOIN
                    glpi_entity ent ON ent.id = mach.glpi_entity_id
                        LEFT OUTER JOIN
                    glpi_register_keys reg ON reg.machines_id = mach.id
                        LEFT OUTER JOIN
                    network netw ON  netw.machines_id = mach.id
                WHERE
                    agenttype LIKE 'm%%'%s%s%s
                GROUP BY mach.id
                limit %s, %s;""" % (computerpresence,
                                    entity,
                                    recherchefild,
                                    start,
                                    end)

        if debugfunction:
            logger.info("SQL request :  %s" % sql)

        result = session.execute(sql)
        result = session.execute(sql)
        sql_count = "SELECT FOUND_ROWS();"
        ret_count = session.execute(sql_count)
        count = ret_count.first()[0]
        session.commit()
        session.flush()
        ret = self.query_to_array_of_dict(result,bycolumn=True,
                                           listexclude=['picklekeypublic',
                                                        'urlguacamole'])
                                                        #'keysyncthing',
                                           #'glpi_location_id',
                                                        #'locationid',
                                                        #'locationpath',
                                                        #'locationname'
        ret['column'] = self.config.summary
        ret['list_reg_columns_name'] = list_reg_columns_name

        for columkeyreg in list_reg_columns_name:
            ret['data'][columkeyreg] =[]
            for stringkeyregistre in ret['data']['regedit'] :
                if stringkeyregistre == '':
                    ret['data'][columkeyreg].append('')
                else:
                    for strkeyvalue in stringkeyregistre.split('@@@'):
                        couplekeyvalue = strkeyvalue.split('|')
                        if len(couplekeyvalue) == 2:
                            if couplekeyvalue[0] == columkeyreg:
                                ret['data'][columkeyreg].append(couplekeyvalue[1])
        ret['total'] = count
        return ret


    @DatabaseHelper._sessionm
    def getPresenceuuid(self, session, uuid):
        machinespresente = session.query(Machines.uuid_inventorymachine).\
            filter(and_( Machines.uuid_inventorymachine == uuid,
                         Machines.enabled == '1')).first()
        session.commit()
        session.flush()
        if machinespresente :
            return True
        return False

    @DatabaseHelper._sessionm
    def getPresenceuuids(self, session, uuids):
        if isinstance(uuids, basestring):
            uuids=[uuids]
        result = { }
        for uuidmachine in uuids:
            result[uuidmachine] = False
        machinespresente = session.query(Machines.uuid_inventorymachine).\
            filter(and_(Machines.uuid_inventorymachine.in_(uuids),
                        Machines.enabled == '1')).all()
        session.commit()
        session.flush()
        for linemachine in machinespresente:
            result[linemachine.uuid_inventorymachine] = True
        return result

    @DatabaseHelper._sessionm
    def getPresenceExistuuids(self, session, uuids):
        if isinstance(uuids, basestring):
            uuids=[uuids]
        result = { }
        for uuidmachine in uuids:
            result[uuidmachine] = [0,0]
        machinespresente = session.query(Machines.uuid_inventorymachine,Machines.enabled).\
            filter(Machines.uuid_inventorymachine.in_(uuids)).all()
        session.commit()
        session.flush()
        for linemachine in machinespresente:
            out = 0;
            if linemachine.enabled == True:
                out = 1
            result[linemachine.uuid_inventorymachine] = [out, 1 ]
        return result

    @DatabaseHelper._sessionm
    def update_uuid_inventory(self, session, sql_id, uuid):
        """
        This function is used to update the uuid_inventorymachine value
        in the database for a specific machine.
        Args:
            session: The SQLAlchemy session
            sql_id: the id of the machine in the SQL database
            uuid: The uuid_inventorymachine of the machine
        Return:
           It returns None if it failed to update the machine uuid_inventorymachine.
        """
        try:
            sql = """UPDATE `xmppmaster`.`machines`
                    SET
                        `uuid_inventorymachine` = '%s'
                    WHERE
                        `id`  = %s;""" % (uuid, sql_id)
            result = session.execute(sql)
            session.commit()
            session.flush()
            return result
        except Exception as e:
            logging.getLogger().error("Function update_uuid_inventory")
            logging.getLogger().error("We got the error: %s" % str(e))
            return None

    #topology
    @DatabaseHelper._sessionm
    def listRS(self,session):
        """ return les RS pour le deploiement """
        sql = """SELECT DISTINCT
                    groupdeploy
                FROM
                    xmppmaster.machines
                WHERE
                    xmppmaster.machines.enabled = '1' and
                    xmppmaster.machines.agenttype="relayserver";"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        listrs = [x for x in result]
        return [ i[0] for i in listrs ]

    #topology
    @DatabaseHelper._sessionm
    def topologypulse(self, session):
        #listrs = self.listRS()
        ## select liste des RS
        #list des machines pour un relayserver

        sql = """SELECT groupdeploy,
                    GROUP_CONCAT(jid)
                FROM
                    xmppmaster.machines
                WHERE
                    xmppmaster.machines.enabled = '1' and
                    xmppmaster.machines.agenttype = 'machine'
                GROUP BY
                    groupdeploy;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        listmachinebyRS = [x for x in result]
        resulttopologie = {}
        for i in listmachinebyRS:
            listmachines = i[1].split(',')
            resulttopologie[i[0]] = listmachines
        self.write_topologyfile(resulttopologie)
        return [ resulttopologie]

    #topology
    def write_topologyfile(self, topology):
        directoryjson = os.path.join("/","usr","share","mmc","datatopology")
        if not os.path.isdir(directoryjson):
            #creation repertoire de json topology
            os.makedirs(directoryjson)
            os.chmod(directoryjson, 0o777) # for example
            uid, gid =  pwd.getpwnam('root').pw_uid, pwd.getpwnam('root').pw_gid
            os.chown(directoryjson, uid, gid) # set user:group as root:www-data
        # creation topology file.
        filename = "topology.json"
        pathfile =  os.path.join(directoryjson, filename)
        builddatajson = { "name" : "Pulse", "type" : "AMR", "parent": None, "children": []}
        for i in topology:
            listmachines = topology[i]

            ARS = {}
            ARS['name'] = i
            ARS['display_name'] = i.split("@")[0]
            ARS['type'] = "ARS"
            ARS['parent'] = "Pulse"
            ARS['children'] = []

            listmachinesstring = []
            for mach in listmachines:
                ARS['children'].append({ "name" : mach,
                'display_name': mach.split(".")[0],
                "type" : "AM", "parent" : i })
            #builddatajson[i] = listmachinesstring
            #ARS['children'] = builddatajson
            #print listmachinesstring
            builddatajson['children'].append(ARS)
        #import pprint
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(builddatajson)

        with open(pathfile, 'w') as outfile:
            json.dump(builddatajson,  outfile, indent = 4)
        os.chmod(pathfile, 0o777)
        uid, gid =  pwd.getpwnam('root').pw_uid, pwd.getpwnam('root').pw_gid
        os.chown(pathfile, uid, gid)

    @DatabaseHelper._sessionm
    def getstepdeployinsession(self, session, sessiondeploy):
        sql = """
                SELECT
            date, text
        FROM
            xmppmaster.logs
        WHERE
            type = 'deploy'
                AND sessionname = '%s'
        ORDER BY id;""" % (sessiondeploy)
        step = session.execute(sql)
        session.commit()
        session.flush()
        step
        #return [x for x in step]
        try:
            a=[]
            for t in step:
                a.append ({'date':t[0],'text':t[1] })
            return a
        except:
            return []

    @DatabaseHelper._sessionm
    def getlistPresenceMachineid(self, session, format=False):
        sql = """SELECT
                    uuid_inventorymachine
                 FROM
                    xmppmaster.machines
                 WHERE
                    enabled = '1' and
                    agenttype = 'machine' and (uuid_inventorymachine IS NOT NULL OR uuid_inventorymachine!='');"""

        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a=[]
            for t in presencelist:
                a.append(t[0])
            return a
        except:
            return a

    @DatabaseHelper._sessionm
    def getidlistPresenceMachine(self, session, presence=None):
        """
        This function is used to retrieve the list of the machines based on the 'presence' argument.

        Args:
            session: The SQLAlchemy session
            presence: if True, it returns the list of the machine with an agent up.
                      if False, it returns the list of the machine with an agent down.
                      if None, it returns the list with all the machines.
        Returns:
            It returns the list of the machine based on the 'presence' argument.
        """
        strpresence = ""

        try:
            if presence is not None:
                if presence == True:
                    strpresence = " and enabled = 1"
                else:
                    strpresence = " and enabled = 0"
            sql = """SELECT
                        SUBSTR(uuid_inventorymachine, 5)
                    FROM
                        xmppmaster.machines
                    WHERE
                        agenttype = 'machine'
                    and
                        uuid_inventorymachine IS NOT NULL %s;""" % strpresence
            presencelist = session.execute(sql)
            session.commit()
            session.flush()
            return [ x[0] for x in  presencelist ]
        except Exception as e:
            logging.getLogger().error("Error debug for the getidlistPresenceMachine function!")
            logging.getLogger().error("The presence of the machine is:  %s" % presence)
            logging.getLogger().error("The sql error is: %s" % sql)
            logging.getLogger().error("the Exception catched is %s" % str(e))
            return []

    @DatabaseHelper._sessionm
    def getxmppmasterfilterforglpi(self, session, listqueryxmppmaster = None):
        fl = listqueryxmppmaster[3].replace('*',"%")
        if listqueryxmppmaster[2] == "OU user":
            machineid = session.query(Organization_ad.id_inventory)
            machineid = machineid.filter(Organization_ad.ouuser.like(fl))
        elif listqueryxmppmaster[2] == "OU machine":
            machineid = session.query(Organization_ad.id_inventory)
            machineid = machineid.filter(Organization_ad.oumachine.like(fl))
        elif listqueryxmppmaster[2] == "Online computer":
            d = XmppMasterDatabase().getlistPresenceMachineid()
            listid = [x.replace("UUID", "") for x in d]
            return listid
        machineid = machineid.all()
        session.commit()
        session.flush()
        ret = [str(m.id_inventory) for m in machineid]
        return ret


    @DatabaseHelper._sessionm
    def getListPresenceMachine(self, session):
        sql = """SELECT
                    jid, agenttype, hostname, uuid_inventorymachine
                 FROM
                    xmppmaster.machines
                 WHERE
                    enabled = '1' and
                    agenttype='machine' and uuid_inventorymachine IS NOT NULL;"""

        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a=[]
            for t in presencelist:
                a.append({'jid':t[0],
                          'type': t[1],
                          'hostname':t[2],
                          'uuid_inventorymachine':t[3]})
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def getListPresenceMachineWithKiosk(self, session):
        sql = """SELECT
                    *
                 FROM
                    xmppmaster.machines
                 WHERE
                    enabled = '1' and
                    agenttype='machine' and uuid_inventorymachine IS NOT NULL ;"""

        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a=[]
            for t in presencelist:
                a.append({'id':t[0],'jid': t[1], 'platform':t[2], \
                    'hostname': t[4], 'uuid_inventorymachine':t[5], \
                    'agenttype':t[10], 'classutil': t[11]})
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def changStatusPresenceMachine(self, session, jid, enable = '0'):
        """
            update presence machine in table machine.
        """
        machine = session.query(Machines).filter( Machines.jid == jid)
        if machine:
            machine.enabled = "%s"%enable
            session.commit()
            session.flush()
        else:
            logger.warning("xmpp signal changement status on machine no exist %s" % jid)

    @DatabaseHelper._sessionm
    def delMachineXmppPresence(self, session, uuidinventory):
        """
            del machine of table machine
        """
        result = ['-1']
        typemachine = "machine"
        try:
            sql = """SELECT
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.uuid_inventorymachine = '%s';""" % uuidinventory
            id = session.execute(sql)
            session.commit()
            session.flush()
            result=[x for x in id][0]
            sql  = """DELETE FROM `xmppmaster`.`machines`
                    WHERE
                        `xmppmaster`.`machines`.`id` = '%s';""" % result[0]
            if result[2] == "relayserver":
                typemachine = "relayserver"
                sql2 = """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';""" % result[1]
                session.execute(sql2)
            session.execute(sql)
            session.commit()
            session.flush()
        except IndexError:
            logging.getLogger().warning("Configuration agent machine uuidglpi [%s]. no uuid in base for configuration" % uuidinventory)
            return {}
        except Exception, e:
            logging.getLogger().error(str(e))
            return {}
        resulttypemachine={"type" : typemachine }
        return resulttypemachine

    @DatabaseHelper._sessionm
    def SetPresenceMachine(self, session, jid, presence=0):
        """
            chang presence in table machines
        """
        user = str(jid).split("@")[0]
        try:
            sql = """UPDATE
                        `xmppmaster`.`machines`
                    SET
                        `xmppmaster`.`machines`.`enabled` = '%s'
                    WHERE
                        `xmppmaster`.`machines`.jid like('%s@%%');""" % (presence, user)
            session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception, e:
            logging.getLogger().error("SetPresenceMachine : %s" % str(e))
            return False

    @DatabaseHelper._sessionm
    def updatedeployresultandstate(self, session, sessionid, state, result ):
            jsonresult = json.loads(result)
            jsonautre = copy.deepcopy(jsonresult)
            del (jsonautre['descriptor'])
            del (jsonautre['packagefile'])
            #DEPLOYMENT START
            try:
                deploysession = session.query(Deploy).filter(Deploy.sessionid == sessionid).one()
                if deploysession:
                    if deploysession.result is None or \
                        ("wol" in jsonresult and \
                            jsonresult['wol']  == 1 ) or \
                        ("advanced" in jsonresult and \
                            'syncthing' in jsonresult['advanced'] and \
                                jsonresult['advanced']['syncthing'] == 1):
                        jsonbase = {
                                    "infoslist": [jsonresult['descriptor']['info']],
                                    "descriptorslist": [jsonresult['descriptor']['sequence']],
                                    "otherinfos": [jsonautre],
                                    "title": deploysession.title,
                                    "session": deploysession.sessionid,
                                    "macadress": deploysession.macadress,
                                    "user": deploysession.login
                        }
                    else:
                        jsonbase = json.loads(deploysession.result)
                        jsonbase['infoslist'].append(jsonresult['descriptor']['info'])
                        jsonbase['descriptorslist'].append(jsonresult['descriptor']['sequence'])
                        jsonbase['otherinfos'].append(jsonautre)
                    deploysession.result = json.dumps(jsonbase, indent=3)
                    if 'infoslist' in jsonbase and \
                        'otherinfos' in jsonbase and \
                        jsonbase['otherinfos'] and \
                        'plan' in jsonbase['otherinfos'][0] and \
                            len(jsonbase['infoslist']) != len(jsonbase['otherinfos'][0]['plan']) and \
                            state == "DEPLOYMENT SUCCESS":
                        state = "DEPLOYMENT PARTIAL SUCCESS"
                    regexpexlusion = re.compile("^(?!abort)^(?!success)^(?!error)",re.IGNORECASE)
                    if regexpexlusion.match(state) is not None:
                        deploysession.state = state
                session.commit()
                session.flush()
                session.close()
                return 1
            except Exception, e:
                self.logger.error(str(e))
                self.logger.error("\n%s" % (traceback.format_exc()))
                return -1

    @DatabaseHelper._sessionm
    def substituteinfo(self, session, listconfsubstitute, arsname):
        """
            search  subtitute agent jid for agent machine
        """
        try:
            exclud = 'master@pulse'

            incrementeiscount=[]
            for t in listconfsubstitute['conflist']:
                result = session.query(Substituteconf.id.label("id"),
                                       Substituteconf.jidsubtitute.label("jidsubtitute"),
                                       Substituteconf.countsub.label("countsub"),
                                       RelayServer.jid.label("namerelayser")).\
                    join(RelayServer, Substituteconf.relayserver_id == RelayServer.id).\
                        filter( and_(not_(Substituteconf.jidsubtitute.like(exclud)),
                                    Substituteconf.type.like(t),
                                    RelayServer.jid == arsname)).order_by(Substituteconf.countsub).all()
                listcommand = []
                test = False
                for y in result:
                    listcommand.append(y.jidsubtitute)
                    if not test:
                        test = True
                        incrementeiscount.append(str(y.id))
                listcommand.append(exclud)
                listconfsubstitute[t] = listcommand
            if incrementeiscount:
                # update contsub
                sql="""UPDATE `xmppmaster`.`substituteconf`
                    SET
                        `countsub` = `countsub` + '1'
                    WHERE
                        `id` IN (%s);""" % ','.join([x for x in incrementeiscount])
                result = session.execute(sql)
                session.commit()
                session.flush()
        except Exception, e:
            logging.getLogger().error("substituteinfo : %s" % str(e))
        return listconfsubstitute

    @DatabaseHelper._sessionm
    def GetMachine(self, session, jid):
        """
            Initialize boolean presence in table machines
        """
        user = str(jid).split("@")[0]
        try:
            sql = """SELECT
                        id, hostname, agenttype, need_reconf
                    FROM
                        `xmppmaster`.`machines`
                    WHERE
                        `xmppmaster`.`machines`.jid like('%s@%%')
                    LIMIT 1;""" % user
            result = session.execute(sql)
            session.commit()
            session.flush()
            return [x for x in result][0]
        except IndexError:
            return None
        except Exception, e:
            logging.getLogger().error("GetMachine : %s" % str(e))
            return None

    @DatabaseHelper._sessionm
    def updateMachinereconf(self, session, jid, status=0):
        """
            update boolean need_reconf in table machines
        """
        user = str(jid).split("@")[0]
        try:
            sql = """UPDATE `xmppmaster`.`machines`
                         SET `need_reconf` = '%s'
                     WHERE
                         `xmppmaster`.`machines`.jid like('%s@%%')""" % (status,
                                                                       user)
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception, e:
            logging.getLogger().error("updateMachinereconf : %s" % str(e))
            return False

    @DatabaseHelper._sessionm
    def initialisePresenceMachine(self, session, jid, presence=0):
        """
            Initialize presence in table machines and relay
        """
        mach = self.GetMachine(jid)
        if mach is not None:
            self.SetPresenceMachine(jid, presence)
            if mach[2] != "machine":
                try:
                    sql = """UPDATE
                                `xmppmaster`.`relayserver`
                            SET
                                `xmppmaster`.`relayserver`.`enabled` = '%s'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';""" % (presence, mach[1])
                    session.execute(sql)
                    session.commit()
                    session.flush()
                except Exception, e:
                    logging.getLogger().error("initialisePresenceMachine : %s" % str(e))
                finally:
                    return {"type": "relayserver", "reconf": mach[3]}
            else:
                return {"type": "machine", "reconf": mach[3]}
        else:
            return {}

    @DatabaseHelper._sessionm
    def update_Presence_Relay(self, session, jid, presence=0):
        """
            Update the presence in the relay and machine SQL Tables
            Args:
                session: The SQL Alchemy session
                jid: jid of the relay to update
                presence: Availability of the relay
                          0: Set the relay as offline
                          1: Set the relay as online
        """
        try:
            user = str(jid).split("@")[0]
            sql = """UPDATE
                        `xmppmaster`.`machines`
                    SET
                        `enabled` = '%s'
                    WHERE
                        `xmppmaster`.`machines`.`jid` like('%s@%%');""" % (presence,
                                                                           user)
            session.execute(sql)
            sql = """UPDATE
                        `xmppmaster`.`relayserver`
                    SET
                        `enabled` = '%s'
                    WHERE
                        `xmppmaster`.`relayserver`.`jid` like('%s@%%');""" % (presence,
                                                                              user)
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().error("\n%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def update_reconf_mach_of_Relay_down(self, session, jid, reconf=1):
        """
            renitialise remote configuration
        """
        try:
            user = str(jid).split("@")[0]
            sql = """UPDATE
                        `xmppmaster`.`machines`
                     SET
                        `need_reconf` = '%s'
                     WHERE
                        `xmppmaster`.`machines`.`agenttype` like ("machine")
                        AND
                        `xmppmaster`.`machines`.`groupdeploy` like('%s@%%');""" % (reconf,
                                                                           user)
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().error("\n%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def delPresenceMachine(self, session, jid):
        """
            del machine of table machines
        """
        result = ['-1']
        typemachine = "machine"
        try:
            sql = """SELECT
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.jid = '%s';""" % jid
            id = session.execute(sql)
            session.commit()
            session.flush()
            result=[x for x in id][0]
            sql  = """DELETE FROM `xmppmaster`.`machines`
                    WHERE
                        `xmppmaster`.`machines`.`id` = '%s';""" % result[0]
            if result[2] == "relayserver":
                typemachine = "relayserver"
                sql2 = """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';""" % result[1]
                session.execute(sql2)
            session.execute(sql)
            session.commit()
            session.flush()
        except IndexError:
            logging.getLogger().warning("Configuration agent machine jid [%s]. no jid in base for configuration" % jid)
            return {}
        except Exception, e:
            logging.getLogger().error(str(e))
            return {}
        resulttypemachine = {"type": typemachine}
        return resulttypemachine

    @DatabaseHelper._sessionm
    def getPresencejiduser(self, session, jiduser, enable = "1"):
        """
            presence machine for jid user  ...@
        """
        machine = session.query(Machines).\
            filter(and_(Machines.jid.like('%s@%%' % (jiduser)),\
                        Machines.enabled == "%s" % enable)).first()
        session.commit()
        session.flush()
        if machine is None:
            return False
        return True

    @DatabaseHelper._sessionm
    def delPresenceMachinebyjiduser(self, session, jiduser):
        """
            del machine of table machines
        """
        result = ['-1']
        typemachine = "machine"
        try:
            sql = """SELECT
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.jid like('%s@%%');""" % jiduser
            id = session.execute(sql)
            session.commit()
            session.flush()
            result=[x for x in id][0]
            sql  = """DELETE FROM `xmppmaster`.`machines`
                    WHERE
                        `xmppmaster`.`machines`.`id` = '%s';""" % result[0]
            if result[2] == "relayserver":
                typemachine = "relayserver"
                sql2 = """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';""" % result[1]
                session.execute(sql2)
            session.execute(sql)
            session.commit()
            session.flush()
        except IndexError:
            logging.getLogger().warning("Configuration agent machine jid [%s]. no jid in base for configuration" % jiduser)
            return {}
        except Exception, e:
            logging.getLogger().error(str(e))
            return {}
        resulttypemachine = {"type": typemachine}
        return resulttypemachine

    @DatabaseHelper._sessionm
    def search_machines_from_state(self, session, state):
        dateend = datetime.now()
        sql= """SELECT
                    *
                FROM
                    xmppmaster.deploy
                WHERE
                    state LIKE '%s%%' AND
                    '%s' BETWEEN startcmd AND
                    endcmd;""" % (state, dateend)
        machines = session.execute(sql)
        session.commit()
        session.flush()
        result =  [x for x in machines]
        resultlist = []
        for t in result:
            listresult = {"id": t[0],
                          "title": t[1],
                          "jidmachine": t[2],
                          "jid_relay": t[3],
                          "pathpackage": t[4],
                          "state": t[5],
                          "sessionid": t[6],
                          "start": str(t[7]),
                          "startcmd": str(t[8]),
                          "endcmd": str(t[9]),
                          "inventoryuuid": t[10],
                          "host": t[11],
                          "user": t[12],
                          "command": t[13],
                          "group_uuid": t[14],
                          "login": t[15],
                          "macadress": t[16],
                          "syncthing": t[17],
                          "result": t[18]}
            resultlist.append(listresult)
        return resultlist

    @DatabaseHelper._sessionm
    def Timeouterrordeploy(self, session):
        ### test les evenements states qui ne sont plus valides sur intervalle de deployement.
        Stateforupdateontimeout=["'WOL 1'",
                                 "'WOL 2'",
                                 "'WOL 3'",
                                 "'WAITING MACHINE ONLINE'",
                                 "'DEPLOYMENT START'",
                                 "'WAITING REBOOT'",
                                 "'DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)'",
                                 "'Offline'"]

        nowdate = datetime.now()
        set_search =','.join(Stateforupdateontimeout)

        # reprise code ici
        try:
            sql= """SELECT
                        *
                    FROM
                        xmppmaster.deploy
                    WHERE
                        state in (%s) AND
                        '%s' > endcmd;""" % (set_search, nowdate)
            machines = session.execute(sql)
            session.commit()
            session.flush()
            result =  [x for x in machines]
            resultlist = []
            for t in result:
                self.update_state_deploy( t[0], 'ABORT ON TIMEOUT')
                listresult = {"id": t[0],
                              "title": t[1],
                              "jidmachine": t[2],
                              "jid_relay": t[3],
                              "pathpackage": t[4],
                              "state": t[5],
                              "sessionid": t[6],
                              "start": str(t[7]),
                              "startcmd": str(t[8]),
                              "endcmd": str(t[9]),
                              "inventoryuuid": t[10],
                              "host": t[11],
                              "user": t[12],
                              "command": t[13],
                              "group_uuid": t[14],
                              "login": t[15],
                              "macadress": t[16],
                              "syncthing": t[17],
                              "result": t[18]}
                resultlist.append(listresult)
            return resultlist
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().error("fn Timeouterrordeploy on sql %s"(sql))
            return resultlist

    @DatabaseHelper._sessionm
    def update_state_deploy(self, session, id, state):
        try:
            sql = """UPDATE `xmppmaster`.`deploy`
                     SET `state`='%s'
                     WHERE `id`='%s';""" % (state, id)
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def updatedeploytosessionid(self, session, status, sessionid):
        try:
            sql = """UPDATE `xmppmaster`.`deploy`
                     SET `state`='%s'
                     WHERE `sessionid`='%s';""" % (status, sessionid)
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def updatedeploytosyncthing(self, session, sessionid, syncthing=1):
        try:
            sql = """UPDATE `xmppmaster`.`deploy`
                     SET `syncthing`='%s'
                     WHERE `sessionid`='%s';""" % (syncthing, sessionid)
            #print sql
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def nbsyncthingdeploy(self, session, grp, cmd):
        try:
            sql = """SELECT
                        COUNT(*) as nb
                    FROM
                        deploy
                    WHERE
                        group_uuid = %s AND command = %s
                            AND syncthing > 1;""" % (grp, cmd)
            req = session.execute(sql)
            session.commit()
            session.flush()
            ret=[elt for elt in req]
            return ret[0][0]
        except Exception, e:
            logging.getLogger().error(str(e))
            return 0

    @DatabaseHelper._sessionm
    def getPresencejiduser(self, session, userjid):
        user = str(userjid).split("@")[0]
        sql = """SELECT COUNT(jid) AS nb
            FROM
                 xmppmaster.machines
             WHERE
              jid LIKE ('%s%%');""" % (user)
        presencejid = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in presencejid]
        if ret[0] == 0:
            return False
        return True

    @DatabaseHelper._sessionm
    def getMachinedeployexistonHostname(self, session, hostname):
        """
        This function is used to find all the machines based on the hostname
        Args:
            session: The SQLAlchemy session
            hostname: The hostname we are searching

        Returns:
            It returns the list of the machines with the searched hostname
        """
        machinesexits = []
        try:
            sql="""SELECT
                    machines.id AS id,
                    machines.uuid_inventorymachine AS uuid,
                    machines.uuid_serial_machine AS serial,
                    GROUP_CONCAT(network.mac) AS macs
                FROM
                    xmppmaster.machines
                        JOIN
                    xmppmaster.network ON machines.id = network.machines_id
                WHERE
                    machines.agenttype = 'machine'
                        AND machines.hostname LIKE '%s'
                GROUP BY machines.id;""" % hostname.strip()
            machines = session.execute(sql)
        except Exception as e:
            logging.getLogger().error("The hostname is: %s" % str(e))
            logging.getLogger().error("We encountered the error: %s" % str(e))
            return machinesexits

        for machine in machines:
            mach = {'id':  machine.id,
                    'uuid': machine.uuid,
                    'macs': machine.macs,
                    'serial': machine.serial}
            machinesexits.append(mach)
        return machinesexits

    @DatabaseHelper._sessionm
    def getMachineHostname(self, session, hostname):
        try:
            machine = session.query(Machines.id,
                                    Machines.uuid_inventorymachine).\
                                        filter(Machines.hostname == hostname).first()
            session.commit()
            session.flush()
            if machine:
                return {"id": machine.id,
                        "uuid_inventorymachine": machine.uuid_inventorymachine}
        except Exception as e:
            logging.getLogger().error("function getMachineHostname %s" % str(e))

        return {}

    @DatabaseHelper._sessionm
    def getGuacamoleRelayServerMachineHostname(self, session, hostname,
                                               enable = 1, agenttype="machine"):
        querymachine = session.query(Machines)
        if enable == None:
            querymachine = querymachine.filter(Machines.hostname == hostname)
        else:
            querymachine = querymachine.filter(and_(Machines.hostname == hostname,
                                                    Machines.enabled == enable,
                                                    Machines.agenttype == agenttype))
        machine = querymachine.one()
        session.commit()
        session.flush()
        try:
            result = {"uuid": machine.uuid_inventorymachine,
                      "jid": machine.jid,
                      "groupdeploy": machine.groupdeploy,
                      "urlguacamole": machine.urlguacamole,
                      "subnetxmpp": machine.subnetxmpp,
                      "hostname": machine.hostname,
                      "platform": machine.platform,
                      "macaddress": machine.macaddress,
                      "archi": machine.archi,
                      "uuid_inventorymachine": machine.uuid_inventorymachine,
                      "ip_xmpp": machine.ip_xmpp,
                      "agenttype": machine.agenttype,
                      "keysyncthing":  machine.keysyncthing,
                      "enabled": machine.enabled
                        }
            for i in result:
                if result[i] == None:
                    result[i] = ""
        except Exception:
            result = {"uuid": -1,
                      "jid": "",
                      "groupdeploy": "",
                      "urlguacamole": "",
                      "subnetxmpp": "",
                      "hostname": "",
                      "platform": "",
                      "macaddress": "",
                      "archi": "",
                      "uuid_inventorymachine": "",
                      "ip_xmpp": "",
                      "agenttype": "",
                      "keysyncthing":  "",
                      "enabled": 0
                    }
        return result

    @DatabaseHelper._sessionm
    def getGuacamoleRelayServerMachineUuid(self, session, uuid, enable = 1):
        querymachine = session.query(Machines)
        if enable == None:
            querymachine = querymachine.filter(Machines.uuid_inventorymachine == uuid)
        else:
            querymachine = querymachine.filter(and_(Machines.uuid_inventorymachine == uuid,
                                                    Machines.enabled == enable))
        machine = querymachine.one()
        session.commit()
        session.flush()
        try:
            result = {
                        "uuid": uuid,
                        "jid": machine.jid,
                        "groupdeploy": machine.groupdeploy,
                        "urlguacamole": machine.urlguacamole,
                        "subnetxmpp": machine.subnetxmpp,
                        "hostname": machine.hostname,
                        "platform": machine.platform,
                        "macaddress": machine.macaddress,
                        "archi": machine.archi,
                        "uuid_inventorymachine": machine.uuid_inventorymachine,
                        "ip_xmpp": machine.ip_xmpp,
                        "agenttype": machine.agenttype,
                        "keysyncthing":  machine.keysyncthing,
                        "enabled": machine.enabled
                        }
            for i in result:
                if result[i] == None:
                    result[i] = ""
        except Exception:
            result = {
                        "uuid": uuid,
                        "jid": "",
                        "groupdeploy": "",
                        "urlguacamole": "",
                        "subnetxmpp": "",
                        "hostname": "",
                        "platform": "",
                        "macaddress": "",
                        "archi": "",
                        "uuid_inventorymachine": "",
                        "ip_xmpp": "",
                        "agenttype": "",
                        "keysyncthing":  "",
                        "enabled": 0
                    }
        return result

    @DatabaseHelper._sessionm
    def getGuacamoleidforUuid(self, session, uuid, existtest = None):
        """
            if existtest is None
             this function return the list of protocole for 1 machine
             if existtest is not None:
             this function return True if guacamole is configured
             or false si guacamole is not configued.
        """
        if existtest is None:
            ret=session.query(Has_guacamole.idguacamole,Has_guacamole.protocol).\
                filter(and_(Has_guacamole.idinventory == uuid.replace('UUID',''),
                            Has_guacamole.protocol != "INF")).all()
            session.commit()
            session.flush()
            if ret:
                return [(m[1],m[0]) for m in ret]
            else:
                return []
        else:
            ret=session.query(Has_guacamole.idguacamole).\
                filter(Has_guacamole.idinventory == uuid.replace('UUID','')).first()
            if ret:
                return True
            return False

    @DatabaseHelper._sessionm
    def getGuacamoleIdForHostname(self, session, host, existtest = None):
        """
            if existtest is None
             this function return the list of protocole for 1 machine
             if existtest is not None:
             this function return True if guacamole is configured
             or false si guacamole is not configued.
        """
        if existtest is None:
            protocole = session.query(Has_guacamole.idguacamole,Has_guacamole.protocol).\
                    join(Machines, Machines.id == Has_guacamole.machine_id)
            protocole = protocole.filter(and_(Has_guacamole.protocol != "INF",
                                          Machines.hostname == host))
            protocole = protocole.all()
            session.commit()
            session.flush()
            if protocole:
                return [(m[1],m[0]) for m in protocole]
            else:
                return []
        else:
            protocole = session.query(Has_guacamole.idguacamole).\
                    join(Machines, Machines.id == Has_guacamole.machine_id)
            protocole = protocole.filter(Machines.hostname == host)

            protocole = protocole.first()
            if protocole:
                return True
            return False

    @DatabaseHelper._sessionm
    def isMachineExistPresentTFN(self, session, jid):
        """
            This function is used to determine if a machine exist and is online.

            Args:
                session:    Sqlalchemy session
                jid:        Jid of the machine we are testing

            Returns:
                It returns None if the machine does not exists in pulse machine database
                It returns True if the machines exists in pulse machine database and is online
                It returns False if the machines exists in pulse machine database and is offline
        """
        machine = session.query(Machines).filter(and_(Machines.jid == jid)).first()
        if machine:
            if machine.enabled == '0':
                return False

            return True

        return None

    @DatabaseHelper._sessionm
    def getPresencejid(self, session, jid, eanable = 1):
        machine = session.query(Machines).filter(and_(Machines.jid == jid,
                                                      Machines.enabled == eanable)).first()
        session.commit()
        session.flush()
        if machine is None:
            return False
        return True

    @DatabaseHelper._sessionm
    def getMachinefromjid(self, session, jid):
        """ information machine"""
        user = str(jid).split("@")[0]
        machine = session.query(Machines).filter(Machines.jid.like("%s%%" % user)).first()
        session.commit()
        session.flush()
        result = {}
        if machine:
            result = {"id": machine.id,
                      "jid": machine.jid,
                      "platform": machine.platform,
                      "archi": machine.archi,
                      "hostname": machine.hostname,
                      "uuid_inventorymachine": machine.uuid_inventorymachine,
                      "ip_xmpp": machine.ip_xmpp,
                      "ippublic": machine.ippublic,
                      "macaddress": machine.macaddress,
                      "subnetxmpp": machine.subnetxmpp,
                      "agenttype": machine.agenttype,
                      "classutil": machine.classutil,
                      "groupdeploy": machine.groupdeploy,
                      "urlguacamole": machine.urlguacamole,
                      "picklekeypublic": machine.picklekeypublic,
                      'ad_ou_user': machine.ad_ou_user,
                      'ad_ou_machine': machine.ad_ou_machine,
                      'kiosk_presence': machine.kiosk_presence,
                      'lastuser': machine.lastuser,
                      'keysyncthing': machine.keysyncthing,
                      'enabled': machine.enabled,
                      'uuid_serial_machine': machine.uuid_serial_machine}
        return result

    @DatabaseHelper._sessionm
    def getMachinefromuuid(self, session, uuid):
        """ information machine """
        machine = session.query(Machines).filter(Machines.uuid_inventorymachine == uuid).first()
        session.commit()
        session.flush()
        result = {}
        if machine:
            result = {"id": machine.id,
                      "jid": machine.jid,
                      "platform": machine.platform,
                      "archi": machine.archi,
                      "hostname": machine.hostname,
                      "uuid_inventorymachine": machine.uuid_inventorymachine,
                      "ip_xmpp": machine.ip_xmpp,
                      "ippublic": machine.ippublic,
                      "macaddress": machine.macaddress,
                      "subnetxmpp": machine.subnetxmpp,
                      "agenttype": machine.agenttype,
                      "classutil": machine.classutil,
                      "groupdeploy": machine.groupdeploy,
                      "urlguacamole": machine.urlguacamole,
                      "picklekeypublic": machine.picklekeypublic,
                      'ad_ou_user': machine.ad_ou_user,
                      'ad_ou_machine': machine.ad_ou_machine,
                      'kiosk_presence': machine.kiosk_presence,
                      'lastuser': machine.lastuser,
                      'enabled': machine.enabled,
                      'uuid_serial_machine': machine.uuid_serial_machine}
        return result

    @DatabaseHelper._sessionm
    def getRelayServerfromjid(self, session, jid):
        relayserver = session.query(RelayServer).filter(RelayServer.jid.like("%s%%" % jid))
        relayserver = relayserver.first()
        session.commit()
        session.flush()
        try:
            result = {'id':  relayserver.id,
                      'urlguacamole': relayserver.urlguacamole,
                      'subnet': relayserver.subnet,
                      'nameserver': relayserver.nameserver,
                      'ipserver': relayserver.ipserver,
                      'ipconnection': relayserver.ipconnection,
                      'port': relayserver.port,
                      'portconnection': relayserver.portconnection,
                      'mask': relayserver.mask,
                      'jid': relayserver.jid,
                      'longitude': relayserver.longitude,
                      'latitude': relayserver.latitude,
                      'enabled': relayserver.enabled,
                      'switchonoff': relayserver.switchonoff,
                      'mandatory': relayserver.mandatory,
                      'classutil': relayserver.classutil,
                      'groupdeploy': relayserver.groupdeploy,
                      'package_server_ip': relayserver.package_server_ip,
                      'package_server_port': relayserver.package_server_port,
                      'moderelayserver': relayserver.moderelayserver,
                      'keysyncthing': relayserver.keysyncthing,
                      'syncthing_port': relayserver.syncthing_port
            }
        except Exception:
            result = {}
        return result


    @DatabaseHelper._sessionm
    def getRelayServerForMachineUuid(self, session, uuid):
        relayserver = session.query(Machines).filter(Machines.uuid_inventorymachine == uuid).one()
        session.commit()
        session.flush()
        try:
            result = {
                        "uuid": uuid,
                        "jid": relayserver.groupdeploy
                        }
            for i in result:
                if result[i] == None:
                    result[i] = ""
        except Exception:
            result = {
                        "uuid": uuid,
                        "jid": ""
                    }
        return result

    @DatabaseHelper._sessionm
    def getCountOnlineMachine(self, session):
        return session.query(func.count(Machines.id)).\
            filter(and_(Machines.agenttype == "machine",
                        Machines.enabled == "1")).scalar()

    @DatabaseHelper._sessionm
    def getRelayServerofclusterFromjidars(self, session, jid, moderelayserver=None, enablears=1):
        #determine ARS id from jid
        relayserver = session.query(RelayServer).filter(RelayServer.jid == jid)
        relayserver = relayserver.first()
        session.commit()
        session.flush()
        if relayserver:
            #object complete
            notconfars = {relayserver.jid: [relayserver.ipconnection,
                                            relayserver.port,
                                            relayserver.jid,
                                            relayserver.urlguacamole,
                                            0,
                                            relayserver.syncthing_port]}
            # search for clusters where ARS is
            clustersid = session.query(Has_cluster_ars).filter(Has_cluster_ars.id_ars == relayserver.id)
            clustersid = clustersid.all()
            session.commit()
            session.flush()
            #search the ARS in the same cluster that ARS finds
            if clustersid:
                listcluster_id = [m.id_cluster for m in clustersid]
                ars = session.query(RelayServer).\
                    join(Has_cluster_ars, Has_cluster_ars.id_ars == RelayServer.id).\
                        join(Cluster_ars, Has_cluster_ars.id_cluster == Cluster_ars.id)
                ars = ars.filter(Has_cluster_ars.id_cluster.in_(listcluster_id))
                if moderelayserver != None:
                    ars = ars.filter(RelayServer.moderelayserver == moderelayserver)
                if enablears != None:
                    ars = ars.filter(RelayServer.enabled == enablears)
                ars = ars.all()
                session.commit()
                session.flush()
                if ars:
                    #result1 = [(m.ipconnection,m.port,m.jid,m.urlguacamole)for m in ars]
                    try:
                        result2 = {m.jid: [m.ipconnection,
                                           m.port,
                                           m.jid,
                                           m.urlguacamole,
                                           0,
                                           m.keysyncthing,
                                           m.syncthing_port] for m in ars}
                    except Exception:
                        result2 = {m.jid: [m.ipconnection,
                                           m.port,
                                           m.jid,
                                           m.urlguacamole,
                                           0,
                                           "",
                                           0] for m in ars}
                    countarsclient = self.algoloadbalancerforcluster()
                    if countarsclient:
                        for i in countarsclient:
                            try:
                                if result2[i[1]]:
                                    result2[i[1]][4] = i[0]
                            except KeyError:
                                pass
                    return result2
            else:
                # there are no clusters configured for this ARS.
                logging.getLogger().warning("Cluster ARS [%s] no configured" % relayserver.jid)
                return notconfars
        else:
            logging.getLogger().warning("Relay server no present")
            logging.getLogger().warning("ARS not known for machine")
        return {}


    @DatabaseHelper._sessionm
    def algoloadbalancerforcluster(self, session):
        sql = """
            SELECT
                COUNT(*) AS nb, `machines`.`groupdeploy`
            FROM
                xmppmaster.machines
            WHERE
                enabled = '1' and
                agenttype = 'machine'
            GROUP BY `machines`.`groupdeploy`
            ORDER BY nb DESC;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def get_machine_ad_infos(self, session, uuid_inventory):
        """
        Select the founded OUs of the logged machine.
        Param:
            uuid_inventory: str. This param is the uuid of the inventory of the machine received by xmpp.

        Returns:
            List of tuple. The tuple contains all the ou_machine and ou_user founded.
        """

        sql = """
        SELECT
            ad_ou_machine, ad_ou_user
        FROM
            machines
        WHERE
            enabled = '1' and
            uuid_inventorymachine = '%s';""" % (uuid_inventory)

        result = session.execute(sql)
        session.commit()
        session.flush()
        return [element for element in result]

    @DatabaseHelper._sessionm
    def get_machines_with_kiosk(self, session):
        """
        Select the machines with the kiosk installed.
        Returns:
            List of tuple. The tuple contains all the machines founded.
        """

        sql = """
        SELECT
            *
        FROM
            machines
        WHERE
            enabled = '1' and
            kiosk_presence = 'True';"""
        result = session.execute(sql)
        session.commit()
        session.flush()

        return [element for element in result]

    @DatabaseHelper._sessionm
    def get_machines_online_for_dashboard(self, session):
        ret = session.query(Machines.uuid_inventorymachine,
                            Machines.macaddress).filter(and_(Machines.agenttype != "relayserver",
                                                             Machines.enabled == '1')).all()

        if ret is None:
            ret = []
        else:
            ret = [{'uuid': machine[0], 'macaddress': machine[1]} for machine in ret]
        return ret

    @DatabaseHelper._sessionm
    def get_syncthing_deploy_to_clean(self, session):
        sql="""
    SELECT
        distinct xmppmaster.syncthing_deploy_group.id,
        GROUP_CONCAT(xmppmaster.syncthing_machine.jidmachine) AS jidmachines,
        GROUP_CONCAT(xmppmaster.syncthing_machine.jid_relay) AS jidrelays,
        xmppmaster.syncthing_ars_cluster.numcluster,
        syncthing_deploy_group.directory_tmp
    FROM
        xmppmaster.syncthing_deploy_group
            INNER JOIN
        xmppmaster.syncthing_ars_cluster
            ON xmppmaster.syncthing_deploy_group.id = xmppmaster.syncthing_ars_cluster.fk_deploy
            INNER JOIN
        xmppmaster.syncthing_machine
            ON xmppmaster.syncthing_ars_cluster.fk_deploy = xmppmaster.syncthing_deploy_group.id
    WHERE
        xmppmaster.syncthing_deploy_group.dateend < NOW()
    GROUP BY xmppmaster.syncthing_ars_cluster.numcluster; """
        result = session.execute(sql)
        session.commit()
        session.flush()
        ret = [{'id': x[0], 'jidmachines': x[1], 'jidrelays': x[2], 'numcluster': x[3],  'directory_tmp': x[4]} for x in result]
        return ret


    @DatabaseHelper._sessionm
    def get_ensemble_ars_idem_cluster(self, session, ars_id):
        sql ="""SELECT
                    jid, nameserver, keysyncthing
                FROM
                    xmppmaster.has_cluster_ars
                        INNER JOIN
                    xmppmaster.relayserver ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                WHERE
                    id_cluster = (SELECT
                            id_cluster
                        FROM
                            xmppmaster.has_cluster_ars
                        WHERE
                            id_ars = %s);""" % ars_id
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [{"jid": element[0],
                 "name": element[1],
                 "keysyncthing": element[2]} for element in result]

    @DatabaseHelper._sessionm
    def get_list_ars_from_cluster(self, session, cluster=0):
        sql ="""SELECT jid, nameserver, keysyncthing  FROM xmppmaster.has_cluster_ars
                INNER JOIN
                xmppmaster.relayserver
                    ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                WHERE id_cluster = %s;""" % cluster
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [{"jid": element[0],
                 "name": element[1],
                 "keysyncthing": element[2]} for element in result]


    @DatabaseHelper._sessionm
    def refresh_syncthing_deploy_clean(self, session, iddeploy):
        sql = """DELETE FROM `xmppmaster`.`syncthing_deploy_group` WHERE  id= %s;""" % iddeploy
        result = session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def get_log_status(self, session):
        """
            get complete table
        """
        result = []
        try:
            ret = session.query(Def_remote_deploy_status).all()
            session.commit()
            session.flush()
            if ret is None:
                result = []
            else:
                result = [{'index':id,
                           "id": rule.id,
                           'regexplog': rule.regex_logmessage,
                           'status': rule.status,
                           'label': rule.label} for id, rule in enumerate(ret)]
            return result
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return result

    @DatabaseHelper._sessionm
    def updateMachinejidGuacamoleGroupdeploy(self, session, jid, urlguacamole, groupdeploy, idmachine):
        updatedb=-1
        try:
            sql = """UPDATE machines
                    SET
                        jid = '%s', urlguacamole = '%s', groupdeploy = '%s'
                    WHERE
                        id = '%s';""" % (jid, urlguacamole, groupdeploy, idmachine)
            updatedb = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return updatedb

    @DatabaseHelper._sessionm
    def get_xmppmachines_list(self, session, start, limit, filter, presence):
        try:
            start = int(start)
        except:
            start = -1
        try:
            limit = int(limit)
        except:
            limit = -1

        query = session.query(Machines.id,
                Machines.hostname,
                Machines.enabled,
                Machines.jid,
                Machines.platform,
                Machines.archi,
                Machines.classutil,
                Machines.urlguacamole,
                Machines.kiosk_presence,
                Machines.ad_ou_user,
                Machines.ad_ou_machine,
                Machines.macaddress,
                Machines.ip_xmpp)\
            .add_column(Cluster_ars.name.label('cluster_name'))\
            .add_column(Cluster_ars.description.label('cluster_description'))\
            .join(RelayServer, RelayServer.jid == Machines.groupdeploy)\
            .outerjoin(Has_cluster_ars, Has_cluster_ars.id_ars == RelayServer.id)\
            .outerjoin(Cluster_ars, Cluster_ars.id == Has_cluster_ars.id_cluster)\
            .filter(Machines.agenttype == 'machine', Machines.uuid_inventorymachine == None)

        if presence == 'nopresence':
            query = query.filter(Machines.enabled != 1)
        elif presence == 'presence':
            query = query.filter(Machines.enabled == 1)

        if filter != "":
            query = query.filter(
                or_(
                    Machines.hostname.contains(filter),
                    Machines.platform.contains(filter),
                    Machines.jid.contains(filter),
                    Machines.archi.contains(filter),
                    Machines.hostname.contains(filter),
                    Machines.ip_xmpp.contains(filter),
                    Machines.macaddress.contains(filter),
                    Machines.classutil.contains(filter),
                    Machines.ad_ou_machine.contains(filter),
                    Machines.ad_ou_user.contains(filter),
                    Machines.kiosk_presence.contains(filter),
                    Cluster_ars.name.contains(filter),
                    Cluster_ars.description.contains(filter)
                )
            )
        count = query.count()
        if start != -1 and limit != -1:
            query = query.offset(start).limit(limit)

        query= query.all()

        result = {
            'id': [],
            'jid': [],
            'enabled': [],
            'enabled_css': [],
            'archi': [],
            'platform': [],
            'hostname': [],
            'ip_xmpp': [],
            'macaddress': [],
            'classutil': [],
            'urlguacamole': [],
            'ad_ou_machine': [],
            'ad_ou_user': [],
            'kiosk_presence': [],
            'cluster_name': [],
            'cluster_description': []
        }
        if query is not None:
            for machine in query:
                result['id'].append(machine.id)
                result['jid'].append(machine.jid)
                if machine.enabled == 1:
                    result['enabled'].append(True)
                    result['enabled_css'].append('machineNamepresente')
                else:
                    result['enabled'].append(False)
                    result['enabled_css'].append('machineName')
                result['archi'].append(machine.archi)
                result['platform'].append(machine.platform)
                result['hostname'].append(machine.hostname)
                result['ip_xmpp'].append(machine.ip_xmpp)
                result['macaddress'].append(machine.macaddress)
                result['classutil'].append(machine.classutil)
                result['ad_ou_machine'].append(machine.ad_ou_machine)
                result['urlguacamole'].append(machine.urlguacamole)
                result['ad_ou_user'].append(machine.ad_ou_user)
                result['kiosk_presence'].append(machine.kiosk_presence)
                if machine.cluster_name is None:
                    result['cluster_name'].append("NULL")
                else:
                    result['cluster_name'].append(machine.cluster_name)
                if machine.cluster_description is None:
                    result['cluster_description'].append("NULL")
                else:
                    result['cluster_description'].append(machine.cluster_description)
        return {'total': count, 'datas': result}

    @DatabaseHelper._sessionm
    def get_clusters_list(self, session, start, max, filter):
        try:
            start = int(start)
        except:
            start = -1
        try:
            max = int(max)
        except:
            max = -1

        query = session.query(Cluster_ars)

        if filter != "":
            query = query.filter(or_(
                Cluster_ars.name.contains(filter),
                Cluster_ars.description.contains(filter),
            ))
        count = query.count()

        if start != -1 and max != -1:
            query = query.offset(start).limit(max)

        result = {
            'id' : [],
            'name' : [],
            'description': [],
            'nb_ars': [],
        }


        for cluster in query:
            count_ars = session.query(Has_cluster_ars.id_cluster).filter(Has_cluster_ars.id_cluster == cluster.id).count()
            result['id'].append(cluster.id)
            result['name'].append(cluster.name)
            result['description'].append(cluster.description)
            result['nb_ars'].append(count_ars if count_ars is not None else 0)

        return {'total': count, 'datas': result}

    @DatabaseHelper._sessionm
    def get_xmpprelays_list(self, session, start, limit, filter, presence):
        try:
            start = int(start)
        except:
            start = -1
        try:
            limit = int(limit)
        except:
            limit = -1
        query = session.query(RelayServer.id,
                RelayServer.ipserver,
                RelayServer.nameserver,
                RelayServer.moderelayserver,
                RelayServer.jid.label('jid_from_relayserver'),
                RelayServer.classutil,
                RelayServer.enabled,
                RelayServer.switchonoff,
                RelayServer.mandatory)\
            .add_column(Machines.jid)\
            .add_column(Cluster_ars.name.label("cluster_name"))\
            .add_column(Cluster_ars.description.label("cluster_description"))\
            .add_column(Machines.macaddress.label('macaddress'))\
            .outerjoin(Has_cluster_ars, Has_cluster_ars.id_ars == RelayServer.id)\
            .outerjoin(Cluster_ars, Cluster_ars.id == Has_cluster_ars.id_cluster)\
            .outerjoin(Machines, func.substring_index(Machines.jid, '/', 1) == func.substring_index(RelayServer.jid, '/', 1))\
            .filter(RelayServer.moderelayserver == 'static')

        if presence == 'nopresence':
            query = query.filter(RelayServer.enabled != 1)
        elif presence == 'presence':
            query = query.filter(RelayServer.enabled == 1)

        if filter != "":
            query = query.filter(
                or_(
                    RelayServer.nameserver.contains(filter),
                    Machines.jid.contains(filter),
                    Cluster_ars.name.contains(filter),
                    Cluster_ars.description.contains(filter),
                    RelayServer.classutil.contains(filter),
                    Machines.macaddress.contains(filter),
                    RelayServer.ipserver.contains(filter),
                )
            )
        count = query.count()
        if start != -1 and limit != -1:
            query = query.offset(start).limit(limit)

        query= query.all()

        result = {
            'id': [],
            'hostname': [],
            'jid': [],
            'jid_from_relayserver': [],
            'cluster_name': [],
            'cluster_description': [],
            'classutil': [],
            'macaddress': [],
            'ip_xmpp': [],
            'enabled': [],
            'enabled_css': [],
            'mandatory': [],
            'switchonoff': [],
            'uninventoried_offline': [],
            'uninventoried_online': [],
            'inventoried_offline': [],
            'inventoried_online': [],
            'total_machines': [],
        }
        if query is not None:
            sql1 = """select count(id) as nb
from machines
where uuid_inventorymachine IS NULL and enabled = 0 and agenttype="machine" """
            sql2 = """select count(id) as nb
from machines
where uuid_inventorymachine IS NULL and enabled = 1 and agenttype="machine"
"""

            sql3 = """select count(id) as nb
from machines
where uuid_inventorymachine IS NOT NULL and enabled = 0 and agenttype="machine"
"""
            sql4 = """select count(id) as nb
from machines
where uuid_inventorymachine IS NOT NULL and enabled = 1 and agenttype="machine"
"""
            for machine in query:
                _sql1 = sql1 + """and groupdeploy = "%s";""" % machine.jid
                count_uninventoried_offline = session.execute(_sql1)
                uninventoried_offline = [x for x in count_uninventoried_offline]

                _sql2 = sql2 + """and groupdeploy = "%s";""" % machine.jid
                count_uninventoried_offline = session.execute(_sql2)
                uninventoried_online = [x for x in count_uninventoried_offline]

                _sql3 = sql3 + """and groupdeploy = "%s";""" % machine.jid
                count_uninventoried_offline = session.execute(_sql3)
                inventoried_offline = [x for x in count_uninventoried_offline]

                _sql4 = sql4 + """and groupdeploy = "%s";""" % machine.jid
                count_uninventoried_offline = session.execute(_sql4)
                inventoried_online = [x for x in count_uninventoried_offline]

                total_machines = uninventoried_offline[0][0] + \
                    uninventoried_online[0][0] + \
                    inventoried_offline[0][0] + \
                    inventoried_online[0][0]
                result['uninventoried_offline'].append(uninventoried_offline[0][0])
                result['uninventoried_online'].append(uninventoried_online[0][0])
                result['inventoried_offline'].append(inventoried_offline[0][0])
                result['inventoried_online'].append(inventoried_online[0][0])
                result['total_machines'].append(total_machines)

                result['id'].append(machine.id)
                result['jid'].append(machine.jid)
                result['jid_from_relayserver'].append(machine.jid_from_relayserver)
                if machine.enabled == 1:
                    result['enabled'].append(True)
                    result['enabled_css'].append('machineNamepresente')
                else:
                    result['enabled'].append(False)
                    result['enabled_css'].append('machineName')
                result['hostname'].append(machine.nameserver)
                result['ip_xmpp'].append(machine.ipserver)
                result['macaddress'].append(machine.macaddress)
                result['classutil'].append(machine.classutil)
                if machine.cluster_name is None:
                    result['cluster_name'].append("NULL")
                else:
                    result['cluster_name'].append(machine.cluster_name)
                if machine.cluster_description is None:
                    result['cluster_description'].append("NULL")
                else:
                    result['cluster_description'].append(machine.cluster_description)
                result['mandatory'].append(machine.mandatory)
                result['switchonoff'].append(machine.switchonoff)
        return {'total': count, 'datas': result}

    @DatabaseHelper._sessionm
    def change_relay_switch(self, session, jid, switch, propagate):
        id_cluster = None
        if propagate is True:
            session.query(RelayServer).filter(func.substring_index(RelayServer.jid, '/', 1) == jid.split('/')[0],\
                RelayServer.mandatory == 0).update(\
                {RelayServer.switchonoff: switch})
            try:
                cluster = session.query(Has_cluster_ars.id_cluster)\
                    .join(RelayServer, Has_cluster_ars.id_ars == RelayServer.id)\
                    .join(Machines, func.substring_index(Machines.jid, '/', 1) == func.substring_index(RelayServer.jid, '/', 1))\
                    .filter(Machines.jid == jid).one()
                id_cluster = cluster.id_cluster
            except:
                pass

        if id_cluster is not None and propagate is True:
            sql = """update
    machines
set
    need_reconf = 1
where agenttype="machine" and groupdeploy in (
    select
        relayserver.jid
    from relayserver
    inner join
        has_cluster_ars
    on has_cluster_ars.id_ars = relayserver.id
    where id_cluster = %s
);""" % id_cluster
            session.execute(sql)
        elif id_cluster is None or propagate is False:
            session.query(Machines).filter(Machines.agenttype=="machine", \
            Machines.groupdeploy==jid).update(\
                {Machines.need_reconf:1})
        session.commit()
        session.flush()


    @DatabaseHelper._sessionm
    def call_reconfiguration_machine(self, session, limit=None, typemachine="machine"):
        if typemachine in ["machine", "relay"]:
            res = session.query(Machines.id, Machines.jid).\
                filter(and_( Machines.need_reconf == '1',
                            Machines.enabled == '1',
                            Machines.agenttype.like(typemachine)))
        elif typemachine is None or typemachine=="all":
            res = session.query(Machines.id, Machines.jid).\
                filter(and_( Machines.need_reconf == '1',
                            Machines.enabled == '1'))
        if limit is not None:
            res = res.limit(int(limit))
        res= res.all()
        listjid = []
        if res is not None:
            for machine in res:
                listjid.append( [machine.id,machine.jid])
        session.commit()
        session.flush()
        return listjid

    @DatabaseHelper._sessionm
    def call_acknowledged_reconficuration(self, session, listmachine=[]):
        listjid = []
        if not listmachine:
            return listjid
        res = session.query(Machines.id,
                            Machines.need_reconf).filter(and_(Machines.need_reconf == '0',
                                                            Machines.id.in_(listmachine))).all()
        if res is not None:
            for machine in res:
                listjid.append(machine.id)
        session.commit()
        session.flush()
        return listjid

    @DatabaseHelper._sessionm
    def call_set_list_machine(self, session, listmachine=[], valueset=0):
        """
            initialise presence on list id machine
        """
        if not listmachine:
            return False
        try:
            liststr = ",".join(["'%s'" % x for x in listmachine])

            sql = """UPDATE `xmppmaster`.`machines`
                    SET
                        `enabled` = '%s'
                    WHERE
                        `id` IN (%s);""" % (valueset, liststr)
            session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception, e:
            logging.getLogger().error("call_set_list_machine: %s" % str(e))
            return False

    @DatabaseHelper._sessionm
    def is_relay_online(self, session, jid):
        """Get the enable status for a specified relay
        @param: jid str
        @returns: boolean"""
        try:
            query = session.query(RelayServer.enabled)\
            .filter(func.substring_index(RelayServer.jid, '/', 1)==jid.split('/')[0]).one()

            if query is not None:
                return query.enabled
            else:
                return False
        except:
            return False
    @DatabaseHelper._sessionm
    def get_qa_for_relays(self, session, login=""):
        """ Get the list of qa for relays
        @login : user's login
        @returns : list of quick actions
        """
        if login != "":
            query = session.query(Qa_relay_command)\
                .filter(
                    or_(
                        Qa_relay_command.user == "allusers",
                        Qa_relay_command.user == login)).all()
        else:
            query = session.query(Qa_relay_command)\
                .filter(Qa_relay_command.user == "allusers").all()

        result = []
        tmp = {'id': 0, 'user':"", 'namecmd': "", 'customcmd': "", 'description': ""}
        if query is not None:
            for command in query:
                result.append({'id' : command.id,
                                'user' : command.user,
                                'script' : command.script,
                                'description' : command.description})
        return result

    @DatabaseHelper._sessionm
    def get_relay_qa(self, session, login, qa_relay_id):
        """ Get the qa by its id and its login
        @returns : the command to be run or None
        """

        try:
            query = session.query(Qa_relay_command)\
                .filter(
                    and_(
                        or_(
                            Qa_relay_command.user == "allusers",
                            Qa_relay_command.user == login)
                        ),
                        Qa_relay_command.id == qa_relay_id).one()
            return {'id' : query.id,
                            'user' : query.user,
                            'name' : query.name,
                            'script' : query.script,
                            'description' : query.description}
        except:
            return None


    @DatabaseHelper._sessionm
    def get_qa_relay_result(self, session, result_id):
        result = {
            'id': 0,
            'launched_id' : 0,
            'session_id' : "",
            'typemessage' : "log",
            'command_result' : "",
            'relay' : ""
        }

        query = session.query(Qa_relay_result).filter(Qa_relay_result.id == result_id).one()
        if query is not None:
            result['id'] = query.id
            result['launched_id'] = query.launched_id
            result['session_id'] = query.session_id
            result['typemessage'] = query.typemessage
            result['command_result'] = query.command_result
            result['relay'] = query.relay

        if query.command_result == "" or query.command_result == None:
            if query.session_id != "" and os.path.isfile(os.path.join('/','tmp', query.session_id)):
                # Try to read the tmp file
                try:
                    with open(os.path.join('/','tmp', query.session_id), 'r') as tmp_file:
                        # If some content : read it
                        content = tmp_file.read()
                        if content != "":
                            # update the result field
                            query.command_result = content
                            session.commit()
                            result['command_result'] = content
                            os.remove(os.path.join('/','tmp', result["session_id"]))
                            tmp_file.close()

                    # do nothing if the tmp file is not readable for any reasons

                except Exception as e:
                    result['command_result'] = ""

        return result

    @DatabaseHelper._sessionm
    def add_qa_relay_launched(self, session, qa_relay_id, login, cluster_id, jid):
        format = "%Y-%m-%d %H:%M:%S"
        execution_date = datetime.now()

        qa_launched = Qa_relay_launched()

        qa_launched.id_command = qa_relay_id
        qa_launched.user_command = login
        qa_launched.command_relay = jid
        qa_launched.command_start = execution_date

        session.add(qa_launched)
        session.commit()
        session.flush()

        if qa_launched.id == None:
            qa_launched.id = 0
        if qa_launched.id_command == None:
            qa_launched.id_command = 0
        if qa_launched.user_command == None:
            qa_launched.user_command = ""
        if qa_launched.command_start == None:
            qa_launched.command_start = ""
        if qa_launched.command_cluster == None:
            qa_launched.command_cluster = ""
        if qa_launched.command_relay == None:
            qa_launched.command_relay = ""


        return {
            'id' : qa_launched.id,
            'id_command' : qa_launched.id_command,
            'user_command' : qa_launched.user_command,
            'command_start' : qa_launched.command_start.strftime(format),
            'command_cluster' : qa_launched.command_cluster,
            'command_relay' : qa_launched.command_relay
        }

    @DatabaseHelper._sessionm
    def add_qa_relay_result(self, session, jid, exec_date, qa_relay_id, launched_id, session_id=""):
        qa_result = Qa_relay_result()
        qa_result.id_command = qa_relay_id
        qa_result.launched_id = launched_id
        qa_result.session_id = session_id # name_random(8,"quick_")
        qa_result.typemessage = "log"
        qa_result.command_result = ""
        qa_result.relay = jid


        session.add(qa_result)
        session.commit()
        session.flush()

        if qa_result.id == None:
            qa_result.id = 0
        if qa_result.id_command == None:
            qa_result.id_command = ""
        if qa_result.launched_id == None:
            qa_result.launched_id = ""
        if qa_result.session_id == None:
            qa_result.session_id = ""
        if qa_result.typemessage == None:
            qa_result.typemessage = ""
        if qa_result.command_result == None:
            qa_result.command_result = ""
        if qa_result.relay == None:
            qa_result.relay = ""

        return {
            'id' : qa_result.id,
            'id_command' : qa_result.id_command,
            'launched_id' : qa_result.launched_id,
            'session_id' : qa_result.session_id,
            'typemessage' : qa_result.typemessage,
            'command_result' : qa_result.command_result,
            'relay' : qa_result.relay
        }

    @DatabaseHelper._sessionm
    def get_relay_qa_launched(self, session, jid, login, start=-1, limit=-1):
        format = "%Y-%m-%d %H:%M:%S"
        try:
            start = int(start)
        except:
            start = -1

        try:
            limit = int(limit)
        except:
            limit = -1

        total = 0

        query = session.query(Qa_relay_launched)\
            .add_column(Qa_relay_command.name)\
            .add_column(Qa_relay_command.description)\
            .add_column(Qa_relay_result.id.label('id_result'))\
            .filter(Qa_relay_launched.user_command == login)\
            .filter(Qa_relay_launched.command_relay == jid)\
            .order_by(desc(Qa_relay_launched.command_start))\
            .outerjoin(Qa_relay_command, Qa_relay_launched.id_command == Qa_relay_command.id)\
            .outerjoin(Qa_relay_result, Qa_relay_launched.id == Qa_relay_result.launched_id)

        total = query.count()

        if start != -1:
            query = query.offset(start)

        if limit != -1:
            query = query.limit(limit)

        query = query.all()

        result = {
            'total': total,
            'datas' : {
                'id' : [],
                'id_command' : [],
                'name' : [],
                'description' : [],
                'user_command' : [],
                'command_start' : [],
                'command_cluster' : [],
                'command_relay' : [],
                'result_id' : []
            }
        }
        if query is not None:
            for launched, name, description, result_id in query:
                result['datas']['id'].append(launched.id)
                result['datas']['id_command'].append(launched.id_command)
                result['datas']['command_start'].append(launched.command_start.strftime(format))
                if launched.command_cluster is None:
                    result['datas']['command_cluster'].append("")
                else:
                    result['datas']['command_cluster'].append(launched.command_cluster)

                result['datas']['command_relay'].append(launched.command_relay)
                result['datas']['user_command'].append(launched.user_command)
                result['datas']['name'].append(name)
                result['datas']['description'].append(description)
                if result_id is None:
                    result['datas']['result_id'].append('')
                else:
                    result['datas']['result_id'].append(result_id)
        return result

    @DatabaseHelper._sessionm
    def getmachinesbyuuids(self, session, uuids):
        query = session.query(Machines).filter(and_(Machines.uuid_inventorymachine.in_(uuids))).all()

        result = {}

        for machine in query:
            result[machine.uuid_inventorymachine] = {
                "id": machine.id,
                'jid' : machine.jid,
                'need_reconf' : machine.need_reconf,
                'enabled' : machine.enabled,
                'platform' : machine.platform,
                'archi' : machine.archi,
                'hostname' : machine.hostname,
                'uuid_inventorymachine' : machine.uuid_inventorymachine,
                'id_inventorymachine' : machine.uuid_inventorymachine.replace('UUID', ''),
                'ippublic' : machine.ippublic,
                'ip_xmpp' : machine.ip_xmpp,
                'macaddress' : machine.macaddress,
                'subnetxmpp' : machine.subnetxmpp,
                'classutil' : machine.classutil,
                'groupdeploy' : machine.groupdeploy,
                'ad_ou_machine' : machine.ad_ou_machine,
                'ad_ou_user' : machine.ad_ou_user,
                'kiosk_presence' : machine.kiosk_presence,
                'lastuser' : machine.lastuser,
                'keysyncthing' : machine.keysyncthing,
                'uuid_serial_machine': machine.uuid_serial_machine}
        return result

    # SUBSTITUTE UPDATE TIME
    @DatabaseHelper._sessionm
    def setUptime_machine(self,
                          session,
                          hostname,
                          jid,
                          status=0,
                          updowntime=0,
                          date=None):
        """
        This function allow to know the uptime of a machine
        Args:
            session: The sqlalchemy session
            hostname: The hostname of the machine
            jid: The jid of the machine
            status: The current status of the machine
                    Can be 1 or 0
                    0: The machine is offline
                    1: The machine is online
            uptime: The current uptime of the machine
        Returns:
            It returns the id of the machine
        """
        try:
            new_Uptime_machine = Uptime_machine()
            new_Uptime_machine.hostname = hostname
            new_Uptime_machine.jid = jid
            new_Uptime_machine.status = status
            new_Uptime_machine.updowntime = updowntime
            if date is not None:
                new_Uptime_machine.date = date
            session.add(new_Uptime_machine)
            session.commit()
            session.flush()
            return new_Uptime_machine.id
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def last_event_presence_xmpp(self,
                                 session,
                                 jid,
                                 nb=1):
        """
        This function allow to obtain the last presence.
            Args:
                session: The sqlalchemy session
                jid: The jid of the machine
                nb: Number of evenements we look at

            Returns:
                It returns a dictionnary with:
                    id: The id of the machine
                    hostname: The hostname of the machine
                    status: The current status of the machine
                        Can be 1 or 0:
                            0: The machine is offline
                            1: The machine is online
                    updowntime:
                            The uptime if status is set to 0
                            The downtime if status is set to 1
                    date: The date we checked the informations
                    time: Unix time
        """
        try:
            sql = """SELECT
                    *,
                    UNIX_TIMESTAMP(date)
                FROM
                    xmppmaster.uptime_machine
                WHERE
                    jid LIKE '%s'
                ORDER BY id DESC
                LIMIT %s;""" % (jid, nb)
            result = session.execute(sql)
            session.commit()
            session.flush()
            return [{"id": element[0],
                     "hostname": element[1],
                     "jid": element[2],
                     "status": element[3],
                     "updowntime": element[4],
                     "date": element[5].strftime("%Y/%m/%d/ %H:%M:%S"),
                     "time": element[6]} for element in result]
        except Exception, e:
            logging.getLogger().error(str(e))
            return []

    #TODO: Add this function for hours too.
    #      Add in QA too.
    @DatabaseHelper._sessionm
    def stat_up_down_time_by_last_day(self,
                                      session,
                                      jid,
                                      day=1):
        """
        This function is used to know how long a machine is online/offline.
        It allow to know the number of start of this machine too.

        Args:
            session: The Sqlalchemy session
            jid: The jid of the machine
            day: The number of days for the count
        Returns:
            It returns a dictonary with :
                jid: The jid of the machine
                downtime: The time the machine has been down
                uptime: The time the machine has been running the agent
                nbstart: The number of start of the agent
                totaltime: The interval (in seconds) on which we count
        """

        statdict = {}
        statdict['machine'] = jid
        statdict['downtime'] = 0
        statdict['uptime'] = 0
        statdict['nbstart'] = 0
        statdict['totaltime'] = day * 86400
        try:
            sql = """SELECT
                    id, status, updowntime, date
                FROM
                    xmppmaster.uptime_machine
                WHERE
                        jid LIKE '%s'
                    AND
                        date > CURDATE() - INTERVAL %s DAY;""" % (jid, day)
            result = session.execute(sql)
            session.commit()
            session.flush()
            # We set nb to false to not use the last informations
            # This would lead to errors.
            nb = False
            if result:
                for el in result:
                    if el.status == 0:
                        if statdict['nbstart'] > 0:
                            if nb:
                                statdict['uptime'] = statdict['uptime'] + el[2]
                            else:
                                nb = True
                    else:
                        statdict['nbstart'] = statdict['nbstart'] + 1
                        if nb:
                            statdict['downtime'] = statdict['downtime'] + el[2]
                        else:
                            nb = True
            return statdict
        except Exception, e:
            self.logger.error("\n%s" % (traceback.format_exc()))
            logging.getLogger().error(str(e))
            return statdict


    @DatabaseHelper._sessionm
    def setMonitoring_machine(self,
                              session,
                              machines_id,
                              hostname,
                              statusmsg="",
                              date=None):
        try:
            new_Monitoring_machine = Mon_machine()
            new_Monitoring_machine.machines_id = machines_id
            if date is not None:
                date = date.replace("T", " ").replace("Z", "")[:19]
                new_Monitoring_machine.date = date
            new_Monitoring_machine.hostname = hostname
            new_Monitoring_machine.statusmsg = statusmsg
            session.add(new_Monitoring_machine)
            session.commit()
            session.flush()
            return new_Monitoring_machine.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def setMonitoring_device(self,
                             session,
                             hostname,
                             mon_machine_id,
                             device_type,
                             serial,
                             firmware,
                             status,
                             alarm_msg,
                             doc):
        try:
            logging.getLogger().debug("==================================\n"
                                      "device_type [%s]"%device_type)
            #if device_type not in ['thermalPrinter',
                                   #'nfcReader',
                                   #'opticalReader',
                                   #'cpu',
                                   #'memory',
                                   #'storage',
                                   #'network',
                                   #'system']:
                #raise DomaineTypeDeviceError()
            if status not in ['ready', 'busy', 'warning', 'error', 'disable']:
                raise DomainestatusDeviceError()
            new_Monitoring_device = Mon_devices()
            new_Monitoring_device.mon_machine_id = mon_machine_id
            new_Monitoring_device.device_type = device_type
            new_Monitoring_device.serial = serial
            new_Monitoring_device.firmware = firmware
            new_Monitoring_device.status = status
            new_Monitoring_device.alarm_msg = alarm_msg
            new_Monitoring_device.doc = doc
            session.add(new_Monitoring_device)
            session.commit()
            session.flush()
            logging.getLogger().debug("==================================")
            return new_Monitoring_device.id
        except Exception as e:
            logging.getLogger().error(str(e))
            self.logger.error("\n%s" % (traceback.format_exc()))
            return -1

    @DatabaseHelper._sessionm
    def setMonitoring_device_reg(self,
                                 session,
                                 hostname,
                                 mon_machine_id,
                                 device_type,
                                 serial,
                                 firmware,
                                 status,
                                 alarm_msg,
                                 doc):
        try:
            id_device_reg = self.setMonitoring_device(hostname,
                                                      mon_machine_id,
                                                      device_type,
                                                      serial,
                                                      firmware,
                                                      status,
                                                      alarm_msg,
                                                      doc)

            # creation event on rule
            objectlist_local_rule = self._rule_monitoring(hostname,
                                                          mon_machine_id,
                                                          device_type,
                                                          serial,
                                                          firmware,
                                                          status,
                                                          alarm_msg,
                                                          doc,
                                                          localrule=True)
            if objectlist_local_rule:
                # A rule is defined for this device on this machine
                self._action_new_event(objectlist_local_rule,
                                        mon_machine_id,
                                        id_device_reg,
                                        doc,
                                        status_event=1,
                                        hostname=hostname)
            else:
                # Check if there is a general rule for this device
                objectlist_local_rule = self._rule_monitoring(hostname,
                                                              mon_machine_id,
                                                              device_type,
                                                              serial,
                                                              firmware,
                                                              status,
                                                              alarm_msg,
                                                              doc,
                                                              localrule=False)
                if objectlist_local_rule:
                    self._action_new_event(objectlist_local_rule,
                                            mon_machine_id,
                                            id_device_reg,
                                            doc,
                                            status_event=1,
                                            hostname=hostname)
            logging.getLogger().debug("==================================")
            return id_device_reg
        except Exception as e:
            logging.getLogger().error(str(e))
            self.logger.error("\n%s" % (traceback.format_exc()))
            return -1

    @DatabaseHelper._sessionm
    def setMonitoring_event(self,
                            session,
                            machines_id,
                            id_device,
                            id_rule,
                            cmd,
                            type_event="log",
                            status_event=1,
                            parameter_other=None,
                            ack_user=None,
                            ack_date=None):
        try:
            new_Monitoring_event = Mon_event()
            new_Monitoring_event.machines_id = machines_id
            new_Monitoring_event.id_rule = id_rule
            new_Monitoring_event.id_device = id_device
            new_Monitoring_event.type_event = type_event
            new_Monitoring_event.cmd = cmd
            new_Monitoring_event.parameter_other = parameter_other
            new_Monitoring_event.ack_user = ack_user
            new_Monitoring_event.ack_date = ack_date
            session.add(new_Monitoring_event)
            session.commit()
            session.flush()
            return new_Monitoring_event.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return -1

    def _action_new_event(self,
                          objectlist_local_rule,
                          id_machine,
                          id_device,
                          doc,
                          status_event=1,
                          hostname=None):
        if objectlist_local_rule:
            # apply binding to find out if an alert or event is defined
            for z in objectlist_local_rule:
                msg, result = self.__binding_application_check(doc,
                                                               z['binding'],
                                                               z['device_type'])
                if result == -1:
                    if z['error_on_binding'] is None or \
                        z['error_on_binding'].strip() == "":
                        # aucun trairement sur error
                        continue
                elif result == 1:
                    # alert True
                    # create event if action associated to true
                    if z['succes_binding_cmd'] is None or \
                        z['succes_binding_cmd'].strip() == "":
                        # aucun trairement sur success binding
                        continue
                    # 1 event est a prendre en compte.
                    bindingcmd = z['succes_binding_cmd']
                elif result == 0:
                    # alert False
                    # create event if action associated to False
                    if z['no_success_binding_cmd'] is None or \
                        z['no_success_binding_cmd'].strip() == "":
                        continue
                    bindingcmd = z['no_success_binding_cmd']
                else:
                    #cas pas encore prevu
                    continue
                #if hostname is not None:
                    #self.remise_status_event(z['id'],
                                             #0,
                                             #hostname)
                self.logger.debug("%s create event %s " %(z['device_type'],
                                                          z['type_event']))
                self.setMonitoring_event(id_machine,
                                         id_device,
                                         z['id'],
                                         bindingcmd,
                                         type_event=z['type_event'],
                                         status_event=1)

    def __binding_application_check(self, datastring, bindingstring, device_type):
        resultbinding = None
        try:
            data=json.loads(datastring)
        except Exception as e:
            msg =  "[binding error device rule %s] : data from message" \
                " monitoring format json error %s" % (device_type, str(e))
            logging.getLogger().error("%s" % msg)
            return (msg, -1)
        try:
            logging.getLogger().debug("compile")
            code = compile(bindingstring, '<string>', 'exec')
            exec(code)
        except KeyError as e:
            msg = "[binding error device rule %s] : key %s in "\
                "binding:\n%s\nis missing. Check your binding on data\n%s" % (
                    device_type,
                    str(e),
                    bindingstring,
                    json.dumps(data,indent=4))
            logging.getLogger().error("%s" % msg)
            return (msg, -1)
        except Exception as e:
            msg = "[binding device rule %s error %s] in binding:\n%s\ "\
                "on data\n%s"%(device_type,
                               str(e),
                               bindingstring,
                               json.dumps(data,indent=4))
            logging.getLogger().error("%s" % msg)
            return (msg, -1)
        msg = "[ %s : result binding %s for binding:\n%s\ "\
                "on data\n%s"%(device_type,
                               resultbinding,
                               bindingstring,
                               json.dumps(data,indent=4))
        logging.getLogger().debug("%s" % msg)
        return (msg, resultbinding)

    @DatabaseHelper._sessionm
    def remise_status_event(self,
                            session,
                            id_rule,
                            status_event,
                            hostname):
        try:
            sql="""UPDATE `xmppmaster`.`mon_event`
                        JOIN
                    xmppmaster.mon_machine ON xmppmaster.mon_machine.id = xmppmaster.mon_event.machines_id
                SET
                    `xmppmaster`.`mon_event`.`status_event` = '%s'
                WHERE
                        xmppmaster.mon_machine.hostname LIKE '%s'
                    AND
                        xmppmaster.mon_event.id_rule = %s;""" % (status_event,
                                                                 hostname,
                                                                 id_rule)

            result = session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logging.getLogger().error(str(e))
            return -1

    def __binding_application(self, datastring, bindingstring, device_type):
        resultbinding = None
        try:
            data=json.loads(datastring)
        except Exception as e:
            return "[binding error device rule %s] : data from message" \
                " monitoring format json error %s" % (device_type, str(e))

        try:
            code = compile(bindingstring, '<string>', 'exec')
            exec(code)
        except KeyError as e:
            resultbinding = "[binding error device rule %s] : key %s in "\
                "binding:\n%s\nis missing. Check your binding on data\n%s" % (
                    device_type,
                    str(e),
                    bindingstring,
                    json.dumps(data,indent=4))
        except Exception as e:
            resultbinding = "[binding device rule %s error %s] in binding:\n%s\ "\
                "on data\n%s"%(device_type,
                               str(e),
                               bindingstring,
                               json.dumps(data,indent=4))
        return resultbinding

    @DatabaseHelper._sessionm
    def getlistMonitoring_devices_type(self,
                              session,
                              enable=1):
        sql = ''' SELECT DISTINCT
                    LOWER(device_type)
                FROM
                    xmppmaster.mon_device_service
                WHERE
                    enable = 1;'''
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [i[0].lower() for i in result]

    @DatabaseHelper._sessionm
    def _rule_monitoring(self,
                         session,
                         hostname,
                         mon_machine_id,
                         device_type,
                         serial,
                         firmware,
                         status,
                         alarm_msg,
                         doc,
                         localrule=True):
        if localrule:
            sql = ''' SELECT
                        *
                    FROM
                        xmppmaster.mon_rules
                    WHERE
                        hostname LIKE '%s'
                            AND device_type LIKE '%s';''' % (hostname,
                                                        device_type)
        else:
            sql = ''' SELECT
                        *
                    FROM
                        xmppmaster.mon_rules
                    WHERE
                        device_type LIKE '%s';''' % (device_type)
        #logging.getLogger().debug("sql %s"%sql)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [{'id': i[0],
                 'hostname': i[1],
                 'device_type': i[2],
                 "binding": i[3],
                 "succes_binding_cmd": i[4],
                 "no_success_binding_cmd": i[5],
                 "error_on_binding": i[6],
                 "type_event": i[7],
                 "user": i[8],
                 "comment": i[9]} for i in result]

    @DatabaseHelper._sessionm
    def analyse_mon_rules(self,
                          session,
                          mon_machine_id,
                          device_type,
                          serial,
                          firmware,
                          status,
                          alarm_msg,
                          doc):
        # search rule for device and machine
        pass


    @DatabaseHelper._sessionm
    def setMonitoring_panels_template(self,
                                      session,
                                      name_graphe,
                                      template_json,
                                      type_graphe,
                                      parameters="{}",
                                      status=True,
                                      comment=""):
        """
        This function allows to record panel graph template
        Args:
            session: The sqlalchemy session
            name_graphe: The name of graph
            template_json: The panel template in json format
            type_graphe: The type of graph
            parameters: The optional parameters json string  { "key":"value",...}
            status: Can be True, False or None
            comment:
        Returns:
            It returns the id of the machine
        """
        try:
            new_Monitoring_panels_template = Mon_panels_template()
            new_Monitoring_panels_template.name_graphe = name_graphe
            new_Monitoring_panels_template.template_json = template_json
            new_Monitoring_panels_template.type_graphe = type_graphe
            new_Monitoring_panels_template.parameters = parameters
            new_Monitoring_panels_template.status = status
            new_Monitoring_panels_template.comment = comment
            session.add(new_Monitoring_panels_template)
            session.commit()
            session.flush()
            return new_Monitoring_panels_template.id
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def getMonitoring_panels_template(self,
                                      session,
                                      status=True):
        """
        This function allows to get panel graph template
        Args:
            session: The sqlalchemy session
            status: The default value is True
                    Can be 1, 0 or None
                    False : list of template panels status False
                    True : list of template panels status True
                    None: list of all template panels
        Returns:
            It returns the list of template panels
        """
        try:
            list_panels_template = []
            if status:
                result_panels_template = session.query(Mon_panels_template).\
                filter(and_(Mon_panels_template.status == 1)).all()
            elif status is False:
                result_panels_template = session.query(Mon_panels_template).\
                filter(and_(Mon_panels_template.status == 0)).all()
            else:
                result_panels_template = session.query(Mon_panels_template).all()
            session.commit()
            session.flush()
            for graphe_template in result_panels_template:
                res = {'id': graphe_template.id,
                       'name_graphe': graphe_template.name_graphe,
                       'template_json': graphe_template.template_json,
                       'type_graphe': graphe_template.type_graphe,
                       'parameters': graphe_template.parameters,
                       'status': graphe_template.status,
                       'comment': graphe_template.comment}
                list_panels_template.append(res)
        except Exception, e:
            logging.getLogger().error(str(e))
        return list_panels_template

    @DatabaseHelper._sessionm
    def get_mon_events(self, session, start, max, filter):
        """Get monitoring events informations
        Params:
            - sqlalchemy session: managed by DatabaseHelper._sessionm decorator
            - int start: represents the starting offset for a sql limit clause
            - int max: represents the number of result returned by the function
            - string filter: if not empty this string is searched into each event
        Returns:
            dict events: all the events found for the limit and filter clause. The
            dict has the following shape:
            result = {
                'total': 1,
                'datas' : [
                    {dict representing the event 1},
                    {dict representing the event 2},
                    ...
                ]
            }
        """

        try:
            start = int(start)
        except ValueError:
            start = -1

        try:
            max = int(max)
        except ValueError:
            max = -1

        event_types = ['log', 'ack']
        count = 0
        query = session.query(Mon_event, Mon_devices, Mon_rules, Mon_machine, Machines)\
            .outerjoin(Mon_devices, Mon_event.id_device == Mon_devices.id)\
            .outerjoin(Mon_rules, Mon_event.id_rule == Mon_rules.id)\
            .outerjoin(Mon_machine, Mon_event.machines_id == Mon_machine.id)\
            .outerjoin(Machines, Mon_machine.machines_id == Machines.id)\
            .filter(and_(
                Mon_event.status_event == 1,
                Mon_event.type_event.in_(event_types))
            )

        if filter != "":
            query = query.filter(or_(
                    Machines.hostname.contains(filter),
                    Machines.jid.contains(filter),
                    Mon_machine.date.contains(filter),
                    Mon_machine.statusmsg.contains(filter),
                    Mon_devices.alarm_msg.contains(filter),
                    Mon_rules.comment.contains(filter),
                    Mon_rules.device_type.contains(filter),
                    Mon_devices.firmware.contains(filter),
                    Mon_devices.serial.contains(filter),
                    Mon_devices.status.contains(filter),
                    Mon_event.type_event.contains(filter)
                    )
                )

        count = query.count()
        query = query.order_by(desc(Mon_machine.date))

        if start != -1:
            query = query.offset(start)
        if max != -1:
            query = query.limit(max)


        query = query.all()

        result = {
        'total': count,
        'datas': []
        }
        if query:
            for event, device, rule, mon_machine, machine in query:
                tmp = {
                    'event_id': event.id,
                    'event_status': event.status_event if event.status_event is not None else "",
                    'event_type_event': event.type_event if event.type_event is not None else "",
                    'event_cmd': event.cmd if event.cmd is not None else "",
                    'rule_id': rule.id,
                    'rule_hostname': rule.hostname if rule.hostname is not None else "",
                    'rule_device_type': rule.device_type if rule.device_type is not None else "",
                    'rule_binding': rule.binding if rule.binding is not None else "",
                    'rule_succes_binding_cmd': rule.succes_binding_cmd if rule.succes_binding_cmd is not None else "",
                    'rule_error_on_binding': rule.error_on_binding if rule.error_on_binding is not None else "",
                    'rule_user': rule.user if rule.user is not None else "",
                    'rule_comment': rule.comment if rule.comment is not None else "",
                    'mon_machine_date': mon_machine.date.strftime("%m-%d-%Y %H:%M:%S") if mon_machine.date is not None else "",
                    'machine_hostname': machine.hostname if machine.hostname is not None else "",
                    'machine_jid': machine.jid if machine.jid is not None else "",
                    'machine_enabled': machine.enabled if machine.enabled is not None else "",
                    'machine_uuid': machine.uuid_inventorymachine if machine.uuid_inventorymachine is not None else "",
                    'mon_machine_statusmsg': mon_machine.statusmsg if mon_machine.statusmsg is not None else "",
                    'device_type': device.device_type if device.device_type is not None else "",
                    'device_serial': device.serial if device.serial is not None else "",
                    'device_firmware': device.firmware if device.firmware is not None else "",
                    'device_status': device.status if device.status is not None else "",
                    'device_alarm_msg': device.alarm_msg if device.alarm_msg is not None else "",
                    'device_doc': device.doc if device.doc is not None else ""
                }
                result['datas'].append(tmp)
        return result

    @DatabaseHelper._sessionm
    def get_mon_events_history(self, session, start, max, filter):
        """Get monitoring events informations
        Params:
            - sqlalchemy session: managed by DatabaseHelper._sessionm decorator
            - int start: represents the starting offset for a sql limit clause
            - int max: represents the number of result returned by the function
            - string filter: if not empty this string is searched into each event
        Returns:
            dict events: The events history found for the limit and filter clause. The
            dict has the following shape:
            result = {
                'total': 1,
                'datas' : [
                    {dict representing the event 1},
                    {dict representing the event 2},
                    ...
                ]
            }
        """

        try:
            start = int(start)
        except ValueError:
            start = -1

        try:
            max = int(max)
        except ValueError:
            max = -1

        event_types = ['log', 'ack']
        count = 0
        query = session.query(Mon_event, Mon_devices, Mon_rules, Mon_machine, Machines)\
            .outerjoin(Mon_devices, Mon_event.id_device == Mon_devices.id)\
            .outerjoin(Mon_rules, Mon_event.id_rule == Mon_rules.id)\
            .outerjoin(Mon_machine, Mon_event.machines_id == Mon_machine.id)\
            .outerjoin(Machines, Mon_machine.machines_id == Machines.id)\
            .filter(and_(
                Mon_event.status_event == 0,
                Mon_event.type_event.in_(event_types))
            )

        if filter != "":
            query = query.filter(or_(
                    Machines.hostname.contains(filter),
                    Machines.jid.contains(filter),
                    Mon_machine.date.contains(filter),
                    Mon_machine.statusmsg.contains(filter),
                    Mon_devices.alarm_msg.contains(filter),
                    Mon_rules.comment.contains(filter),
                    Mon_rules.device_type.contains(filter),
                    Mon_devices.firmware.contains(filter),
                    Mon_devices.serial.contains(filter),
                    Mon_devices.status.contains(filter),
                    Mon_event.type_event.contains(filter),
                    Mon_event.ack_user.contains(filter),
                    Mon_event.ack_date.contains(filter),
                    )
                )

        count = query.count()
        query = query.order_by(desc(Mon_machine.date))

        if start != -1:
            query = query.offset(start)
        if max != -1:
            query = query.limit(max)


        query = query.all()

        result = {
        'total': count,
        'datas': []
        }
        if query:
            for event, device, rule, mon_machine, machine in query:
                tmp = {
                    'event_id': event.id,
                    'event_status': event.status_event if event.status_event is not None else "",
                    'event_type_event': event.type_event if event.type_event is not None else "",
                    'event_cmd': event.cmd if event.cmd is not None else "",
                    'ack_user' : event.ack_user if event.ack_user is not None else "",
                    'ack_date' : event.ack_date.strftime("%m-%d-%Y %H:%M:%S") if event.ack_date is not None else "",
                    'rule_id': rule.id,
                    'rule_hostname': rule.hostname if rule.hostname is not None else "",
                    'rule_device_type': rule.device_type if rule.device_type is not None else "",
                    'rule_binding': rule.binding if rule.binding is not None else "",
                    'rule_succes_binding_cmd': rule.succes_binding_cmd if rule.succes_binding_cmd is not None else "",
                    'rule_error_on_binding': rule.error_on_binding if rule.error_on_binding is not None else "",
                    'rule_user': rule.user if rule.user is not None else "",
                    'rule_comment': rule.comment if rule.comment is not None else "",
                    'mon_machine_date': mon_machine.date.strftime("%m-%d-%Y %H:%M:%S") if mon_machine.date is not None else "",
                    'machine_hostname': machine.hostname if machine.hostname is not None else "",
                    'machine_jid': machine.jid if machine.jid is not None else "",
                    'machine_enabled': machine.enabled if machine.enabled is not None else "",
                    'machine_uuid': machine.uuid_inventorymachine if machine.uuid_inventorymachine is not None else "",
                    'mon_machine_statusmsg': mon_machine.statusmsg if mon_machine.statusmsg is not None else "",
                    'device_type': device.device_type if device.device_type is not None else "",
                    'device_serial': device.serial if device.serial is not None else "",
                    'device_firmware': device.firmware if device.firmware is not None else "",
                    'device_status': device.status if device.status is not None else "",
                    'device_alarm_msg': device.alarm_msg if device.alarm_msg is not None else "",
                    'device_doc': device.doc if device.doc is not None else ""
                }
                result['datas'].append(tmp)
        return result

    @DatabaseHelper._sessionm
    def acquit_mon_event(self, session, id, user):
        """Disables the selected event specified by its id.
        params:
            - sqlalchemy session : managed by DatabaseHelper._sessionm decorator
            - int id : monitoring event id
            - string user: user name (not used yet)
        returns:
            string "success" if the modification successed or "failure" in the other case
        """
        try:
            id = int(id)
        except:
            return "failure"
        try:
            session.query(Mon_event).filter(Mon_event.id == id)\
            .update({Mon_event.status_event: 0, Mon_event.ack_user: user, Mon_event.ack_date:datetime.now()})
            session.commit()
            session.flush()
            return "success"
        except:
            return "failure"

    @DatabaseHelper._sessionm
    def get_count_success_rate_for_dashboard(self, session):
        """
        call the stored procedure to get the deployment success rate for the 6 last weeks

        @returns:
            list of float
        """
        session.execute("call countSuccessRateLastSixWeeks(@week1, @week2, @week3, @week4, @week5, @week6)")
        query = session.execute("select @week1, @week2, @week3, @week4, @week5, @week6")
        query = query.fetchall()[0]

        return list(query)

    @DatabaseHelper._sessionm
    def get_ars_from_cluster(self, session, id, filter=""):
        result = {
            'in_cluster' : [],
            'out_cluster' :[],
            'in_ars_list' : [],
            'out_ars_list' : []
        }

        query = session.query(Has_cluster_ars.id_ars, Has_cluster_ars.id_cluster)\
            .add_column(RelayServer.nameserver)\
            .add_column(RelayServer.jid)\
            .outerjoin(RelayServer, Has_cluster_ars.id_ars == RelayServer.id)\
            .filter(Has_cluster_ars.id_cluster == id).all()

        if query is not None:
            for id_ars, id_cluster, name, jid in query:
                result['in_cluster'].append({
                    'id_ars': id_ars,
                    'id_cluster': id_cluster,
                    'name' : name,
                    'jid' : jid
                })
                result['in_ars_list'].append(id_ars)

        query2 = session.query(Has_cluster_ars.id_ars, Has_cluster_ars.id_cluster)\
            .add_column(RelayServer.nameserver)\
            .add_column(RelayServer.jid)\
            .outerjoin(RelayServer, Has_cluster_ars.id_ars == RelayServer.id)\
            .filter(not_(Has_cluster_ars.id_ars.in_(result['in_ars_list'])))\
            .filter(RelayServer.id )


        query2 = query2.all()


        if query2 is not None:
            for id_ars, id_cluster, name, jid in query2:
                result['out_cluster'].append({
                    'id_ars' : id_ars,
                    'id_cluster' : id_cluster,
                    'name' : name,
                    'jid' : jid
                })
                result['out_ars_list'].append(id_ars)
        return result

    @DatabaseHelper._sessionm
    def update_cluster(self, session, id, name, description, relay_ids):
        relay_ids = relay_ids.split(',')

        try:
            id = int(id)
            if name != "":
                query = session.query(Cluster_ars).filter(Cluster_ars.id == id)\
                    .update({Cluster_ars.name : name, Cluster_ars.description : description})
                session.commit()
                session.flush()
            else:
                query = session.query(Cluster_ars).filter(Cluster_ars == id)\
                    .update({Cluster_ars.description : description})
                session.commit()
                session.flush()

            query = session.query(Has_cluster_ars).filter(Has_cluster_ars.id_ars.in_(relay_ids))\
                .update({Has_cluster_ars.id_cluster: id}, synchronize_session='fetch')
            session.commit()
            session.flush()

        except Exception as err:
            return {'state': 'failure', 'msg':'No cluster found'}
        return {'state': 'success'}

    @DatabaseHelper._sessionm
    def create_cluster(self, session, name, description, relay_ids):
        relay_ids = relay_ids.split(',')

        try:
            if name != "":
                cluster = Cluster_ars()
                cluster.name = name
                cluster.description = description
                session.add(cluster)
                session.commit()
                session.flush()

                query = session.query(Has_cluster_ars).filter(Has_cluster_ars.id_ars.in_(relay_ids))\
                    .update({Has_cluster_ars.id_cluster: cluster.id}, synchronize_session='fetch')
                session.commit()
                session.flush()
            else:
                return {'state': 'failure', 'msg':'This cluster has no name'}

        except Exception as err:
            return {'state': 'failure', 'msg':'No cluster found'}
        return {'state': 'success'}

    @DatabaseHelper._sessionm
    def get_rules_list(self, session, start, end, filter):
        try:
            start = int(start)
        except:
            start = -1

        try:
            end = int(end)
        except:
            end = -1

        result = {
            'total' : 0,
            'datas':{
                'id' : [],
                'name' : [],
                'description' : [],
                'level' : [],
                'count' : []
            }
        }

        query = session.query(Regles).order_by(Regles.level)

        if filter != "":
            query = query.filter(or_(
                Regles.name.contains(filter),
                Regles.description.contains(filter),
                Regles.level.contains(filter)
            ))
        count = query.count()

        if start != -1 and end != -1:
            query = query.offset(start).limit(end)

        query = query.all()
        result['total'] = count
        if query is not None:
            for rule in query:
                count_rules = session.query(Has_relayserverrules.id)\
                    .filter(Has_relayserverrules.rules_id == rule.id).count()

                result['datas']['id'].append(rule.id)
                result['datas']['name'].append(rule.name)
                result['datas']['description'].append(rule.description)
                result['datas']['level'].append(rule.level)
                result['datas']['count'].append(count_rules)
        return result

    @DatabaseHelper._sessionm
    def order_relay_rule(self, session, action, id):
        try:
            id = int(id)
        except Exception as err:
            return {'status':'error', 'message': 'Invalid id'}
        if action not in ['raise', 'down']:
            return {'status':'error', 'message': 'Unknown action'}
        else:
            selected = session.query(Regles).filter(Regles.id == id).one()
            if selected is not None:
                selected_level = selected.level
                if action == "raise":
                    query = session.query(Regles)\
                        .filter(Regles.level < selected.level)\
                        .order_by(desc(Regles.level))\
                        .first()

                    if query is None:
                        return {'status':'success', 'message': 'Is top level'}
                    else:
                        new_level = query.level
                else:
                    query = session.query(Regles)\
                        .filter(Regles.level > selected.level)\
                        .order_by(Regles.level)\
                        .first()
                    if query is None:
                        return {'status':'success', 'message': 'Is lowest level'}
                    else:
                        new_level = query.level

                query.level, selected.level = selected.level, query.level

                session.commit()
                session.flush()
                if action == "raise":
                    return {'status':'success', 'message': 'raised'}
                else:
                    return {'status':'success', 'message': 'downed'}
            else:
                return {'status':'error', 'message': 'No rule found with id # %s'%id}

    @DatabaseHelper._sessionm
    def get_relay_rules(self, session, id, start, end, filter):
        try:
            start = int(start)
        except:
            start = 0
        try:
            end = int(end)
        except:
            end = -1

        result = {
            'total': 0,
            'datas' : {
                'id' : [],
                'subject' : [],
                'order' : [],
                'name' : []
            },
            'status': "error",
            'message': ""
        }
        try:
            id = int(id)
        except Exception as err:
            result['message'] = "Bad relay Id"
            return result


        query = session.query(Has_relayserverrules).filter(Has_relayserverrules.relayserver_id == id)\
            .add_column(Regles.name)\
            .join(Regles, Regles.id == Has_relayserverrules.rules_id)\
            .order_by(Has_relayserverrules.order)

        if filter != "":
            query = query.filter(or_(
                Has_relayserverrules.subject.contains(filter),
                Has_relayserverrules.order.contains(filter),
                Regles.name.contains(filter),
            ))

        result['total'] = query.count()

        if end != -1:
            query = query.offset(start).limit(end)
        else:
            query = query.offset(start)

        query = query.all()
        result["status"] = "success"
        if query is not None:
            for rule, name in query:
                result['datas']['id'].append(rule.id)
                result['datas']['subject'].append(rule.subject)
                result['datas']['order'].append(rule.order)
                result['datas']['name'].append(name)
            return result
        else:
            return result

    @DatabaseHelper._sessionm
    def new_rule_order_relay(self, session, id):
        query = session.query(Has_relayserverrules.order)\
        .filter(Has_relayserverrules.relayserver_id == id)\
        .order_by(desc(Has_relayserverrules.order))\
        .first()

        if query is not None:

            return int(query[0]) + 1
        else:
            return 0

    @DatabaseHelper._sessionm
    def add_rule_to_relay(self, session, relay_id, rule_id, order, subject):
        has_rule = Has_relayserverrules()

        has_rule.rules_id = rule_id
        has_rule.order = order
        has_rule.subject = subject
        has_rule.relayserver_id = relay_id
        try:
            session.add(has_rule)
            session.commit()
            session.flush()
            return {'status' : 'success'}
        except:
            return {'status' : 'error'}

    @DatabaseHelper._sessionm
    def delete_rule_relay(self, session, rule_id):
        try:
            rule_id = int(rule_id)
        except:
            return {'status' : 'error'}
        try:
            result = session.query(Has_relayserverrules).\
                filter(Has_relayserverrules.id == rule_id).delete()
            session.commit()
            session.flush()
            if result == 0:
                return {'status' : 'error', 'message': 'rule doesn\'t exist'}
            else:
                return {'status' : 'success'}
        except:
            return {'status' : 'error'}


    @DatabaseHelper._sessionm
    def move_relay_rule(self, session, relay_id, rule_id, action):
        result = {
            "status": None,
            "message": ""
            }

        try:
            relay_id = int(relay_id)
        except:
            result['status'] = "error"
            result['message'] = "wrong relay id"
            return result

        try:
            rule_id = int(rule_id)
        except:
            result['status'] = "error"
            result['message'] = "wrong rule id"
            return result

        # Get the selected rule
        rule = session.query(Has_relayserverrules)\
            .filter(Has_relayserverrules.id == rule_id).one()

        if rule is not None:
            if action == "raise":
                selected = session.query(Has_relayserverrules)\
                    .filter(Has_relayserverrules.order < rule.order)\
                    .order_by(desc(Has_relayserverrules.order)).first()

            elif action == "down":
                selected = session.query(Has_relayserverrules)\
                    .filter(Has_relayserverrules.order > rule.order)\
                    .order_by(Has_relayserverrules.order).first()
            else:
                result['status'] = "error"
                result['message'] = "bad action"
                return result

            if selected is not None:
                selected.order, rule.order = rule.order, selected.order
                session.commit()
                session.flush()

                result['status'] = "success"
                result['message'] = "%sed"%action
            else:
                result['status'] = "success"
                result['message'] = "reached top level" if action == "raise" else "reached last level"
            return result

        else:
            result['status'] = "error"
            result['message'] = "No rule found"
            return result

    @DatabaseHelper._sessionm
    def get_relay_rule(self, session, rule_id):
        result = {
            'status': None,
            'massage' : ''
        }
        try:
            rule_id = int(rule_id)
        except:
            result['status'] = "error"
            result['message'] = "bad rule id"
            return result

        query = session.query(Has_relayserverrules)\
            .filter(Has_relayserverrules.id == rule_id).first()

        if query is not None:
            has_rule = query
            result['datas'] = {
                'id' : query.id,
                'rules_id' : query.rules_id,
                'order' : query.order,
                'relayserver_id': query.relayserver_id,
                'subject' : query.subject
            }
            result['status'] = 'success'
            result['message'] = ""
        else:
            result['status'] = "error"
            result['message'] = "no rule found"

        return result


    @DatabaseHelper._sessionm
    def get_relays_for_rule(self, session, rule_id, start, end, filter=""):
        result = {
            'status': None,
            'massage' : '',
            'total' : 0,
            'datas':{
                'relay_id': [],
                'hostname': [],
                'order': [],
                'subject': [],
                'id' : [],
                'rule_id': [],
                'enabled': []
            }
        }
        try:
            rule_id = int(rule_id)
        except:
            result['status'] = "error"
            result['message'] = "bad rule id"
            return result

        try:
            start = int(start)
        except:
            result['status'] = "error"
            result['message'] = "bad start offset"
            return result
        try:
            end = int(end)
        except:
            result['status'] = "error"
            result['message'] = "bad end limit"
            return result


        query = session.query(Has_relayserverrules, RelayServer)\
            .filter(and_(Has_relayserverrules.rules_id == rule_id,
                RelayServer.moderelayserver == "static"))\
            .join(RelayServer, RelayServer.id == Has_relayserverrules.relayserver_id)

        if filter != "":
            query = query.filter(or_(
                RelayServer.id.contains(filter),
                RelayServer.nameserver.contains(filter),
                Has_relayserverrules.order.contains(filter),
                Has_relayserverrules.subject.contains(filter)
            ))
        count = query.count()
        query = query.order_by(RelayServer.nameserver)\
            .offset(start).limit(end)
        query = query.all()

        result['total'] = count

        if query is not None:
            for rule, relay in query:
                result['datas']['id'].append(rule.id)
                result['datas']['rule_id'].append(rule.rules_id)
                result['datas']['relay_id'].append(relay.id)
                result['datas']['hostname'].append(relay.nameserver)
                result['datas']['enabled'].append(relay.enabled)
                result['datas']['order'].append(rule.order)
                result['datas']['subject'].append(rule.subject)

            result['status'] = 'success'
            result['message'] = ""
        else:
            result['status'] = "error"
            result['message'] = "no rule found"

        return result

    @DatabaseHelper._sessionm
    def edit_rule_to_relay(self, session, id, relay_id, rule_id, subject):
        result = {
            "status" : None,
            "message" : ""
        }

        try:
            id = int(id)
        except:
            result['status'] = 'error'
            result['message'] = "bad id"
            return result

        try:
            relay_id = int(relay_id)
        except:
            result['status'] = 'error'
            result['message'] = "bad relay id"
            return result

        try:
            rule_id = int(rule_id)
        except:
            result['status'] = 'error'
            result['message'] = "bad rule_id"
            return result

        query = session.query(Has_relayserverrules)\
            .filter(Has_relayserverrules.id == id).first()

        if query is None:
            result['status'] = 'error'
            result['message'] = "no rule found"
        else:
            query.rules_id = rule_id
            if subject != "":
                query.subject = subject

            query.relayserver_id = relay_id

            session.commit()
            session.flush()

            result['status'] = 'success'
            result['message'] = "rule edited"

        return result

    @DatabaseHelper._sessionm
    def get_minimal_relays_list(self, session, mode):
        query = session.query(RelayServer.id, RelayServer.nameserver)
        if mode in ['static', 'dynamic']:
            query = query.filter(RelayServer.moderelayserver == mode)
        else:
            query = query.filter(RelayServer.moderelayserver == "static")
        query = query.order_by(RelayServer.nameserver)
        query = query.all()

        result = {
        'id': [],
        'hostname': []
        }

        if query is not None:
            for id, hostname in query:
                result['id'].append(id)
                result['hostname'].append(hostname)
        return result

    @DatabaseHelper._sessionm
    def get_count_total_deploy_for_dashboard(self, session):
        """Get the total of deployments for each last six months
            Returns: list of deployments
        """
        session.execute("call countDeployLastSixMonths()")
        query = session.execute("select @month6, @month5, @month4, @month3, @month2, @month1")
        query = query.fetchall()[0]
        return list(query)

    @DatabaseHelper._sessionm
    def get_count_agent_for_dashboard(self, session):
        session.execute("call countAgentsLastSixMonths()")
        query = session.execute("select @month6, @month5, @month4, @month3, @month2, @month1")
        query = query.fetchall()[0]
        return list(query)



    @DatabaseHelper._sessionm
    def get_ars_group_in_list_clusterid(self,
                                        session,
                                        clusterid,
                                        enabled=None):
        """
        This function is used to get the list of the ars from a cluster.

        Args:
            session: the SQLAlchemy session
            clusterid: the id of the used cluster
            enabled: Tell if we used enabled ars only
                     If None we do not use enabled in the SQL request
        Returns:
            It returns informations from the ars of a cluster
            like jid, name, classutil, enabled, etc.
        """
        setsearch = clusterid
        if isinstance(clusterid, list):
            listidcluster = [x for x in set(clusterid)]
            if listidcluster:
                setsearch=("%s" % listidcluster)[1:-1]
            else:
                raise
        searchclusterars = "(%s)" % setsearch

        sql ="""SELECT
                    relayserver.id AS ars_id,
                    relayserver.urlguacamole AS urlguacamole,
                    relayserver.subnet AS subnet,
                    relayserver.nameserver AS nameserver,
                    relayserver.ipserver AS ipserver,
                    relayserver.ipconnection AS ipconnection,
                    relayserver.port AS port,
                    relayserver.portconnection AS portconnection,
                    relayserver.mask AS mask,
                    relayserver.jid AS jid,
                    relayserver.longitude AS longitude,
                    relayserver.latitude AS latitude,
                    relayserver.enabled AS enabled,
                    relayserver.mandatory AS mandatory,
                    relayserver.switchonoff AS switchonoff,
                    relayserver.classutil AS classutil,
                    relayserver.groupdeploy AS groupdeploy,
                    relayserver.package_server_ip AS package_server_ip,
                    relayserver.package_server_port AS package_server_port,
                    relayserver.moderelayserver AS moderelayserver,
                    relayserver.keysyncthing AS keysyncthing,
                    relayserver.syncthing_port AS syncthing_port,
                    has_cluster_ars.id_cluster AS id_cluster,
                    cluster_ars.name AS name_cluster
                FROM
                    xmppmaster.relayserver
                        INNER JOIN
                    xmppmaster.has_cluster_ars ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                        INNER JOIN
                    xmppmaster.cluster_ars ON xmppmaster.cluster_ars.id = xmppmaster.has_cluster_ars.id_cluster
                WHERE
                    id_cluster IN %s """ % (searchclusterars)
        if enabled is not None:
            sql += """AND `relayserver`.`enabled` = %s""" % enabled
        sql += ";"
        clusterList = session.execute(sql)
        session.commit()
        session.flush()
        arsListInfos = []
        for ars in clusterList:
            arsInfos = {"ars_id": ars[0],
                       "urlguacamole": ars[1],
                       "subnet": ars[2],
                       "nameserver": ars[3],
                       "ipserver": ars[4],
                       "ipconnection": ars[5],
                       "port": ars[6],
                       "portconnection": ars[7],
                       "mask": ars[8],
                       "jid": ars[9],
                       "longitude": ars[10],
                       "latitude": ars[11],
                       "enabled": ars[12],
                       "mandatory": ars[13],
                       "switchonoff": ars[14],
                       "classutil": ars[15],
                       "groupdeploy": ars[16],
                       "package_server_ip": ars[17],
                       "package_server_port": ars[18],
                       "moderelayserver": ars[19],
                       "keysyncthing": ars[20],
                       "syncthing_port": ars[21],
                       "id_cluster": ars[22],
                       "name_cluster": ars[23]}
            arsListInfos.append(arsInfos)
        return arsListInfos
