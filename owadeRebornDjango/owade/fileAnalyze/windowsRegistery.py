
#############################################################################
##                                                                         ##
## This file is part of Owade : www.owade.org                              ##
## Offline Windows Analyzer and Data Extractor                             ##
##                                                                         ##
##  Authors:                                                               ##
##  Elie Bursztein <owade@elie.im>                                         ##
##  Ivan Fontarensky <ivan.fontarensky@cassidian.com>                      ##
##  Matthieu Martin <matthieu.mar+owade@gmail.com>                         ##
##  Jean-Michel Picod <jean-michel.picod@cassidian.com>                    ##
##                                                                         ##
## This program is distributed under GPLv3 licence (see LICENCE.txt)       ##
##                                                                         ##
#############################################################################
__author__="ashe"
__date__ ="$Jul 6, 2011 5:55:21 PM$"

import hivex
import datetime
import sys
from owade.models import *
from owade.process import Process

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def hexdump(src, length=8, startindex=0):
    """
    Returns a hexadecimal dump of a binary string.
    length: number of bytes per row.
    startindex: index of 1st byte.
    """
    result=[]
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       printable = s.translate(FILTER)
       result.append("%04X   %-*s   %s\n" % (i+startindex, length*3, hexa, printable))
    return ''.join(result)

def openHive(path):
    hive = hivex.Hivex(path)
    root = hive.root()
    return hive, root

def getNode(hive, node, nodes):
    if node == None:
        return None
    for i in range(len(nodes)):
        try:
            node = hive.node_get_child (node, nodes[i])
        except Exception as exp:
            #print "Exception getNode: %s, %s, %s" % (exp.message, str(node), nodes[i])
            return None
    return node

def getValue(hive, node, nodes, key):
    if node == None:
        return None
    node = getNode(hive, node, nodes)
    if node == None:
        return None
    try:
        value = hive.node_get_value (node, key)
    except Exception as exp:
        #print "Exception getValue: %s" % exp.message
        return None
    return value

def searchNode(hive, node, name, depth=1):
    if node == None:
        return None
    depth = depth - 1
    for child in hive.node_children(node):
        if depth == 0:
            if hive.node_name(child) == name:
                return child
        else:
            node = searchNode(hive, child, name, depth)
            if node != None:
                return node
    return None

def searchValue(hive, node, name, depth=1):
    if node == None:
        return []
    nodes = []
    depth = depth - 1
    for child in hive.node_children(node):
        if depth == 0:
            for value in hive.node_values(child):
                if hive.value_key(value) == name:
                    nodes.append(value)
        else:
            nodes.extend(searchValue(hive, child, name, depth))
    return nodes

class GetHardwareDetail:
    def main(self, system):
        info = {}
        hive, root = openHive(system)
        current = getValue(hive, root, ["Select"], "Current")
        if current == None:
            return {name:info}
        current = hive.value_dword(current)

        enum = getNode(hive, root, ["ControlSet0%02u"%current,"Enum"])
        if enum == None:
            return {self.__class__.__name__:info}

        names = ["ACPI", "IDE", "FDC", "SCSI", "DISPLAY", "PCIDE", "SW", "USBSTOR", "PCI"]
        keys = ["FriendlyName", "FriendlyName", "HardwareID", "FriendlyName", "DeviceDesc", "HardwareID",
            "DeviceDesc", "FriendlyName","DeviceDesc"]

        for i in range(len(names)):
            node = getNode(hive, enum, [names[i]])
            values = searchValue(hive, node, keys[i], 2)
            info[names[i]] = {}
            if len(values) == 1:
                try:
                    info[names[i]][keys[i]] = hive.value_string(values[0])
                except:
                    print >>sys.stderr, "Error while accessing '%s' in '%s/%s'" % (value, names[i], keys[i])
            else:
                j = 0
                for value in values:
                    try:
                        info[names[i]]['%s%i' % (keys[i], j)] = hive.value_string(value)
                    except:
                        print >>sys.stderr, "Error while accessing '%s' in '%s/%s'" % (value, names[i], keys[i])
                    j += 1

        return {self.__class__.__name__:info}

