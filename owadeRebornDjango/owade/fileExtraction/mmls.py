
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

## Launch mmls unix binary
class Mmls(Launcher):
    def __init__(self, internLog, terminalLog, image_path):
        Launcher.__init__(self, internLog, terminalLog)
        self.cmd_ = ["mmls", image_path]
        self.partitions_ = []

    def final(self):
        log = self.terminalLog_.getLog()
        for entry in log:
            match = re.search(r'^[0-9]*: *([0-9]*):[0-9]* *([0-9]*) *[0-9]* *([0-9]*) *(.*)$',
                entry['line'])
            if match != None:
                self.partitions_.append({'slot':match.group(1), 'offset':match.group(2),
                    'size':match.group(3), 'type':match.group(4)})
        if len(self.partitions_) != 0:
            self.success_ = True
            

    partitions_ = None