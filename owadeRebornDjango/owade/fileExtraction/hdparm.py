
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
__date__ ="$May 24, 2011 6:31:48 PM$"

from owade.launcher import Launcher
import re

## Launch hdparm unix binary
class Hdparm(Launcher):
    def __init__(self, internLog, terminalLog, drive):
        Launcher.__init__(self, internLog, terminalLog)
        self.cmd_ = ["hdparm", "-i", drive]
        self.serial_ = ""

    def final(self):
        self.serial_ = ""
        log = self.terminalLog_.getLog()
        for entry in log:
            match = re.search(r'SerialNo=(.*)$', entry['line'])
            if match != None:
                self.serial_ = match.group(1)
                self.success_ = True
                return

    serial_ = None