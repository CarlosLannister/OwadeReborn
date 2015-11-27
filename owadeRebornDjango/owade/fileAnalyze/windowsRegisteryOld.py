
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
__date__ ="$Jun 21, 2011 5:01:18 PM$"

import re
import os
import time
import hivex
import chardet

from owade.constants import *
from owade.process import  Process
from owade.models import Partition, FileInfo, HiveRegistery, NodeRegistery, ValueRegistery

class WindowsRegistery(Process):
    def __init__(self, internLog, terminalLog, hardDrive, overWrite):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive_ = hardDrive
        self.overWrite_ = overWrite

    def run(self):
        for partition in Partition.objects.filter(harddrive=self.hardDrive_):
            registery = self.loadDb(partition)
            for file in registery:
                self.extractKeys(file)
                if self.interupt_:
                    return
            if self.interupt_:
                return

    def loadDb(self, partition):
        registery = []
        filesInfo = FileInfo.objects.filter(partition=partition, dir_path__iexact="/windows/system32/config/")
        for fileInfo in filesInfo:
            if not fileInfo.name.lower() in ['default', 'sam', 'security', 'software', 'system', 'userdiff']:
                continue
            print fileInfo.name + " " + fileInfo.dir_path
            registery.append(fileInfo.file)
        filesInfo = FileInfo.objects.filter(partition=partition, dir_path__icontains="/documents and settings/", name__iexact="ntuser.dat")
        for fileInfo in filesInfo:
            print fileInfo.name + " " + fileInfo.dir_path
            registery.append(fileInfo.file)
        if len(registery) == 0:
            self.internLog_.addLog("No windows registery on this partition", 2)
        return registery

    def extractKeys(self, registery):
        self.internLog_.addLog("Extracting windows registery from %s" % registery.file_path(), 1)
        hiveRegistery = HiveRegistery.objects.get(file=registery)
        if hiveRegistery != None:
            if self.overWrite_:
                hiveRegistery.delete()
            else:
                self.internLog_.addLog("Windows registery already extract", 2)
                return False

        hive = hivex.Hivex(registery.file_path())
        node = hive.root()
        root = self.parc(hive, node, None)
        if root == None:
            return False
        hiveRegistery = HiveRegistery(file=registery, root=root)
        if not self.updateDb(hiveRegistery):
            return False
        return True

    def parc(self, hive, node, father):
        name = hive.node_name(node)
        nodeRegistery = NodeRegistery(name=name, father=father)
        if not self.updateDb(nodeRegistery):
            return None
        for value in hive.node_values(node):
            key = hive.value_key(value)
            #print "key:" + key
            type = hive.value_type(value)[0]
            #print type
            if type == 0:
                val = ""
            else:
                val = hive.value_value(value)[1]
                encod = chardet.detect(val)['encoding']
                if encod != None:
                    try:
                        val = val.decode(encod)#('utf-16le')#.encode('utf-8')
                        val = val.encod('utf-8')
                    except:
                        val = "" #FIXME: Some value are using an unknow encoding, not good for db, but maybe usefull
                else:
                    val = "" #FIXME: Some value are using an unknow encoding, not good for db, but maybe usefull
            #print val
            valueRegistery = ValueRegistery(key=key, type=type, value=val, node=nodeRegistery)
            if not self.updateDb(valueRegistery):
                return None
        for child in hive.node_children(node):
            self.parc(hive, child, nodeRegistery)
        return nodeRegistery

    hardDrive_ = None
    overWrite_ = None