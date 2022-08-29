#!/usr/bin/python
# -*- coding: utf-8 -*-
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
#

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
import re
import codecs
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
    LANG = "fr"
    
    CONF_FILE="/etc/cow/cow.init"
    

    def __init__(
        self, updatetempfiles_path="/tmp/winupdate", path_file_extract="wsusscn2.cab"
    ):
        
        self.insertion_in_base=0
        self.exist_in_base=0
        self.read_config()
        self.NAME_UPDATE_TABLE="%s_%s"%(self.NAME_UPDATE_TABLE, self.LANG )
        self.NAME_TABLE= "%s_%s"%( self.NAME_TABLE, self.LANG)
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
                db=self.NAME_BASE,                
                               charset = 'utf8'
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

            if Config.has_option('main', 'language'):
                self.param_language = Config.get('main', 'language')
    
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
                `revisionid` varchar(38) NOT NULL,
                `creationdate` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
                `company` varchar(120) DEFAULT NULL,
                `product` varchar(1024) DEFAULT NULL,
                `productfamily` varchar(120) DEFAULT NULL,
                `updateclassification` text DEFAULT NULL,
                `prerequisite`text DEFAULT NULL,
                `title` text DEFAULT NULL,
                `description` text DEFAULT NULL,
                `msrcseverity` text DEFAULT NULL,
                `msrcnumber` text DEFAULT NULL,
                `kb` text DEFAULT NULL,
                `languages` text DEFAULT NULL,
                `category` text DEFAULT NULL,
                `supersededby` text DEFAULT NULL,
                `supersedes` text DEFAULT NULL,
                PRIMARY KEY (`updateid`),
                UNIQUE KEY `id_UNIQUE` (`updateid`),
                UNIQUE KEY `id_UNIQUE1` (`revisionid`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ;"""%(self.NAME_TABLE)
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
            u'"Update ID","Creation Date","Update Classification","Title","Description","KB ID","MSRC Severity","MSRC Number"\n'
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
            #print(dda)
            if cursor1.execute(dda):
                updateclassification = cursor1.fetchone()[0]
                #print updateclassification
                cursor1.close()
                datetimeupdate = i[1].strftime("%m/%d/%Y, %H:%M:%S")
                de='''"%s","%s","%s","%s","%s","%s","%s","%s"\n'''%(i[0],
                                                                    datetimeupdate,
                                                                    updateclassification,
                                                                    i[3],
                                                                    i[4],
                                                                    i[5],
                                                                    i[6],
                                                                    i[7])
                fileout.write(
                    de.encode('utf-8')
                )
                
                self.write_table_update_wsu( 
                                        i[0], 
                                        datetimeupdate,
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
                        `title`,
                        `description`,
                        `kb`,
                        `msrcseverity`,
                        `msrcnumber`)
                        VALUES ( '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s');""" %(self.NAME_BASE,
                                self.NAME_UPDATE_TABLE,
                                updateid, 
                                creationdate,
                                MySQLdb.escape_string(updateclassification),
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
        rep=os.path.join(self.directory_output, "package%s" % choix)
        c=os.path.join(rep, "c", str(nbrange)) 
        l=os.path.join(rep, "l", self.LANG, str(nbrange))
        en=os.path.join(rep, "l", "en", str(nbrange))
        s=os.path.join(rep, "s",  str(nbrange))
        x=os.path.join(rep, "x",  str(nbrange))
        out=os.path.join(rep, "%s.xml" % str(nbrange))
        
        filenames=[]
        
        if  os.path.exists(c):
            filenames.append(c)
        filedescription=""
        if  os.path.exists(l):
            #filenames.append(l)
            filedescription=l
        if  os.path.exists(s):
            filenames.append(s)
        if  os.path.exists(x):
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

        #print (filenames)
        #if len(stringconcat_ascii) >  6000:
        #print( "creation file %s" % out)
        #if  filedescription:
            #print( "fichier de localisation %s [%s] existe " % (l, self.LANG))
            #if  os.path.exists(en):
                #print( "mais %s existe" % (en))
        with open(out, "w") as new_file:
            new_file.write(stringconcat_ascii)
        #cmd = 'xmllint --format "%s" 2>&1 > /tmp/winupdate/convert' % (out )
        #print (cmd)
        #print ('mv  /tmp/winupdate/convert "%s"' % ( out))
        #os.system(cmd)
        #os.system('mv  /tmp/winupdate/convert "%s"' % ( out))
        return stringconcat_ascii , filedescription

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
        for element_update in root.iterfind(".//Update"):
            att = element_update.attrib
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
        
            supersededby=Category_Company=Category_Product=Category_ProductFamily=Category_UpdateClassification=prerequisites=supersedes=""
        
            Category_Company=",".join(Company)
            Category_Product=",".join(Product)
            Category_ProductFamily=",".join(ProductFamily)
            Category_UpdateClassification=",".join(UpdateClassification)
            prerequisites=",".join(Prerequisitel)
            supersededby=",".join(Supersededbyl)

            #print("supersededby %s" % supersededby)
            try:
                # print("supersededby %s" % supersededby)
                revisiondata = element_update.attrib["RevisionId"]
                #print (revisiondata)
                filexmlreisonid , filedescription= self.file_contient(
                    int(revisiondata)
                )
                root = etree.fromstring(filexmlreisonid)
            except Exception as e:
                print (str(e))
                print ("error creation file RevisionId %s" %RevisionId)
                print("\n%s" % (traceback.format_exc()))
                continue
            title=description=moreinfourl=languages=""
            uninstallnotes=supporturl=""
            
            
                
            if filedescription:
                Localized = etree.parse(filedescription)
                #print (Localized)
                #print (filedescription)
                try:
                    Title = Localized.find("Title")
                    title = Title.text
                except:
                    # pas de title
                    title="title missing"
                    pass
                
                try:
                    UninstallNotes = Localized.find("UninstallNotes")
                    uninstallnotes = UninstallNotes.text
                except:
                    # pas de title
                    uninstallnotes="uninstallnotes missing"
                    pass
                
                try:
                    SupportUrl = Localized.find("SupportUrl")
                    supporturl = SupportUrl.text
                except:
                    # pas de title
                    supporturl="supporturl missing"
                    

                try:
                    Description = Localized.find("Description")
                    description=Description.text
                except:
                    description="no_descip"
                    

                try:
                    Moreinfourl = Localized.find("MoreInfoUrl")
                    moreinfourl=Moreinfourl.text
                except:
                    moreinfourl="moreinfourl missing"
                    
                
                try:
                    Language = Localized.find("Language")
                    languages=Language.text
                except:
                    languages="languages missing"
                    pass
                
            Supersedes=[]
            for Upid in root.iterfind(".//SupersededUpdates/UpdateIdentity"):
                self.normalize_attr(Upid)
                if "updateid" in Upid.attrib:
                    Supersedes.append(Upid.attrib["updateid"])
            supersedes=",".join(Supersedes)

            defaultpropertieslanguage=msrcseverity=isbeta=kbarticleid=securitybulletinid = ""
            ExtendedProperties = root.find("ExtendedProperties")
            self.normalize_attr(ExtendedProperties)
            if "defaultpropertieslanguage" in ExtendedProperties.attrib:
                defaultpropertieslanguage = ExtendedProperties.attrib['defaultpropertieslanguage']
            
            #if  not languages:
                #languages=defaultpropertieslanguage
            
            
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
                Categoryinformation = root.find("HandlerSpecificData/CategoryInformation")
                self.normalize_attr(Categoryinformation)
                if "categorytype" in Categoryinformation.attrib:
                    categorytype = Categoryinformation.attrib['categorytype']
            except:
                pass

            
            ###################"
            #print("######################injection in base######################")
            #print ("UpdateId %s" % UpdateId)
            #print ("RevisionId %s"% RevisionId)
            #print ("description %s" % description)
            #print ("title %s" % title)  
            #print ("Moreinfourl %s" % moreinfourl)
            #print ("supersededby %s" % supersededby)
            #print ("Category_Company %s" % moreinfourl)
            #print ("Category_Product %s" % moreinfourl)
            #print ("Category_ProductFamily %s" % Category_ProductFamily)
            #print ("Category_UpdateClassification %s" % Category_UpdateClassification)
            #print ("prerequisites %s" % prerequisites)
            #print ("supersedes %s" % supersedes)
            #print ("securitybulletinid %s" % securitybulletinid)
            #print ("categorytype %s" % categorytype)
            #print ("kbarticleid %s" % kbarticleid)
            #print ("isbeta %s" % isbeta)
            #print ("msrcseverity %s" % msrcseverity)
            #print ("defaultpropertieslanguage %s" % defaultpropertieslanguage)
            #print("######################end in base######################")
            # Languages => defaultpropertieslanguage ou Language
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
                `supersedes`) VALUES ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');""" %(self.NAME_BASE,
                    self.NAME_TABLE,
                    UpdateId,
                    RevisionId,
                    MySQLdb.escape_string(Category_Company),
                    MySQLdb.escape_string(Category_Product),
                    MySQLdb.escape_string(Category_ProductFamily),
                    MySQLdb.escape_string(Category_UpdateClassification),
                    MySQLdb.escape_string(prerequisites),
                    re.escape(title),
                    re.escape(description),
                    msrcseverity,
                    securitybulletinid,
                    kbarticleid,
                    languages,
                    categorytype,
                    supersededby,
                    supersedes
                    )
                #print (cmd)
                cursor.execute(cmd)
                self.db.commit()
                
                self.insertion_in_base+=1
            except Exception as e:
                print("\n%s" % (traceback.format_exc()))
                
        
        #self.db.close()





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


def export(output_file):
    fileout = open(output_file, "w")
    finalupdates_query = (
        str(final_updates_list).replace("u'", "'").replace("[", "(").replace("]", ")")
    )
    fileout.write(
        '"Update ID","Creation Date","Update Classification","Title","Description","KB ID","MSRC Severity","MSRC Number"\n'
    )
    record = c.execute(
        "select updateid,creationdate,updateclassification,title,description,kb,msrcseverity,msrcnumber from MSPatchTable where updateid in "
        + finalupdates_query
        + " order by creationdate desc;"
    )
    for i in tqdm(record.fetchall(), total=final_updates_list.__len__()):
        updateclassification = c.execute(
            "select title from MSPatchTable where updateid='" + i[2] + "';"
        ).fetchone()[0]
        fileout.write(
            '"'
            + i[0]
            + '","'
            + i[1]
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
    fileout.close()
    print("\n\n Report exported Successfully !!")


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
