#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2021 siveo, http://www.siveo.net
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


import json, os, sys
from datetime import datetime
import traceback

datenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

def readjsonfile(namefile):

    with open(namefile) as json_data:
        data_dict = json.load(json_data)
    return data_dict

def writejsonfile(namefile, data):
    with open(namefile, 'w') as json_data:
        json.dump(data, json_data, indent=4)

def listpartage():
    exclude_name_package = ["sharing", ".stfolder", ".stignore"]
    folderpackages = os.path.join("/", "var" ,"lib","pulse2","packages","sharing")
    return  [ os.path.join(folderpackages,x) for x in os.listdir(folderpackages) \
                if os.path.isdir(os.path.join(folderpackages,x)) \
                    and x not in exclude_name_package]

def listpackage():
    listpackagestotal=[]
    listepartage = listpartage()
    exclude_name_package = ["sharing", ".stfolder", ".stignore" ]
    folderpackages = os.path.join("/", "var" ,"lib","pulse2","packages","sharing")
    
    for partage in listepartage:
        listpackagestotal.extend(
            [ os.path.join(partage,x) for x in os.listdir(partage) \
                if os.path.isdir(os.path.join(partage,x)) \
                    and x not in exclude_name_package])
    return listpackagestotal

def main():
    for path_packagename in listpackage():
        namefilejson = os.path.join(path_packagename,"conf.json")
        print
        print "------- START traitement file %s _______" % namefilejson
        try:
            jsondata = readjsonfile(namefilejson)
            modif=False
            partagename = os.path.basename(os.path.dirname(path_packagename))
            if "localisation_server" not in jsondata:
                jsondata['localisation_server'] = partagename
                print "localisation_server missing"
                modif=True
            else:
                if jsondata['localisation_server'].strip() == "":
                    jsondata['localisation_server'] = partagename
                    print "localisation_server exist but not share value"
                    modif=True
                elif jsondata['localisation_server'].strip() != partagename:
                    print "localisation_server exist but error value is %s" %jsondata['localisation_server']
                    jsondata['localisation_server'] = partagename
                    modif=True
            if "previous_localisation_server" not in jsondata:
                jsondata['previous_localisation_server'] = partagename
                print "previous_localisation_server missing"
                modif=True
            if "creation_date" not in jsondata:
                jsondata['creation_date'] = datenow
                print "creation date missing missing"
                modif=True
            if "creator" not in jsondata:
                jsondata['creator'] = "oldtonewpackagescript"
                print "creator name missing"
                modif=True
            if "metagenerator" not in jsondata:
                print "metagenerator missing"
                jsondata['metagenerator'] = "expert"
            if modif:
                print "save file %s"% namefilejson
                writejsonfile(namefilejson, jsondata)
                print "new file \n%s" % json.dumps(jsondata,indent=4)
            else:
                print "Correct values pour ce packages"
            print "------- END trairement file_______"
        except:
            print "VERIFY JSON FILE %s"%namefilejson  
            print "%s" % traceback.format_exc()
            print "------- END trairement file _______"
    return 0    
if __name__ == '__main__':
    sys.exit(main())
