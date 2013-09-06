#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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

"""
Glpi querymanager
give informations to the dyngroup plugin to be able to build dyngroups
on glpi informations
"""

import logging
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.config import GlpiQueryManagerConfig

from pulse2.utils import unique

def activate():
    conf = GlpiQueryManagerConfig("glpi")
    return conf.activate

def queryPossibilities():
    ret = {}
    ret['Computer name'] = ['list', getAllHostnames]
    ret['Contact'] = ['list', getAllContacts]
    ret['Contact number'] = ['list', getAllContactNums]
    ret['Description'] = ['list', getAllComments]
    ret['Model'] = ['list', getAllModels]
    ret['Manufacturer'] = ['list', getAllManufacturers]
    ret['State'] = ['list', getAllStates]
    ret['Location'] = ['list', getAllLocations]
    ret['Opeating system'] = ['list', getAllOs]
    ret['Service Pack'] = ['list', getAllOsSps]
    ret['Group'] = ['list', getAllGroups]
    #ret['Network'] = ['list', getAllNetworks]  # Disabled (TODO: discuss)
    ret['Software name'] = ['list', getAllSoftwares, 3]
    ret['Software name & version'] = ['double', getAllSoftwaresAndVersions, 3, 2]
    ret['Entity'] = ['list', getAllEntities]

    logging.getLogger().info('queryPossibilities %s'%(str(ret)))
    return ret

def queryGroups():
    # Assign criterions to categories
    ret = {}
    # Identification cat
    ret['Identification'] = [ \
                                ['Computer name','Get all computers by hostname pattern'], \
                                ['Description','Get all computers by description pattern'], \
                                ['Group',''] \
                            ]
    # Hardware cat
    ret['Hardware'] =       [ \
                                ['Model'], \
                                ['Manufacturer'], \
                                ['State',''] \
                            ]
    # Contact
    ret['Contact'] =        [ \
                                ['Contact',''], \
                                ['Contact number',''] \
                            ]
    #Zone
    ret['Zone'] =           [ \
                                ['Location',''], \
                                ['Entity',''] \
                            ]
    # Software
    ret['Software'] =       [ \
                                ['OS',''], \
                                ['Service Pack',''], \
                                ['Software name',''], \
                                ['Software name & version',''] \
                            ]
    #
    return ret

def extendedPossibilities():
    """
    GLPI plugin has no extended possibilities
    """
    return {}

def query(ctx, criterion, value):
    logging.getLogger().info(ctx)
    logging.getLogger().info(criterion)
    logging.getLogger().info(value)
    machines = []
    if criterion == 'OS' or criterion == 'Operating system':
        machines = [x.name for x in Glpi().getMachineByOs(ctx, value)]
    elif criterion == 'ENTITY' or criterion == 'Entity':
        machines = [x.name for x in Glpi().getMachineByEntity(ctx, value)]
    elif criterion == 'SOFTWARE' or criterion == 'Software name':
        machines = [x.name for x in Glpi().getMachineBySoftware(ctx, value)]
    elif criterion == 'Software name & version':
        machines = [x.name for x in Glpi().getMachineBySoftwareAndVersion(ctx, value)]
    elif criterion == 'Computer name':
        machines = [x.name for x in Glpi().getMachineByHostname(ctx, value)]
    elif criterion == 'Contact':
        machines = [x.name for x in Glpi().getMachineByContact(ctx, value)]
    elif criterion == 'Contact number':
        machines = [x.name for x in Glpi().getMachineByContactNum(ctx, value)]
    elif criterion == 'Description':
        machines = [x.name for x in Glpi().getMachineByComment(ctx, value)]
    elif criterion == 'Model':
        machines = [x.name for x in Glpi().getMachineByModel(ctx, value)]
    elif criterion == 'Manufacturer':
        machines = [x.name for x in Glpi().getMachineByManufacturer(ctx, value)]
    elif criterion == 'State':
        machines = [x.name for x in Glpi().getMachineByState(ctx, value)]
    elif criterion == 'Location':
        machines = [x.name for x in Glpi().getMachineByLocation(ctx, value)]
    elif criterion == 'Service Pack':
        machines = [x.name for x in Glpi().getMachineByOsSp(ctx, value)]
    elif criterion == 'Group':
        machines = [x.name for x in Glpi().getMachineByGroup(ctx, value)]
    elif criterion == 'Network':
        machines = [x.name for x in Glpi().getMachineByNetwork(ctx, value)]
    #elif criterion == '':
    #    machines = map(lambda x: x.name, Glpi().getMachineBy(ctx, value))
    return [machines, True]

def getAllOs(ctx, value = ''):
    return unique([x.name for x in Glpi().getAllOs(ctx, value)])

def getAllEntities(ctx, value = ''):
    return [x.name for x in Glpi().getAllEntities(ctx, value)]

def getAllSoftwares(ctx, value = ''):
    ret = unique([x.name for x in Glpi().getAllSoftwares(ctx, value)])
    ret.sort()
    return ret

def getAllSoftwaresAndVersions(ctx, softname = "", version = None):
    ret = []
    if version == None:
        ret = unique([x.name for x in Glpi().getAllSoftwares(ctx, softname)])
    else:
        if Glpi().glpi_chosen_version().find('0.8') == 0: # glpi in 0.8
            ret = unique([x.name for x in Glpi().getAllVersion4Software(ctx, softname, version)])
        else:
            if Glpi().glpi_version_new():
                ret = unique([x.name for x in Glpi().getAllVersion4Software(ctx, softname, version)])
            else:
                ret = unique([x.version for x in Glpi().getAllVersion4Software(ctx, softname, version)])
    ret.sort()
    return ret

def getAllHostnames(ctx, value = ''):
    return unique([x.name for x in Glpi().getAllHostnames(ctx, value)])

def getAllContacts(ctx, value = ''):
    return unique([x.contact for x in Glpi().getAllContacts(ctx, value)])

def getAllContactNums(ctx, value = ''):
    return unique([x.contact_num for x in Glpi().getAllContactNums(ctx, value)])

def getAllComments(ctx, value = ''):
    if Glpi().glpi_chosen_version().find('0.8') == 0:
        return unique([x.comment for x in Glpi().getAllComments(ctx, value)])
    else:
        return unique([x.comments for x in Glpi().getAllComments(ctx, value)])

def getAllModels(ctx, value = ''):
    return unique([x.name for x in Glpi().getAllModels(ctx, value)])

def getAllManufacturers(ctx, value = ''):
    return unique([x.name for x in Glpi().getAllManufacturers(ctx, value)])

def getAllStates(ctx, value = ''):
    return unique([x.name for x in Glpi().getAllStates(ctx, value)])

def getAllLocations(ctx, value = ''):
    return unique([x.completename for x in Glpi().getAllLocations(ctx, value)])

def getAllOsSps(ctx, value = ''):
    return unique([x.name for x in Glpi().getAllOsSps(ctx, value)])

def getAllGroups(ctx, value = ''):
    return unique([x.name for x in Glpi().getAllGroups(ctx, value)])

def getAllNetworks(ctx, value = ''):
    return unique([x.name for x in Glpi().getAllNetworks(ctx, value)])