class GetOSDetail:
    def main(self, software):
        info = {}

        hive, root = openHive(software)
        node = getNode(hive, root, ["Microsoft", "Windows NT", "CurrentVersion"])

        keys = ["ProductName", "CSDVersion", "CurrentVersion", "CurrentBuildNumber", "InstallDate",
            "RegisteredOrganization", "RegisteredOwner", "LicenseInfo"]

        for key in keys:
            value = getValue(hive, node, [], key)
            if value != None:
                if key == "InstallDate":
                    value = hive.value_dword(value)
                    value = datetime.datetime.utcfromtimestamp(value).ctime()
                elif key == "LicenseInfo":
                    value = hive.value_value(value)
                    value = hexdump(value[1],16,0)
                else:
                    value = hive.value_string(value)
            info[key] = value

        return {self.__class__.__name__:info}

class GetUserConfigurationDetail:
    def main(self, system, software, security):
        timezoneInfo = {}
        explorerInfo = {}

        system = hivex.Hivex(system)
        software = hivex.Hivex(software)
        security = hivex.Hivex(security)
        current = getValue(system, system.root(), ["Select"], "Current")
        if current == None:
            return {self.__class__.__name__:{'Timezone':timezoneInfo, 'Explorer':explorerInfo}}
        current = system.value_dword(current)

        #TimeZone
        timezone = getNode(system, system.root(), ["ControlSet0%02u" % current, "Control", "TimeZoneInformation"])
        for key in ['StandardName', 'DaylightName']:
            value = getValue(system, timezone, [], key)
            value = (value if value == None else system.value_string(value))
            timezoneInfo[key] = value

        #Explorer
        explorer = getNode(software, software.root(), ["Microsoft", "Windows", "CurrentVersion", "Explorer"])
        for key in ["Shell Folders", "User Shell Folders"]:
            node = software.node_get_child(explorer, key)
            if node != None:
                values = software.node_values(node)
                for value in values:
                    keyName = (software.value_key(value) if key == "Shell Folders" else "User %s" % software.value_key(value))
                    explorerInfo[keyName] = software.value_string(value)

        explorer = getNode(software, software.root(), ["Microsoft", "Windows NT", "CurrentVersion", "Winlogon"])
        for key in ["DefaultUserName", "DefaultDomainName"]:
            value = software.node_get_value(explorer, key)
            value = (value if value == None else software.value_string (value))
            explorerInfo[key] = value

        explorer = getNode(system, system.root(), ["ControlSet0%02u" % current, "Services", "LanManServer", "Shares"])
        if explorer != None:
            values = system.node_values(explorer)
            for value in values:
                explorerInfo[system.value_key(value)] = system.value_value(value)[1]

        return {self.__class__.__name__:{'Timezone':timezoneInfo, 'Explorer':explorerInfo}}

class GetSoftwareDetail:
    def main(self, software):
        hive, root = openHive(software)
        reg_uninstall = getNode(hive, root, ["Microsoft", "Windows", "CurrentVersion", "Uninstall"])

        softwares = {}
        if reg_uninstall == None:
            return {self.__class__.__name__:softwares}

        list_soft = hive.node_children(reg_uninstall)
        id = 0
        for reg in list_soft:
            value = getValue(hive, reg, [], "DisplayName")
            if value == None:
                continue
            displayName = hive.value_string(value)
            values = {}

            for key in ["ParentDisplayName", "ParentKeyName", "InstallLocation", "DisplayVersion"]:
                value = getValue(hive, reg, [], key)
                if value != None:
                    values[key] = hive.value_string(value)

            value = getValue(hive, reg, [], "InstallDate")
            if value != None:
                #FIXME: try except may hide problems, copy paste from initial script
                try:
                    value = hive.value_string(value)
                    values[key] = datetime.datetime.utcfromtimestamp(InstallDate).ctime()
                except:
                    pass

            for key in ["VersionMajor", "VersionMinor", "EstimatedSize"]:
                value = getValue(hive, reg, [], key)
                if value != None:
                    #FIXME: try except may hide problems, copy paste from initial script
                    try:
                        values[key] = hive.value_dword(value)
                    except:
                        pass

            id += 1
            softwares[displayName] = values

        return {self.__class__.__name__:softwares}

