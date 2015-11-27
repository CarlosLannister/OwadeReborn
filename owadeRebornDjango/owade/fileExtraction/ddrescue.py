
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
__date__ ="$May 18, 2011 3:09:03 PM$"

import re

from owade.launcher import Launcher
from owade.constants import *


## Launch ddrescue unix binary
class DDrescue(Launcher):
    def __init__(self, internLog, terminalLog, drive, image, log, retry=3):
        Launcher.__init__(self, internLog, terminalLog)
        if retry == 0:
            self.cmd_ = ["ddrescue", drive, image, log]
        else:
            self.cmd_ = ["ddrescue", "-r%i" % retry, drive, image, log]

    def final(self):
        log = self.terminalLog_.getLog(1)
        if len(log) != 0:
            if re.search(r'Finished', log[0]['line']) != None:
                self.success_ = True
