
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
__date__ ="$Jun 2, 2011 7:13:22 PM$"

import re
import os

from owade.constants import *
from owade.process import Process
from owade.fileExtraction.smartctl import Smartctl
from owade.fileExtraction.ddrescue import DDrescue
from owade.models import HardDrive



## Add a new hard drive connected to the computer into the database.
# Create an image of the hard drive on the Owade server using ddrescue.
class NewHardDrive(Process):
    ## Constructor
    # @param internLog An instance of the Log class, replace stdout and stderr
    # @param terminalLog An instance of the Log class, use by DDrescue class
    # @param hardDrive The hard drive to add (shound be a unix device)
    # @param overWrite Define if the process should overwrite the database if this serial is already known
    def __init__(self, internLog, terminalLog, hardDrive, overWrite, retry=3):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive_ = hardDrive
        self.overWrite_ = overWrite
        if retry < 0:
            retry = 0
        if retry > 3:
            retry = 3
        self.retry_ = retry

    ## Main method.
    # Get the serial number using smartctl.
    # Copy the hard drive using ddrescue.
    # Update the database
    def run(self):
        #Check hard drive and get uuid
        self.internLog_.addLog("Check hard drive and get serial", 1)
        if re.match("^/dev/sd[a-z]$", self.hardDrive_) == None:
            self.internLog_.addLog("Specify an entire hard drive (not a partition for example)", 2)
            return
        smartctl = Smartctl(self.internLog_, self.terminalLog_, self.hardDrive_)
        if not self.launch(smartctl):
            self.internLog_.addLog("Hard drive is incorrect", 2)
            return
        serial = smartctl.serial_
        size = smartctl.size_
        self.internLog_.addLog("Hard drive : serial %s, size %s" % (serial, size), 1)
        if self.interupt_:
            return

        #Check existence in db
        hd = HardDrive.objects.filter(serial=serial)
        if hd.count() > 0:
            if self.overWrite_ == False:
                self.internLog_.addLog("The hard drive is already in the database", 2)
                return
            self.internLog_.addLog("Overidding the hard drive", 2)
            hd = hd[0]
            os.remove(hd.image_path())
            os.remove(hd.log_path())
        else:
            hd = HardDrive(serial=serial, size=size)
        if self.interupt_:
            return

        #DDrescue
        self.internLog_.addLog("DDrescue the hard drive", 1)
        ddrescue = DDrescue(self.internLog_, self.terminalLog_, self.hardDrive_,
            hd.image_path(), hd.log_path(), self.retry_)
        if not self.launch(ddrescue):
            self.internLog_.addLog("DDrescue execution failed", 2)
            return
        if self.interupt_:
            return

        # update db
        if not self.updateDb(hd):
            return
        self.internLog_.addLog("Add new hard drive done, database updated", 1)

    hardDrive_ = None
    overWrite_ = None
    retry_ = None

