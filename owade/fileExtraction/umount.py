
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

## Launch umount unix binary
class Umount(Launcher):
    def __init__(self, internLog, terminalLog, mount_path):
        Launcher.__init__(self, internLog, terminalLog)
        self.cmd_ = ["umount", mount_path]

    def final(self):
        if self.process_.returncode == 0:
            self.success_ = True
