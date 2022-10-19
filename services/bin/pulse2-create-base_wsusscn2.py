#!/usr/bin/python3
# -*- coding:utf-8 -*-
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
#
# file : cow.py
# prerequisite pacquage a installer
#  python3-scrapy python3-tqdm python3-lxml python3-mysqldb cabextract python3-py7zr libxml2-utils

# python2
#apt install libxml2-utils cabextract p7zip python-scrapy python-mysqldb python-lxml python-tqdm


# des information a remonter depuis l agent
###  version de .net  \HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full
#version edge powershell.exe "(Get-AppxPackage Microsoft.MicrosoftEdge).Version"

#version de mrt.exec  (voir meta data)
        #(Get-ChildItem 'C:\Windows\System32\mrt.exe').VersionInfo | Format-List *
        #(Get-ChildItem 'C:\Windows\System32\mrt.exe').VersionInfo.ProductVersion


from datetime import datetime

from scrapy import Selector
from tqdm import tqdm
import requests
import math
import re
import sqlite3
import subprocess
import sys, os
import tempfile
import xml.etree.ElementTree as ET
import time
import signal
import logging
import traceback
import configparser
# from lxml import etree

from lxml import etree

import MySQLdb


logger = logging.getLogger()


def simplecommand(cmd):
    obj = {}
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    obj["code"] = p.wait()
    obj["result"] = result
    return obj


def simplecommandstr(cmd):
    obj = {}
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    obj["code"] = p.wait()
    obj["result"] = "\n".join(result)
    return obj

def test_executable():
    """verify executable"""
    exec_extract = {}
    res = simplecommand("which cabextract 7z")
    if res["code"] == 0:
        for t in res["result"]:
            if "cabextract" in t.decode('utf-8'):
                exec_extract["cabextract"] = t.decode('utf-8').strip()
            if "7z" in t.decode('utf-8'):
                exec_extract["7z"] = t.decode('utf-8').strip()
        return exec_extract
    return ""

