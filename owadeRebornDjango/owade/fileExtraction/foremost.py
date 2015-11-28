
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

## Launch foremost unix binary
class Foremost(Launcher):
    def __init__(self, internLog, terminalLog, image, dumpDir):
        Launcher.__init__(self, internLog, terminalLog)
        self.cmd_ = ["foremost", "-i", image, "-o", dumpDir]

    def final(self):
        if self.process_.returncode == 0:
            self.success_ = True
