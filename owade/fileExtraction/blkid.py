
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


## Launch blkid unix binary
class Blkid(Launcher):
    def __init__(self, internLog, terminalLog, drive):
        Launcher.__init__(self, internLog, terminalLog)
        self.cmd_ = ["blkid", drive]
        self.uuid_ = ""

    def final(self):
        self.uuid_ = ""
        log = self.terminalLog_.getLog(1)
        if len(log) != 0:
            match = re.search(r'UUID="([^\"]*)"', log[0]['line'])
            if match != None:
                self.uuid_ = match.group(1)
                self.success_ = True

    uuid_ = None