class extract_cab:
    CONF_FILE="/etc/mmc/plugins/pulse2-create-base_wsusscn2.init"
    def __init__(self):
        self.insertion_in_base=0
        self.exist_in_base=0
        self.read_config()
        #self.name_file = path_file_extract
        self.file_extract = os.path.join(self.directory_output, self.name_file_wsu)
        self.exec_extract = {}
        self.rangestart = []
        res = simplecommand("which cabextract 7z")
        if res["code"] == 0:
            for t in res["result"]:
                if "cabextract" in t.decode('utf-8'):
                    self.exec_extract["cabextract"] = t.decode('utf-8').strip()
                if "7z" in t.decode('utf-8'):
                    self.exec_extract["7z"] = t.decode('utf-8').strip()
        if not os.path.exists(self.directory_output):
            os.makedirs(self.directory_output)

        self.pk1 = os.path.join(self.directory_output, "package1.xml")
        self.ind1 = os.path.join(self.directory_output, "index1.xml")
        self.pk = os.path.join(self.directory_output, "package.xml")
        self.ind = os.path.join(self.directory_output, "index.xml")

    def create_connection(self):
        try:
            logger.debug("connection base de donne")
            self.db = MySQLdb.connect(
                host=self.host,
                user=self.user,
                port=int(self.port),
                passwd=self.passwd,
                db=self.NAME_BASE
            )
            #cursor = self.db.cursor()
        except Exception as e:
            print("\n%s" % (traceback.format_exc()))
            return False
        return self.create_table()

    def read_config(self):
        self.host = "localhost"
        self.user = "mmc"
        self.port = "3307"
        self.passwd = "mmc"
        self.url = "http://go.microsoft.com/fwlink/?linkid=74689"
        self.NAME_BASE="base_wsusscn2"
        self.NAME_TABLE="update_data"
        self.NAME_UPDATE_TABLE="data_simple_update"
        self.name_file_wsu="wsusscn2.cab"
        if os.path.exists(self.CONF_FILE):
            Config = configparser.ConfigParser()
            Config.read(self.CONF_FILE)
            #charge config
            if Config.has_option('connection', 'host'):
                self.host = Config.get('connection', 'host')

            if Config.has_option('connection', 'user'):
                self.user = Config.get('connection', 'user')

            if Config.has_option('connection', 'port'):
                self.port = Config.get('connection', 'port')

            if Config.has_option('connection', 'password'):
                self.passwd = Config.get('connection', 'password')

            if Config.has_option('main', 'url'):
                self.url = Config.get('main', 'url')

            if Config.has_option('main', 'directory_output'):
                self.directory_output = Config.get('main', 'directory_output')

            if Config.has_option('main', 'NAME_BASE'):
                self.NAME_BASE = Config.get('main', 'NAME_BASE')

            if Config.has_option('main', 'NAME_TABLE'):
                self.NAME_TABLE = Config.get('main', 'NAME_TABLE')

            if Config.has_option('main', 'NAME_UPDATE_TABLE'):
                self.NAME_UPDATE_TABLE = Config.get('main', 'NAME_UPDATE_TABLE')

            if Config.has_option('main', 'name_file_wsu'):
                self.name_file_wsu = Config.get('main', 'name_file_wsu')

    def create_table(self):
        print ("cretion tables")
        self.create_table_wsu()
        self.create_table_update_wsu()
        return True

    def create_table_wsu(self):
        print ("creation table %s"%self.NAME_TABLE)
        try:
            cursor = self.db.cursor()
            cmd="""CREATE TABLE IF NOT EXISTS %s (
                `updateid` varchar(38) NOT NULL,
                `revisionid` varchar(16) NOT NULL,
                `creationdate` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
                `compagny` varchar(36) DEFAULT '',
                `product` varchar(512) DEFAULT '',
                `productfamily` varchar(100) DEFAULT '',
                `updateclassification` varchar(36) DEFAULT '',
                `prerequisite` varchar(2000) DEFAULT '',
                `title` varchar(500) DEFAULT '',
                `description` varchar(2048) DEFAULT '',
                `msrcseverity` varchar(16) DEFAULT '',
                `msrcnumber` varchar(16) DEFAULT '',
                `kb` varchar(16) DEFAULT '',
                `languages` varchar(16) DEFAULT '',
                `category` varchar(80) DEFAULT '',
                `supersededby` varchar(2048) DEFAULT '',
                `supersedes` text DEFAULT NULL,
                `payloadfiles` varchar(1024) DEFAULT '',
                `revisionnumber` varchar(30) DEFAULT '',
                `bundledby_revision` varchar(30) DEFAULT '',
                `isleaf` varchar(6) DEFAULT '',
                `issoftware` varchar(30) DEFAULT '',
                `deploymentaction` varchar(30) DEFAULT '',
                `title_short` varchar(500) DEFAULT '',
                    PRIMARY KEY (`updateid`),
                    UNIQUE KEY `id_UNIQUE` (`updateid`),
                    UNIQUE KEY `id_UNIQUE1` (`revisionid`),
                    KEY `indproduct` (`product`(512)),
                    KEY `indkb` (`kb`),
                    KEY `indclassification` (`updateclassification`),
                    KEY `ind_remplacerpar` (`supersededby`(768)),
                    KEY `indcategory` (`category`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  ;"""%(self.NAME_TABLE)
            cursor.execute(cmd)
            return True
        except Exception as e:
            print("\n%s" % (traceback.format_exc()))
            return False

    def create_table_update_wsu(self):
        print ("cretion table %s"%self.NAME_UPDATE_TABLE)
        try:
            cursor = self.db.cursor()
            cmd="""CREATE TABLE  IF NOT EXISTS `%s`(
                `updateid` varchar(38) NOT NULL COMMENT 'creationdate',
                `creationdate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
                `updateclassification` text DEFAULT NULL,
                `category` text DEFAULT NULL,
                `title` text DEFAULT NULL,
                `description` text DEFAULT NULL,
                `kb` text DEFAULT NULL,
                `msrcseverity` text DEFAULT NULL,
                `msrcnumber` text DEFAULT NULL,
                PRIMARY KEY (`updateid`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""%(self.NAME_UPDATE_TABLE)
            cursor.execute(cmd)
            return True
        except Exception as e:
            print("\n%s" % (traceback.format_exc()))
            return False


    def update(self):
        if self.create_connection():
            if not (os.path.exists(self.pk) and os.path.exists(self.ind)):
                self.decompacte_wsusscn2()
                self.decompresse_all_cab()

            self.update_data()
            self.exportdb()

    def exportdb(self, output_file="MSPatches.csv"):
        """
        generation cvs file
        """
        if not output_file:
            output_file="MSPatches.csv"

        fileout = open(output_file, "w")
        fileout.write(
            '"Update ID","Creation Date","Update Classification","Title","Description","KB ID","MSRC Severity","MSRC Number"\n'
        )
        if self.create_connection():
            cursor = self.db.cursor()
        else:
            print("connection error")
            return


        dde = "select updateid,creationdate,updateclassification,title,description,kb,msrcseverity,msrcnumber from %s where updateclassification not in ('') order by creationdate desc;"%(self.NAME_TABLE)

        record = cursor.execute(dde)

        for i in cursor.fetchall():
            cursor1 = self.db.cursor()
            dda="select title from "+self.NAME_TABLE+" where updateid='" + i[2] + "';"
            if cursor1.execute(dda):
                updateclassification = cursor1.fetchone()[0]
                cursor1.close()
                datetimeupdate = i[1].strftime("%m/%d/%Y, %H:%M:%S")
                fileout.write(
                    '"'
                    + i[0]
                    + '","'
                    + datetimeupdate
                    + '","'
                    + updateclassification
                    + '","'
                    + i[3]
                    + '","'
                    + i[4]
                    + '","'
                    + i[5]
                    + '","'
                    + i[6]
                    + '","'
                    + i[7]
                    + '"'
                    + "\n"
                )

                self.write_table_update_wsu(
                                        i[0],
                                        datetimeupdate,
                                        i[2],
                                        updateclassification,
                                        i[3],
                                        i[4],
                                        i[5],
                                        i[6],
                                        i[7])
        fileout.close()
        print("\n \n DB Exported as CSV sucessfully [%s]!!"%output_file)

    def write_table_update_wsu( self,
                                updateid,
                                creationdate,
                                updateclassification,
                                category,
                                title,
                                description,
                                kb,
                                msrcseverity,
                                msrcnumber ):
        try:
            cursor = self.db.cursor()
            cmd="""INSERT INTO `%s`.`%s` ( `updateid`,
                        `creationdate`,
                        `updateclassification`,
                        `category`,
                        `title`,
                        `description`,
                        `kb`,
                        `msrcseverity`,
                        `msrcnumber`)
                        VALUES ( '%s', '%s', '%s','%s','%s', '%s', '%s', '%s','%s');""" %(self.NAME_BASE,
                                self.NAME_UPDATE_TABLE,
                                updateid,
                                creationdate,
                                MySQLdb.escape_string(updateclassification),
                                category,
                                MySQLdb.escape_string(title),
                                MySQLdb.escape_string(description),
                                kb,
                                msrcseverity,
                                msrcnumber )
            cursor.execute(cmd)
            self.db.commit()
        except MySQLdb.IntegrityError as e:
            if "Duplicate entry" in e[1]:
                pass
            else:
                print("\n%s" % (traceback.format_exc()))
        except Exception as e:
            print("\n%s" % (traceback.format_exc()))

        finally:
            cursor.close()

    def decompresse_all_cab(self):
        onlyfiles = [f for f in os.listdir(self.directory_output) if f.endswith(".cab")]
        onlyfiles.remove(self.name_file_wsu)
        self.list_dir = {}
        for t in onlyfiles:
            if t.endswith(".cab"):
                fnamedir = t[:-4]
                fndir = os.path.join(self.directory_output, fnamedir)
                repfn = os.path.join(self.directory_output, t)
                self.list_dir[t] = fndir
                if not os.path.isdir(fndir):
                    # print ("creation directory %s" % self.directory_output )
                    os.makedirs(fndir)
                    cmd = '%s -d "%s" "%s"' % (
                        self.exec_extract["cabextract"],
                        fndir,
                        repfn,
                    )
                    print("cmd %s" % cmd)
                    res = simplecommand(cmd)
                    os.remove(repfn)

    def human_file(self):
        cmd = 'xmllint --format "%s" > "%s"' % (self.pk, self.pk1)
        cmd1 = 'xmllint --format "%s" > "%s"' % (self.ind, self.ind1)

        os.system(cmd)
        os.system(cmd1)

        os.system('mv "%s" "%s"' % (self.ind1, self.ind))
        os.system('mv "%s" "%s"' % (self.pk1, self.pk))
        if os.path.exists(self.pk1):
            os.remove(self.pk1)
        ###  supprime namespace pour minimiser les chaine

        if os.path.exists(self.ind1):
            os.remove(self.ind1)

    def decompacte_wsusscn2(self):
        if not os.path.exists(self.file_extract):
            try:
                self.download_cab()
            except requests.exceptions.ConnectionError as e:
                print ("connection microsoft erreur")
                print ("%s"% e )
                sys.exit(-1)
        if not os.path.exists(self.pk):
            cmd = '%s -d "%s" "%s"' % (
                self.exec_extract["cabextract"],
                self.directory_output,
                self.file_extract,
            )
            print("cmd %s" % cmd)
            res = simplecommand(cmd)
            if res["code"] == 0:
                self.package_cab = os.path.join(self.directory_output, "package.cab")
                cmd = '%s -d "%s" "%s"' % (
                    self.exec_extract["cabextract"],
                    self.directory_output,
                    self.package_cab,
                )
                print("cmd %s" % cmd)
                res = simplecommand(cmd)
                if res["code"] == 0:
                    os.remove(self.package_cab)
                else:
                    print("error deconpactage package.cab")
                    return False
            else:
                print("error deconpactage cab [%s]" % cmd)
                return False
            print("HUMAN FILE")
            self.human_file()
            return True

    def download_cab(self):
        if not os.path.isdir(self.directory_output):
            print("creation directory %s" % self.directory_output)
            os.makedirs(self.directory_output)
        if not os.path.exists(self.file_extract):
            print(
                "\n\nThis is going to take some time. Please be patient .... \n\nGrabbing a cup of coffee might be a good idea right now !! :P \n\nStep 1 out of 4 :- Downloading Official WSUS Update Cab File\n\n"
            )
            #url = "http://go.microsoft.com/fwlink/?linkid=74689"
            r = requests.get(self.url, stream=True)
            total_size = int(r.headers.get("content-length", 0))
            block_size = 1024
            wrote = 0
            with open(self.file_extract, "wb") as f:
                for data in tqdm(
                    r.iter_content(block_size),
                    total=math.ceil(total_size // block_size),
                    unit="KB",
                    unit_scale=True,
                ):
                    wrote = wrote + len(data)
                    f.write(data)

            if total_size != 0 and wrote != total_size:
                print("ERROR, something went wrong")
        return True


    def determination_range_in_file(self):
        root = etree.parse(os.path.join(self.directory_output, "index.xml"))
        # e=[ {"name" : int(b.attrib['NAME'][7:-4]), "rangestart": b.attrib['RANGESTART'] } for b in root.iterfind(".//CAB") if 'RANGESTART' in b.attrib ]
        self.rangestart = [
            int(b.attrib["RANGESTART"])
            for b in root.iterfind(".//CAB")
            if "RANGESTART" in b.attrib
        ]
        print(self.rangestart)

    def file_contient(self, nbrange, createfile=False):
        if len(self.rangestart) == 0:
            self.determination_range_in_file()
        choix = len(self.rangestart) + 1
        if nbrange < int(self.rangestart[-1]):
            for i in enumerate(self.rangestart):
                if int(nbrange) < int(i[1]):
                    choix = int(i[0]) + 1
                    break
        fileextract={}
        rep=os.path.join(self.directory_output, "package%s" % choix)
        c=os.path.join(rep, "c", str(nbrange))
        l=os.path.join(rep, "l", "en", str(nbrange))
        s=os.path.join(rep, "s",  str(nbrange))
        x=os.path.join(rep, "x",  str(nbrange))
        out=os.path.join(rep, "%s.xml" % str(nbrange))

        filenames=[]

        if  os.path.exists(c):
            filenames.append(c)
            fileextract["supersedes_file"]=c

        if  os.path.exists(l):
            fileextract["title_description_file"]=l
            filenames.append(l)
        if  os.path.exists(s):
            fileextract["msrcnumber_msrcseverity_kb_languages_file"]=s
            filenames.append(s)
        if  os.path.exists(x):
            fileextract["categoryfile"]=x
            filenames.append(x)
        stringconcat_ascii="<concat>"
        for name in filenames:
            with open(name) as f:
                stringconcat_ascii += f.read()

        stringconcat_ascii += "</concat>"
        stringconcat_ascii = re.sub(
                r"[^\x00-\x7f]",
                "",
                stringconcat_ascii.replace("\n", "").replace("\r", "").replace("\t", "").strip(" "))

        #print( "creation file %s" % out)
        with open(out, "w") as new_file:
            new_file.write(stringconcat_ascii)

        return stringconcat_ascii


    def normalize_attr(self, root):
        for attr, value in root.attrib.items():
            norm_attr = attr.lower()
            if norm_attr != attr:
                root.set(norm_attr, value)
                root.attrib.pop(attr)

    def update_data(self):
        os.system(
            """sed -i -e 's@xmlns="http://schemas.microsoft.com/msus/2004/02/OfflineSync"@@' "%s" """
            % (self.pk)
        )
        root = etree.parse(os.path.join(self.directory_output, "package.xml"))
        cursor = self.db.cursor()

        for element_update in root.iterfind(".//Updates/Update"):
            #print ("kkkk%s"%element_update)
            #return
            att = element_update.attrib
            #print (att)
            fileinstall = element_update.find("PayloadFiles/File")
            payloadfiles=""
            if fileinstall is not None:
                payloadfiles = fileinstall.get("Id","")

            BundledBysearch= element_update.find("BundledBy/Revision")
            bundledby_revision=""
            if BundledBysearch is not None:
                bundledby_revision=BundledBysearch.get("Id","")
            creationdate=""
            creationdate= att["CreationDate"]
            if len(creationdate) == 20:
                creationdate = re.sub("[a-zA-Z]", " ", creationdate[:-1])

            revisionnumber=""
            revisionnumber= att["RevisionNumber"]
            isleaf=""
            if "IsLeaf" in att:
                isleaf = att["IsLeaf"]
            issoftware=""
            if "IsSoftware" in att:
                issoftware = att["IsSoftware"]
            deploymentaction=""
            if "DeploymentAction" in att:
                deploymentaction = att["DeploymentAction"]

            UpdateId = att["UpdateId"]
            RevisionId = att["RevisionId"]

            try:
                sql = 'select updateid from %s where updateid="%s";' % (
                    self.NAME_TABLE,
                    att["UpdateId"],
                )
                # print (sql)
                cursor.execute(sql)
                results = cursor.fetchall()
                if results:
                    self.exist_in_base+=1
                    continue
            except Exception as e:
                print("\n%s" % (traceback.format_exc()))
                continue

            Prerequisitel = []
            for Prerequisites in element_update.iterfind(".//UpdateId"):
                self.normalize_attr(Prerequisites)
                Prerequisitel.append(Prerequisites.attrib["id"])

            Supersededbyl = []
            for SupersededBy in element_update.iterfind(".//Revision"):
                self.normalize_attr(SupersededBy)
                Supersededbyl.append(SupersededBy.attrib["id"])

            Compagny = []
            Product = []
            ProductFamily = []
            UpdateClassification = []
            for Categories in element_update.iterfind(".//Category"):

                self.normalize_attr(Categories)
                typea = Categories.attrib["type"]


                if typea.endswith("t"):
                    Product.append(Categories.attrib["id"])
                elif typea.startswith("C"):
                    Compagny.append(Categories.attrib["id"])
                elif typea.startswith("U"):
                    UpdateClassification.append(Categories.attrib["id"])
                elif typea.endswith("y"):
                    ProductFamily.append(Categories.attrib["id"])


            supersededby=Category_Compagny=Category_Product=Category_ProductFamily=Category_UpdateClassification=prerequisites=title=description=moreinfourl=supersedes=""

            Category_Compagny=",".join(Compagny)
            Category_Product=",".join(Product)
            Category_ProductFamily=",".join(ProductFamily)
            Category_UpdateClassification=",".join(UpdateClassification)
            prerequisites=",".join(Prerequisitel)
            supersededby=",".join(Supersededbyl)
            #print("supersededby %s" % supersededby)
            try:
                #print("supersededby %s" % supersededby)
                revisiondata = element_update.attrib["RevisionId"]

                filexmlreisonid = self.file_contient(
                    int(revisiondata)
                )

                root1 = etree.fromstring(filexmlreisonid)
            except Exception as e:
                print (str(e))
                print ("error creation file RevisionId %s" %RevisionId)
                continue
            try:
                Title = root1.find("LocalizedProperties/Title")
                title = Title.text
            except:
                # pas de title
                pass

            try:
                Description = root1.find("LocalizedProperties/Description")
                description=Description.text
            except:
                pass

            try:
                Moreinfourl = root1.find("LocalizedProperties/MoreInfoUrl")
                moreinfourl=Moreinfourl.text
            except:
                pass

            Supersedes=[]
            for Upid in root1.iterfind(".//SupersededUpdates/UpdateIdentity"):
                self.normalize_attr(Upid)
                if "updateid" in Upid.attrib:
                    Supersedes.append(Upid.attrib["updateid"])

            supersedes=",".join(Supersedes)

            defaultpropertieslanguage=msrcseverity=isbeta=kbarticleid=securitybulletinid = ""
            ExtendedProperties = root1.find("ExtendedProperties")
            self.normalize_attr(ExtendedProperties)
            if "defaultpropertieslanguage" in ExtendedProperties.attrib:
                defaultpropertieslanguage = ExtendedProperties.attrib['defaultpropertieslanguage']
            if "msrcseverity" in ExtendedProperties.attrib:
                msrcseverity = ExtendedProperties.attrib['msrcseverity']
            if "isbeta" in ExtendedProperties.attrib:
                isbeta = ExtendedProperties.attrib['isbeta']

            try:
                KBArticleID = ExtendedProperties.find("KBArticleID")
                kbarticleid=KBArticleID.text
            except:
                pass

            try:
                SecurityBulletinID = ExtendedProperties.find("SecurityBulletinID")
                securitybulletinid=SecurityBulletinID.text
            except:
                pass

            categorytype=""
            try:
                Categoryinformation = root1.find("HandlerSpecificData/CategoryInformation")
                self.normalize_attr(Categoryinformation)
                if "categorytype" in Categoryinformation.attrib:
                    categorytype = Categoryinformation.attrib['categorytype']
            except:
                pass

            if payloadfiles:
                pathcalcule="/OfflineSyncPackage/FileLocations/FileLocation[@Id='%s']/@Url"%payloadfiles
                eee= root.xpath(pathcalcule)
                payloadfiles = eee[0]


            if not creationdate:
                try:
                    cmd="""INSERT INTO `%s`.`%s` ( `updateid`,
                    `revisionid`,
                    `compagny`,
                    `product`,
                    `productfamily`,
                    `updateclassification`,
                    `prerequisite`,
                    `title`,
                    `description`,
                    `msrcseverity`,
                    `msrcnumber`,
                    `kb`,
                    `languages`,
                    `category`,
                    `supersededby`,
                    `supersedes`,
                    `payloadfiles`,
                    `revisionnumber`,
                    `bundledby_revision`,
                    `isleaf`,
                    `issoftware`,
                    `deploymentaction`
                    ) VALUES ( '%s', '%s',  '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' , '%s', '%s');""" %(self.NAME_BASE,
                        self.NAME_TABLE,
                        UpdateId,
                        RevisionId,
                        MySQLdb.escape_string(Category_Compagny).decode('utf-8'),
                        MySQLdb.escape_string(Category_Product).decode('utf-8'),
                        MySQLdb.escape_string(Category_ProductFamily).decode('utf-8'),
                        MySQLdb.escape_string(Category_UpdateClassification).decode('utf-8'),
                        MySQLdb.escape_string(prerequisites).decode('utf-8'),
                        MySQLdb.escape_string(title).decode('utf-8'),
                        MySQLdb.escape_string(description).decode('utf-8'),
                        msrcseverity,
                        securitybulletinid,
                        kbarticleid,
                        defaultpropertieslanguage,
                        categorytype,
                        supersededby,
                        supersedes,
                        payloadfiles,
                        revisionnumber,
                        bundledby_revision,
                        isleaf,
                        issoftware,
                        deploymentaction
                        )
                    #print (cmd)
                    cursor.execute(cmd)
                    self.db.commit()
                    self.insertion_in_base+=1
                except Exception as e:
                    print("\n%s" % (traceback.format_exc()))
            else:
                try:
                    cmd="""INSERT INTO `%s`.`%s` ( `updateid`,
                    `creationdate`,
                    `revisionid`,
                    `compagny`,
                    `product`,
                    `productfamily`,
                    `updateclassification`,
                    `prerequisite`,
                    `title`,
                    `description`,
                    `msrcseverity`,
                    `msrcnumber`,
                    `kb`,
                    `languages`,
                    `category`,
                    `supersededby`,
                    `supersedes`,
                    `payloadfiles`,
                    `revisionnumber`,
                    `bundledby_revision`,
                    `isleaf`,
                    `issoftware`,
                    `deploymentaction`
                    ) VALUES ( '%s', '%s', '%s','%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' , '%s', '%s');""" %(self.NAME_BASE,
                        self.NAME_TABLE,
                        UpdateId,
                        creationdate,
                        RevisionId,
                        MySQLdb.escape_string(Category_Compagny).decode('utf-8'),
                        MySQLdb.escape_string(Category_Product).decode('utf-8'),
                        MySQLdb.escape_string(Category_ProductFamily).decode('utf-8'),
                        MySQLdb.escape_string(Category_UpdateClassification).decode('utf-8'),
                        MySQLdb.escape_string(prerequisites).decode('utf-8'),
                        MySQLdb.escape_string(title).decode('utf-8'),
                        MySQLdb.escape_string(description).decode('utf-8'),
                        msrcseverity,
                        securitybulletinid,
                        kbarticleid,
                        defaultpropertieslanguage,
                        categorytype,
                        supersededby,
                        supersedes,
                        payloadfiles,
                        revisionnumber,
                        bundledby_revision,
                        isleaf,
                        issoftware,
                        deploymentaction
                        )
                    #print (cmd)
                    cursor.execute(cmd)
                    self.db.commit() #  300 self.insertiaxe o(n_in_base+=1
                except Exception as e:
                    print("\n%s" % (traceback.format_exc()))

        cursorproc = self.db.cursor()
        cursorproc.execute("call update_updateclassification();")
        cursorproc.execute("call update_updatecompagny();")
        cursorproc.execute("call update_updateproductfamily();")
        cursorproc.execute("call update_update_product();")
        cursorproc.execute("call update_update_remplaces();")
        cursorproc.execute("call update_datetime();")
        self.db.commit()

def help():

    print(
        r"""Usage:-
    %s  update - Updates the local patch database (Requires Internet Connection and some patience !! :P)
    %s  help  -  Displays this help

    eg: sudo nice -6 python3 %s update""" %(sys.argv[0], sys.argv[0], sys.argv[0])
    )


if __name__ == "__main__":

    # Quit the process if we don't want to continue
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

    executable = {}
    file_handler = logging.FileHandler(filename='tmp.log')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers
    )

    logger = logging.getLogger('UPDATE')
    argc = sys.argv.__len__()
    if argc == 1:
        help()
        sys.exit(1)
    logger.debug("start programe %s" % sys.argv[1])

    executable = test_executable()
    if len(executable) != 2:
        print(
            "7z or cabextract file not found.\n\nCUW cannot function without these dependencies.\n\nPlease install cabextract and 7z [%s]"
            % executable
        )
        sys.exit(1)

    if argc == 2:
        if sys.argv[1] == "update":
            print("UPDATE BASE")
            dd = extract_cab()
            dd.update()
        else :
            help()

