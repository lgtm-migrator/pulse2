#!/usr/bin/python
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


###  version de .net  \HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full
#version edge powershell.exe "(Get-AppxPackage Microsoft.MicrosoftEdge).Version"

#version de mrt.exec  (voir meta data)
        #(Get-ChildItem 'C:\Windows\System32\mrt.exe').VersionInfo | Format-List *
        #(Get-ChildItem 'C:\Windows\System32\mrt.exe').VersionInfo.ProductVersion



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
import ConfigParser
# from lxml import etree

from lxml import etree

import MySQLdb

#from  MySQLdb import IntegrityError
# Global Variables

list_name_cab = []
extractedcabs = []
list_range_start_cab = []
nb_update = 0
executable = {}
supportcab = {}
# updatetempfiles_path= os.path.join(tempfile.gettempdir(), "winupdate")


updatetempfiles_path = os.path.join("/", "tmp", "winupdate")
wsusscn2_file = os.path.join(updatetempfiles_path, "wsusscn2.cab")
package_file = os.path.join(updatetempfiles_path, "package.cab")
index_xml = os.path.join(updatetempfiles_path, "index.xml")
package_xml = os.path.join(updatetempfiles_path, "package.xml")
extractcmd = "/usr/bin/7z x "
patches = []
programs = []
final_updates_list = []
solved_revisionids = []

# OS Dependant Variables
OS = ""
EXEC = ""
EXEC_FULL_PATH = ""

logger = logging.getLogger()

OS = "linux"
EXEC = "7z"
EXEC_DEP = []
PATH_SEPARATOR = ":"


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


def concatenate_list_data(list):
    result = ""
    for element in list:
        result += str(element)
    return result



def get_list_package():
    global supportcab
    return supportcab.keys()


def test_executable():
    """verify executable"""
    exec_extract = {}
    res = simplecommand("which cabextract 7z")
    if res["code"] == 0:
        for t in res["result"]:
            if "cabextract" in t:
                exec_extract["cabextract"] = t.strip()
            if "7z" in t:
                exec_extract["7z"] = t.strip()
        return exec_extract


