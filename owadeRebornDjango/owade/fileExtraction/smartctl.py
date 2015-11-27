
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

import re

from owade.launcher import Launcher

## Launch smartctl unix binary
class Smartctl(Launcher):
    def __init__(self, internLog, terminalLog, drive):
        Launcher.__init__(self, internLog, terminalLog)
        self.cmd_ = ["smartctl", "--info", drive]
        self.serial_ = ""
        self.size_ = ""


    def final(self):
        log = self.terminalLog_.getLog(15)
        for entry in log:
            match = re.search(r'^Serial Number: *(.*)$', entry['line'])
            if match != None:
                self.serial_ = match.group(1)
            match = re.search(r'^User Capacity: *(.*) bytes', entry['line'])
            if match != None:
                self.size_ = match.group(1).replace(',','')
        if self.serial_ != "" and self.size_ != "":
            self.success_ = True
            

    serial_ = None
    size_ = None