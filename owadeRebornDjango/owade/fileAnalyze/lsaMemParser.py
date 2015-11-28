
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
__date__ ="$Jun 27, 2011 5:56:50 PM$"

import re

from owade.constants import *
from owade.process import Process
from owade.launcher import Launcher
from owade.models import HardDrive,Partition,File,FileInfo


class LsaMemParser(Process):
    def __init__(self, internLog, terminalLog, hardDrive, overWrite):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive_ = hardDrive
        self.overWrite_ = overWrite

    def run(self):
        for partition in Partition.objects.filter(harddrive=self.hardDrive_):
            for fileInfo in FileInfo.objects.select_related().filter(partition=partition, file__extension='sys'):
                lsaMemLauncher = LsaMemLauncher(self.internLog_, self.terminalLog_, fileInfo.file.file_path())
                if not self.launch(lsaMemLauncher):
                    if self.interupt_:
                        return
                    continue
                print "success"
                if self.interupt_:
                    return

    hardDrive_ = None
    overWrite_ = None


## Launch blkid unix binary
class LsaMemLauncher(Launcher):
    def __init__(self, internLog, terminalLog, file):
        Launcher.__init__(self, internLog, terminalLog)
        self.cmd_ = ["python", "/media/raid0/Owade/ivan/LsaMemParser.py", file]

    def final(self):
        logs = self.terminalLog_.getLog()
        if len(logs) != 0:
            for log in logs:
                match = re.search(r'SHA1', log['line'])
                if match != None:
                    self.success_ = True
                    print log['line']
                    return