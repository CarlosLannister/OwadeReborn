
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
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="ashe"
__date__ ="$Jun 2, 2011 6:56:43 PM$"


from owade.process import Process
from owade.fileExtractor.extract import GetFiles
from owade.fileAnalyzer.programAnalyze import ProgramAnalyze
from owade.log import Log


## Wrapper between the UI and the different Process.
# Check that only one process at a time is launched.
class Program:
    def __init__(self):
        self.reset()

    def reset(self):
        self.internLog_ = Log(False)
        self.terminalLog_ = Log(True, 20)
        self.thread_ = Process(self.internLog_, self.terminalLog_)

    tasks_form_ = (
        ('0', 'Extract files from dump'),
        #('1', 'Files analysis'),
        #('2', 'Extract windows registery'),
        #('3', 'Extract data from sys files'),
        #('4', 'Get password in sam'),
        ('5', 'Program analysis'),
        #('6', 'Web analysis'),
        )

    def task(self, id, *args, **kwargs):
        values = {
            '0':GetFiles,
            #'1':FilesStatistics,
            #2':WindowsRegistery,
            #'3':LsaMemParser,
            #'4':UserPassword,
            '5':ProgramAnalyze,
            #'6':WebAnalyze,
            }
        return self.launch(values[id], *args, **kwargs)

    def single(func):
        def deco(self, *args, **kwargs):
            if self.thread_.is_alive():
                return False
            self.reset()
            func(self, *args, **kwargs)
            return True
        return deco

    @single
    def launch(self, task, *args, **kwargs):
        self.thread_ = task(self.internLog_, self.terminalLog_, *args, **kwargs)
        self.thread_.start()

    def interupt(self):
        if not self.thread_.is_alive():
            return True
        if not self.thread_.interupt():
            return False
        self.thread_.join(10)
        if self.thread_.is_alive():
            return False
        else:
            return True

    def available(self):
        if self.thread_.is_alive():
            return False
        return True

    thread_ = None
    internLog_ = None
    terminalLog_ = None

