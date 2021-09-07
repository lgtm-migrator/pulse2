# coding: utf-8;
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

# file : mmc/extractor/__init__.py
# coding:utf-8

"""
csv extractor
"""
import os
import sys
import logging
from datetime import datetime
from optparse import OptionParser
import csv
import pprint

from mmc.extractor.db.xmpp import XmppMasterDatabase
#from mmc.extractor.db.pkgs import PkgsDatabase



logging.basicConfig(level=logging.DEBUG)
parser = OptionParser()
logger = logging.getLogger()

# When calling this program:
# -f option specify the dest csv file
parser.add_option("-f", "--file", dest="filename",
                  help="write csv to FILE", metavar="FILE")

# -w option specify which week the stats are calculated
# -w 1 (default) = stats between 1 week ago and now
# -w 2 = stats between 2 weeks ago and 1 week ago
# -w 3 = stats between 3 weeks ago and 2 weeks ago

# All the dates are calculated from the current datetime (now).
parser.add_option("-w", "--week", dest="week",
                  help="Get status for n weeks ago", metavar="WEEK")

(options, args) = parser.parse_args(sys.argv)

# Define config files for the database connectors
pkgsconfigfile = os.path.join("/", "etc", "mmc", "plugins", "pkgs.ini")
xmppconfigfile = os.path.join("/", "etc", "mmc", "plugins", "xmppmaster.ini")

# Needed to use the database connector
XmppMasterDatabase().activate(xmppconfigfile)
# If the pkgs database connector is needed
#PkgsDatabase().activate(pkgsconfigfile)

# Set by default the selected week.
week = 1
if options.week != "":
    week = int(options.week)

# Processing the stats
datas = XmppMasterDatabase().get_deploy(week)

# Check the filename
if options.filename != "" and options.filename is not None:
    if os.path.isdir(os.path.dirname(os.path.abspath(options.filename))):
        with open(options.filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)

            count = 0
            for row in datas:
                if count == 0:
                    header = row.keys()
                    csv_writer.writerow(header)
                    count += 1

                # Writing data of CSV file
                csv_writer.writerow(row.values())
            csv_file.close()
        logging.info("The file %s is generated", os.path.abspath(options.filename))
    else:
        logging.error("The folder %s doesn't exist", \
                      os.path.dirname(os.path.abspath(options.filename)))
else:
    # In a case where the filename is not specified,
    # The datas are printed
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(datas)
