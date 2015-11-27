
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

## Launch md5sum unix binary
class Hash(Launcher):
    def __init__(self, internLog, terminalLog, path):
        Launcher.__init__(self, internLog, terminalLog)
        self.cmd_ = ["md5sum", path]
        self.hash_ = ""

    def final(self):
        if self.process_.returncode != 0:
            return
        log = self.terminalLog_.getLog(1)
        match = re.search(r'^([0-9a-f]*) *.*$', log[0]['line'])
        if match != None:
            self.hash_ = match.group(1)
            self.success_ = True

    hash_ = None