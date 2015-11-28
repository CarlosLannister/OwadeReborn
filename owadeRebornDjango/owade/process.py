
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
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="ashe"
__date__ ="$Jun 3, 2011 2:53:46 PM$"

import re
from threading import Thread

from owade.models import Value
from owade.models import Category
from owade.launcher import Launcher

from owade.models import *
from threading import Thread


## Main class of every owade's process, inherit from thread as you don't want the ui to be frozen.
# Abstract Class (as much as Python allows such a scheme).
# Define mostly methods for the ui.
# To create a new Process, you have to define __init__ and run.
class Process(Thread):
    ## Constructor
    # @param internLog An instance of the Log class, replace stdout and stderr for a Process
    # @param terminalLog An instance of the Log class, only usefull if a Launcher is used
    def __init__(self, internLog, terminalLog):
        Thread.__init__(self)
        self.internLog_ = internLog
        self.terminalLog_ = terminalLog
        self.interupt_ = False
        self.launcher_ = Launcher(internLog, terminalLog)

    ## Define the main behaviour of your process (Abstract method)
    def run(self):
        raise NotImplementedError("Subclasses should implement this!")

    ## Set everything to start an instance of the Launcher class
    # @param launcher The instance of the Launcher class
    # @return Boolean The result of the Launcher execution
    def launch(self, launcher):
        self.launcher_ = launcher
        launcher.start()
        launcher.join()
        return launcher.success_

    ## Interupt the Process
    # @return Boolean Success or failure or the interuption
    def interupt(self):
        self.interupt_ = True
        if self.launcher_.is_alive():
            self.launcher_.interupt()
            self.launcher_.join(10)
        else:
            return True
        if self.launcher_.is_alive():
            return False
        else:
            return True

    ## Update an instance of Model in the database, catch exception
    # @param obj The instance of the Model class
    def updateDb(self, obj):
        try:
            obj.save()
        except Exception as exp:
            try:
                self.internLog_.addLog("Update database failed, obj: %s, exception: %s" % (str(obj), str(exp)), 2)
            except Exception as exp2:
                self.internLog_.addLog("Update database failed: exception: %s" % (str(exp)), 2)
            return False
        return True

    descriptionToken = 'O_DESCRIPTION'
    def recurseUpdateDbGenericDic(self, dic, partition, father):
        for key in dic:
            if key == self.descriptionToken:
                continue
            value = dic[key]
            if type(value) == dict:
                #New category
                description = ""
                if self.descriptionToken in value:
                    description = value[self.descriptionToken]
                category = Category(name=key, description=description, partition=partition, father=father)
                category.save()
                self.recurseUpdateDbGenericDic(value, None, category)
            else:
                #New key value
                valueModel = Value(key=key, value=value, category=father)
                valueModel.save()


    def updateDbGenericDic(self, dic, partition):
        try:
            self.recurseUpdateDbGenericDic(dic, partition, None)
        except Exception as exp:
            print exp.message
            self.internLog_.addLog("Update database failed for dic %s" % (str(dic)), 2)
            return False
        self.internLog_.addLog("Update database success", 1)
        return True

    def recurseGetDbGenericDic(self, father):
        dic = {}
        for category in father.category_set.all():
            dic[category.name] = self.recurseGetDbGenericDic(category)
        for value in father.value_set.all():
            dic[value.key] = value.value
        return dic

    def getDbGenericDic(self, name, partition, father=None):
        try:
            father = Category.objects.select_related().get(name__iexact=name, partition=partition, father=father)
        except Exception as exp:
            print exp
            return None
        return self.recurseGetDbGenericDic(father)

    def overWriteCategory(self, partition, name, overWrite):
        try:
            category = Category.objects.get(partition=partition, name__iexact=name)
            if not overWrite:
                self.internLog_.addLog("%s already done" % name, 2)
                return False
            self.internLog_.addLog("Deleting old database content because of overwrite option (%s)" % name, 1)
            category.delete()
            return True
        except Exception as exp:
            return True

    def getHives(self, fileInfos, names):
        hives = fileInfos.filter(dir_path__iexact="/windows/system32/config/")
        paths = []
        if len(hives) == 0:
            print 'Error in getHives: no hives found'
            return None
        try:
            for name in names:
                paths.append(hives.get(name__iexact=name).file.file_path())
        except Exception as exp:
            print 'Exception in getHives: %s' % exp.message
            return None
        return paths

    def getUserHives(self, fileInfos):
        hives = fileInfos.filter(dir_path__istartswith="/Documents and Settings/", name__iexact="ntuser.dat")
        if len(hives) == 0:
            print 'Error in getUserHives: no hives found'
            return None
        paths = {}
        for hive in hives:
            user = re.search(r'^/[^/]*/([^/]*)/$', hive.dir_path).group(1)
            paths[user] = hive
        return paths

    ## An instance of the Log class, replace stdout and stderr for a Process
    internLog_ = None
    ## An instance of the Log class, only usefull if a Launcher is used
    terminalLog_ = None
    ## Has the process been interupted (initial = False)
    interupt_ = None
    ## An instance of the Launcher class, needed for user interuption
    launcher_ = None