class extract_cab:
    NAME_BASE="base_wsusscn2"
    NAME_TABLE="update_data"
    NAME_UPDATE_TABLE="data_simple_update"

    CONF_FILE="/etc/cow/cow.init"


    def __init__(
        self, updatetempfiles_path="/tmp/winupdate", path_file_extract="wsusscn2.cab"
    ):
        self.insertion_in_base=0
        self.exist_in_base=0
        self.read_config()
        self.name_file = path_file_extract
        self.file_extract = os.path.join(updatetempfiles_path, path_file_extract)
        self.directory_output = updatetempfiles_path
        self.exec_extract = {}
        self.rangestart = []
        res = simplecommand("which cabextract 7z")
        if res["code"] == 0:
            for t in res["result"]:
                if "cabextract" in t:
                    self.exec_extract["cabextract"] = t.strip()
                if "7z" in t:
                    self.exec_extract["7z"] = t.strip()
        if not os.path.exists(self.directory_output):
            os.makedirs(self.directory_output)

        self.pk1 = os.path.join(self.directory_output, "package1.xml")
        self.ind1 = os.path.join(self.directory_output, "index1.xml")
        self.pk = os.path.join(self.directory_output, "package.xml")
        self.ind = os.path.join(self.directory_output, "index.xml")

    def create_connection(self):
        try:
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
        if os.path.exists(self.CONF_FILE):
            Config = ConfigParser.ConfigParser()
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

    def create_table(self):
        print ("cretion tables")
        self.create_table_wsu()
        self.create_table_update_wsu()
        return True



    def create_table_wsu(self):
        print ("cretion table %s"%self.NAME_TABLE)
        try:
            cursor = self.db.cursor()
            cmd="""CREATE TABLE IF NOT EXISTS %s (
                `updateid` varchar(38) NOT NULL,
                `revisionid` varchar(16) NOT NULL,
                `creationdate` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
                `company` varchar(36) DEFAULT '',
                `product` varchar(1024) DEFAULT '',
                `productfamily` varchar(36) DEFAULT '',
                `updateclassification` varchar(36) DEFAULT '',
                `prerequisite` varchar(4096) DEFAULT '',
                `title` varchar(1024) DEFAULT '',
                `description` varchar(4096) DEFAULT '',
                `msrcseverity` varchar(16) DEFAULT '',
                `msrcnumber` varchar(16) DEFAULT '',
                `kb` varchar(16) DEFAULT '',
                `languages` varchar(16) DEFAULT '',
                `category` varchar(128) DEFAULT '',
                `supersededby` varchar(3072) DEFAULT '',
                `supersedes` text DEFAULT NULL,
                `payloadfiles` varchar(2048) DEFAULT '',
                `revisionnumber` varchar(30) DEFAULT '',
                `bundledby_revision` varchar(30) DEFAULT '',
                `isleaf` varchar(6) DEFAULT '',
                `issoftware` varchar(30) DEFAULT '',
                `deploymentaction` varchar(30) DEFAULT '',
                    PRIMARY KEY (`updateid`),
                    UNIQUE KEY `id_UNIQUE` (`updateid`),
                    UNIQUE KEY `id_UNIQUE1` (`revisionid`),
                    KEY `indproduct` (`product`(768)),
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
        #try:
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
        onlyfiles.remove(self.name_file)
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
            self.download_cab()
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
            url = "http://go.microsoft.com/fwlink/?linkid=74689"
            r = requests.get(url, stream=True)
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

    def traitement_updateid(self, updateid):
        c = db.cursor()
        try:
            if (
                c.execute(
                    'select updateid from MSPatchTable where updateid="'
                    + updateid
                    + '"'
                )
                .fetchall()
                .__len__()
                > 0
            ):
                return False
            else:
                return True
        except Exception:
            print(("%s" % (traceback.format_exc())))
        finally:
            c.close()

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

            Company = []
            Product = []
            ProductFamily = []
            UpdateClassification = []
            for Categories in element_update.iterfind(".//Category"):
                self.normalize_attr(Categories)
                typea = Categories.attrib["type"]
                if typea.endswith("t"):
                    Product.append(Categories.attrib["id"])
                elif typea.startswith("C"):
                    Company.append(Categories.attrib["id"])
                elif typea.startswith("U"):
                    UpdateClassification.append(Categories.attrib["id"])
                elif typea.endswith("y"):
                    ProductFamily.append(Categories.attrib["id"])

            supersededby=Category_Company=Category_Product=Category_ProductFamily=Category_UpdateClassification=prerequisites=title=description=moreinfourl=supersedes=""

            Category_Company=",".join(Company)
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
                    `company`,
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
                        MySQLdb.escape_string(Category_Company),
                        MySQLdb.escape_string(Category_Product),
                        MySQLdb.escape_string(Category_ProductFamily),
                        MySQLdb.escape_string(Category_UpdateClassification),
                        MySQLdb.escape_string(prerequisites),
                        MySQLdb.escape_string(title),
                        MySQLdb.escape_string(description),
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
                    `company`,
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
                        MySQLdb.escape_string(Category_Company),
                        MySQLdb.escape_string(Category_Product),
                        MySQLdb.escape_string(Category_ProductFamily),
                        MySQLdb.escape_string(Category_UpdateClassification),
                        MySQLdb.escape_string(prerequisites),
                        MySQLdb.escape_string(title),
                        MySQLdb.escape_string(description),
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

            cursorproc = self.db.cursor()
            cursorproc.execute("call update_updateclassification();")
            self.db.commit()


def solve_supersede_updateids(applicable_updates):
    global final_updates_list
    superseded_updates = []
    applicable_updates_query = (
        str(applicable_updates).replace("u'", "'").replace("[", "(").replace("]", ")")
    )
    record = c.execute(
        "select supersededby from MSPatchTable where updateid in "
        + applicable_updates_query
        + ";"
    )
    for i, j in zip(record.fetchall(), range(0, applicable_updates.__len__())):
        if i[0].__len__() == 0:
            final_updates_list.append(applicable_updates[j])
            record = c.execute(
                "select revisionid from MSPatchTable where updateid ='"
                + applicable_updates[j]
                + "';"
            )
            solved_revisionids.append(record.fetchall()[0][0])
        else:
            solve_supersede_revisionids(i[0])


def solve_supersede_revisionids(revisionids):
    for i in revisionids.split(","):
        if i.strip(" ") in solved_revisionids:
            continue
        record = c.execute(
            "select updateid,supersededby from MSPatchTable where revisionid='"
            + i.strip(" ")
            + "' ;"
        )
        for j in record.fetchall():
            if j[1].__len__() == 0:
                if j[0] in final_updates_list:
                    continue
                else:
                    final_updates_list.append(j[0])
                    solved_revisionids.append(i.strip(" "))
            else:
                solve_supersede_revisionids(j[1])
                solved_revisionids.append(i.strip(" "))


def scan(input_file):
    files = open(input_file, "r")
    a = str(files.readlines()).replace("\\n", "")
    print(
        str(
            a.replace("]", "")
            .replace("[", "")
            .replace("'", "")
            .replace(" ", "")
            .split(",")
            .__len__()
        )
        + " selected updates"
    )
    solve_supersede_updateids(
        a.replace("]", "").replace("[", "").replace("'", "").replace(" ", "").split(",")
    )
    print(
        str(final_updates_list.__len__())
        + " applicable updates after solving for supersedes !!"
    )


def help():

    print(
        r"""Usage:-

    cuw.exe scan <filename with updateids> - Checks for Update ids in the input file and gives the final list of applicable updates with details
    cuw.exe scan <filename with updateids> output <output file name> - Same as the previous option with the output (with extra details) being exported as csv
    cuw.exe update - Updates the local patch database (Requires Internet Connection and some patience !! :P)
    cuw.exe exportdb <filename of the exported csv>" - Exports the local patch database as csv file
    cuw.exe help  -  Displays this help"""
    )


if __name__ == "__main__":

    # Quit the process if we don't want to continue
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))




    logging.basicConfig(
        filename="logout",
        filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )

    logger.debug("start programe %s" % sys.argv[1])

    executable = test_executable()
    if len(executable) != 2:
        print(
            "7z or cabextract file not found.\n\nCUW cannot function without these dependencies.\n\nPlease install cabextract and 7z [%s]"
            % executable
        )
        sys.exit(1)

    argc = sys.argv.__len__()
    if argc == 1:
        help()
    elif argc == 2:
        if sys.argv[1] == "update":
            dd = extract_cab()
            dd.update()
        elif sys.argv[1] == "exportdb":
            dd = extract_cab()
            dd.exportdb()
        else :
            help()
    elif argc == 3:
        if sys.argv[1] == "scan":
            if os.path.isfile(sys.argv[2]):
                scan(sys.argv[2])
                records = c.execute(
                    "select title,kb from MSPatchTable where updateid in "
                    + str(final_updates_list)
                    .replace("u'", "'")
                    .replace("[", "(")
                    .replace("]", ")")
                    + ";"
                )
                for i in records:
                    print(i[0] + " : " + i[1])
            else:
                print("\n\n" + sys.argv[2] + " file does not exist !!")
                help()
        elif sys.argv[1] == "exportdb":
            exportdb(sys.argv[2])
        else:
            help()
    elif argc == 5:
        if (
            sys.argv[1] == "scan"
            and os.path.isfile(sys.argv[2])
            and sys.argv[3] == "output"
        ):
            scan(sys.argv[2])
            export(sys.argv[4])
        else:
            help()
    else:
        help()

#procedure stockee utiliser par le programme

#USE `base_wsusscn2`;
#DROP procedure IF EXISTS `update_updateclassification`;

#USE `base_wsusscn2`;
#DROP procedure IF EXISTS `base_wsusscn2`.`update_updateclassification`;
#;

#DELIMITER $$
#USE `base_wsusscn2`$$
#CREATE DEFINER=`root`@`localhost` PROCEDURE `update_updateclassification`()
#BEGIN
  #DECLARE is_done INTEGER DEFAULT 0;
  #-- déclarer la variable qui va contenir les noms des clients récupérer par le curseur .
  #DECLARE c_title varchar(2040)  DEFAULT "";
  #DECLARE c_udateid varchar(2040)  DEFAULT "";
  #-- déclarer le curseur
  #DECLARE client_cursor CURSOR FOR
   #select title, updateid FROM base_wsusscn2.update_data where updateid in
   #(SELECT distinct updateclassification FROM base_wsusscn2.update_data where updateclassification not in (''));

  #-- déclarer le gestionnaire NOT FOUND
  #DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
    #-- ouvrir le curseur
  #OPEN client_cursor;
  #-- parcourir la liste des noms des clients et concatèner tous les noms où chaque nom est séparé par un point-virgule(;)
  #get_list: LOOP
  #FETCH client_cursor INTO c_title,c_udateid;

  #IF is_done = 1 THEN
  #LEAVE get_list;
  #END IF;

  #-- traitement
  #UPDATE `base_wsusscn2`.`update_data` SET `updateclassification` = c_title WHERE (`updateclassification` = c_udateid);

  #END LOOP get_list;
  #-- fermer le curseur
  #CLOSE client_cursor;
#END$$

#DELIMITER ;
#;

#" procedure stockee renvoi les mise à jour
#USE `base_wsusscn2`;
#DROP procedure IF EXISTS `create_update_result`;

#USE `base_wsusscn2`;
#DROP procedure IF EXISTS `base_wsusscn2`.`create_update_result`;
#;

#DELIMITER $$
#USE `base_wsusscn2`$$
#CREATE DEFINER=`root`@`localhost` PROCEDURE `create_update_result`( in FILTERtable varchar(2048), in KB_LIST varchar(2048), in createtbleresult int)
#BEGIN
#DECLARE _next TEXT DEFAULT NULL;
#DECLARE _nextlen INT DEFAULT NULL;
#DECLARE _value TEXT DEFAULT NULL;
#DECLARE _list MEDIUMTEXT;

#DECLARE kb_next TEXT DEFAULT NULL;
#DECLARE kb_nextlen INT DEFAULT NULL;
#DECLARE kb_value TEXT DEFAULT NULL;
#DECLARE kb_updateid  varchar(50) DEFAULT NULL;
#-- clean table
#drop table if EXISTS tmp_kb_updateid;
#drop table IF EXISTS tmp_t1;
#drop table IF EXISTS tmp_my_mise_a_jour;
#drop table IF EXISTS tmp_result_procedure;
#CREATE TABLE IF NOT EXISTS `tmp_kb_updateid` (
  #`c1` varchar(64) NOT NULL,
  #PRIMARY KEY (`c1`),
  #UNIQUE KEY `c1_UNIQUE` (`c1`)
#) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;
#truncate tmp_kb_updateid;

#iteratorkb:
#LOOP
  #-- exit the loop if the list seems empty or was null;
  #-- this extra caution is necessary to avoid an endless loop in the proc.
  #IF CHAR_LENGTH(TRIM(kb_list)) = 0 OR kb_list IS NULL THEN
    #LEAVE iteratorkb;
  #END IF;

  #-- capture the next value from the list
  #SET kb_next = SUBSTRING_INDEX(kb_list,',',1);

  #-- save the length of the captured value; we will need to remove this
  #-- many characters + 1 from the beginning of the string
  #-- before the next iteration
  #SET kb_nextlen = CHAR_LENGTH(kb_next);

  #-- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  #SET kb_value = TRIM(kb_next);

  #-- insert the extracted value into the target table
  #-- select updateid into kb_updateid from base_wsusscn2.update_data where kb = kb_value;
  #-- select kb_updateid;
  #INSERT IGNORE INTO tmp_kb_updateid (c1) VALUES (kb_value );

  #-- rewrite the original string using the `INSERT()` string function,
  #-- args are original string, start position, how many characters to remove,
  #-- and what to "insert" in their place (in this case, we "insert"
  #-- an empty string, which removes kb_nextlen + 1 characters)
  #SET kb_list = INSERT(kb_list,1,kb_nextlen + 1,'');
#END LOOP;




#-- ------ generation table kb tmp_kb_updateid -----------
#-- call list_kb_machine(KBLIST);
#-- les updatesid des mise a jour deja installer seront inclus dans la table des update excluts tmp_t1

#-- creation table filter
#CREATE TABLE IF NOT EXISTS tmp_my_mise_a_jour AS (SELECT * FROM
    #base_wsusscn2.update_data
#WHERE
    #title LIKE FILTERtable and title not like "%Dynamic Cumulative Update%");

#SELECT
    #GROUP_CONCAT(DISTINCT supersedes
        #ORDER BY supersedes ASC
        #SEPARATOR ',')
#INTO _list FROM
    #base_wsusscn2.tmp_my_mise_a_jour;

#CREATE TABLE IF NOT EXISTS `tmp_t1` (
    #`c1` VARCHAR(64) NOT NULL,
    #PRIMARY KEY (`c1`),
    #UNIQUE KEY `c1_UNIQUE` (`c1`)
#)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
#truncate tmp_t1;
#iterator:
#LOOP
  #-- exit the loop if the list seems empty or was null;
  #-- this extra caution is necessary to avoid an endless loop in the proc.
  #IF CHAR_LENGTH(TRIM(_list)) = 0 OR _list IS NULL THEN
    #LEAVE iterator;
  #END IF;

  #-- capture the next value from the list
  #SET _next = SUBSTRING_INDEX(_list,',',1);

  #-- save the length of the captured value; we will need to remove this
  #-- many characters + 1 from the beginning of the string
  #-- before the next iteration
  #SET _nextlen = CHAR_LENGTH(_next);

  #-- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  #SET _value = TRIM(_next);

  #-- insert the extracted value into the target table

  #INSERT IGNORE INTO tmp_t1 (c1) VALUES (_value);

  #-- rewrite the original string using the `INSERT()` string function,
  #-- args are original string, start position, how many characters to remove,
  #-- and what to "insert" in their place (in this case, we "insert"
  #-- an empty string, which removes _nextlen + 1 characters)
  #SET _list = INSERT(_list,1,_nextlen + 1,'');
#END LOOP;
#DELETE FROM `base_wsusscn2`.`tmp_t1`
#WHERE
    #(`c1` = '');

#-- injection les update_id deja installer dans tmp_t1
 #INSERT IGNORE INTO tmp_t1  select updateid from base_wsusscn2.update_data where kb in (select c1 from tmp_kb_updateid);

#CREATE TABLE tmp_result_procedure AS (SELECT * FROM
    #tmp_my_mise_a_jour
#WHERE
    #updateid NOT IN (SELECT
            #c1
        #FROM
            #tmp_t1));

#-- on supprime les updateid qui sont dans select c1 from tmp_kb_updateid
#DELETE FROM tmp_result_procedure WHERE updateid IN (select c1 from tmp_kb_updateid);
#drop table IF EXISTS tmp_t1;
#drop table IF EXISTS tmp_my_mise_a_jour;
#drop table IF EXISTS tmp_kb_updateid;
#SELECT
    #*
#FROM
    #tmp_result_procedure;
	#if    createtbleresult = 0 then
		#drop table IF EXISTS tmp_result_procedure;
	#END IF;
#END$$

#DELIMITER ;
#;

#USE `base_wsusscn2`;
#DROP procedure IF EXISTS `base_wsusscn2`.`update_datetime`;
#;

#DELIMITER $$
#USE `base_wsusscn2`$$
#CREATE DEFINER=`root`@`localhost` PROCEDURE `update_datetime`()
#BEGIN
  #UPDATE `base_wsusscn2`.`update_data`
#SET
    #`datetitle` = STR_TO_DATE(concat(SUBSTRING(title, 1, 7),'-01'),'%Y-%m-%d %h:%i%s')
#WHERE
    #(`updateid` IN (SELECT
            #updateid
        #FROM
            #update_data
        #WHERE
            #title REGEXP ('^[0-9]{4}-[0-9]{2} *')));

#END$$

#DELIMITER ;
#;