class GetUserEnvironmentDetail:
    def main(self, software):
        data = {}
        hive, root = openHive(software)
        node = getNode(hive, root, ["Microsoft", "Windows NT", "CurrentVersion", "ProfileList"])

        if node == None:
            return {self.__class__.__name__:data}

        list_key = hive.node_values(node)
        for item in list_key:
            data[hive.value_key(item)] = hive.value_string(item)

        value = getValue(hive, node, [], "ProfilesDirectory")
        if value != None:
            value = hive.value_string(value)
            value = value.split("\\", 2)
            data["HOMEDRIVE"] = value[0]

        return {self.__class__.__name__:data}

class GetSoftwareEnvironmentDetail:
    def main(self, software):
        data = {}
        hive, root = openHive(software)
        node = getNode(hive, root, ["Microsoft", "Windows", "CurrentVersion", "Explorer", "Shell Folders"])
        if node == None:
            return {self.__class__.__name__:data}

        list_key = hive.node_values(node)
        for item in list_key:
            data[hive.value_key(item)] = hive.value_string(item)

        value = getValue(hive, root, ["Microsoft", "Windows NT", "CurrentVersion"], "SYSTEMROOT")
        if value != None:
            value = hive.value_string(value)
            data["SYSTEMROOT"] = value
            value = value.split(":", 2)
            data["SYSTEMDRIVE"] = value[0] + ':'
        else:
            data["SYSTEMROOT"] = None
            data["SYSTEMDRIVE"] = None

        return {self.__class__.__name__:data}

class GetSystemEnvironmentDetail:
    def main(self, system):
        data = {}
        hive, root = openHive(system)
        current = getValue(hive, root, ["Select"], "Current")
        if current == None:
            return {self.__class__.__name__:data}
        current = hive.value_dword(current)
        node = getNode(hive, root, ["ControlSet0%02u" % current, "Control", "Session Manager", "Environment"])
        if node == None:
            return {self.__class__.__name__:data}

        list_key = hive.node_values(node)
        for item in list_key:
            data[hive.value_key(item)] = hive.value_string(item)

        return {self.__class__.__name__:data}

class WindowsRegistery(Process):
    def __init__(self, internLog, terminalLog, hardDrive, overWrite):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive_ = hardDrive
        self.overWrite_ = overWrite

    def run(self):
        self.internLog_.addLog("Windows registery extraction launched", 1)
        for partition in Partition.objects.filter(harddrive=self.hardDrive_):
            fileInfos = FileInfo.objects.filter(partition=partition)
            self.internLog_.addLog("partition", 1)
            hives = self.getHives(fileInfos, ["system", "security", "software"])
            if hives == None:
                continue

            self.internLog_.addLog("Hives found, and start extraction in partition %s" % partition, 1)
            mod = GetHardwareDetail()
            print "Entro"
            if self.overWriteCategory(partition, mod.__class__.__name__, self.overWrite_):
                print "me tiran"
                dic = mod.main(hives[0])
                self.updateDbGenericDic(dic, partition)
            mod = GetOSDetail()
            if (self.overWriteCategory(partition, mod.__class__.__name__, self.overWrite_)):
                dic = mod.main(hives[2])
                ##Update database with os of the partition
                os = dic['GetOSDetail']['ProductName']
                partition.os = os
                partition.save()
                self.updateDbGenericDic(dic, partition)
            mod = GetUserConfigurationDetail()
            if (self.overWriteCategory(partition, mod.__class__.__name__, self.overWrite_)):
                dic = mod.main(hives[0], hives[2], hives[1])
                self.updateDbGenericDic(dic, partition)
            mod = GetSoftwareDetail()
            if (self.overWriteCategory(partition, mod.__class__.__name__, self.overWrite_)):
                dic = mod.main(hives[2])
                self.updateDbGenericDic(dic, partition)

            mod = GetSystemEnvironmentDetail()
            if (self.overWriteCategory(partition, mod.__class__.__name__, self.overWrite_)):
                dic = mod.main(hives[0])
                self.updateDbGenericDic(dic, partition)
            mod = GetSoftwareEnvironmentDetail()
            if (self.overWriteCategory(partition, mod.__class__.__name__, self.overWrite_)):
                dic = mod.main(hives[2])
                self.updateDbGenericDic(dic, partition)
            mod = GetUserEnvironmentDetail()
            if (self.overWriteCategory(partition, mod.__class__.__name__, self.overWrite_)):
                dic = mod.main(hives[2])
                self.updateDbGenericDic(dic, partition)

    hardDrive_ = None
    overWrite_ = None