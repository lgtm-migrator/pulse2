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

# file  : transfert_partage_cnam.py

import shutil
import sys,os
import logging
import platform
import subprocess
import base64
import time
import json
import re
import traceback
from datetime import datetime
from optparse import OptionParser
import MySQLdb
import getpass
logger = logging.getLogger()

def simplecommand(cmd):
    obj = {}
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code'] = p.wait()
    obj['result'] = result
    return obj
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if __name__ == '__main__':
    base="pkgs"

    textprogrammehelp="Ce Programme permet de deplacer les packages existant en les classant dans leurs repertoire de partages. le classement est suivant le ucam  contenue dans le nom ou root."

    optp = OptionParser(description=textprogrammehelp)


    optp.add_option("-e", "--nosimul",action="store_true",
                    dest="execcmd", default = False,
                    help="execute les actions.")

    optp.add_option("-i", "--indeterminertoglobal",action="store_true",
                    dest="indeterminertoglobal", default = False,
                    help="les packages sans numero de ucam ou sans root sont considere comme national")

    opts, args = optp.parse_args()


    packagedir=os.path.join("/", "var", "lib", "pulse2", "packages")
    sharing=os.path.join(packagedir,"sharing")
    list_package_non_lien_symbolique =   [os.path.join(packagedir, x) for x in os.listdir(packagedir) \
        if len(x) == 36 and\
            os.path.isdir(os.path.join(packagedir, x)) and\
                not  os.path.islink(os.path.join(packagedir, x))]


    if not os.path.exists(sharing):
        os.mkdir(sharing)
    if not os.path.exists(os.path.join(sharing, "global")):
        os.mkdir(os.path.exists(os.path.join(sharing, "global")))

    partage_list=set()
    partage_indeterminer=[]
    #selection package from ucam
    if opts.execcmd:
        print "Commande transfert"
    else:
        print "Commande transfert simulée"
    for package in list_package_non_lien_symbolique:
        if package[34:38] == "root":
            #global package.
            partage_list.add("global")
            print"\033[95mtransfert %s -> %s\033[0m" % (package, os.path.join(sharing, "global"))
            cmd="mv %s %s/" % (package, os.path.join(sharing, "global"))
            if opts.execcmd:
                simplecommand(cmd)


        elif package[33] == "-" and package[40] == "-" and package[34:40].isdigit():
            ucam =package[34:40]
            partage_list.add(ucam)
            partagefolder = os.path.join("/var/lib/pulse2/packages/sharing", ucam )
            if not os.path.exists(partagefolder): os.mkdir(partagefolder)
            print "\033[94mtransfert %s -> %s\033[0m" %(package, os.path.join(sharing, ucam))
            cmd="mv %s %s/"%(package, os.path.join(sharing, ucam))
            if opts.execcmd:
                simplecommand(cmd)
        else:
            if opts.indeterminertoglobal:
                print"\033[95mtransfert package sans ucam in national partage\n\t%s -> %s\033[0m" % (package, os.path.join(sharing, "global"))
                partage_list.add("global")
                cmd="mv %s %s/"%(package, os.path.join(sharing, "global"))
                if opts.execcmd:
                    simplecommand(cmd)
            else:
                print "Ne peut pas classe ce package dans 1 partage %s" % (package)
                partage_indeterminer.append(package)
    print
    print "\nlists des partages dans lequel il existent au moins 1 package de transfere."
    for li in partage_list:
        print li

    if len(partage_indeterminer):
        print "\n\nlist des \033[1mpackages non classe\033[0ms dans 1 partage \033[96m\033[4mOPTION -i pour forcer le classemment dans national partage\033[0m"
        for li in partage_indeterminer:
            print li

    if not opts.execcmd:
        print "\nMode Simulation \033[93mAucune ACTION REALISER\033[0m \033[96m\033[4mOPTION -e pour execute les actions.\033[0m"






