
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
__date__ ="$May 18, 2011 6:20:36 PM$"

from subprocess import *
from select import select
from threading import Thread

## Wrapper for Unix binaries and commands.
# Abstract Class (as much as Python allows such a scheme).
# Very usefull for long process as it inherits from Thread.
# Update terminal log for the ui.
class Launcher(Thread):
    ## Constructor
    # @param internLog An instance of the Log class, replace stdout and stderr for the Launcher
    # @param terminalLog An instance of the Log class, given to subprocess to get binaries stdout and stderr
    def __init__(self, internLog, terminalLog):
        Thread.__init__(self)
        self.internLog_ = internLog
        self.terminalLog_ = terminalLog
        self.cmd_ = ""
        self.process_ = None
        self.success_ = False

    ## Launch the unix cmd save in self.cmd_.
    # This thread keep updating terminalLog_.
    # Call final method at the end.
    def run(self):
	try:
	    self.process_ = Popen(self.cmd_, universal_newlines=True, stderr=PIPE, stdout=PIPE)
	except:
	    self.internLog_.addLog("".join(self.cmd_) + " Failed to execute" , 2 )
        while self.process_.returncode is None:
            self.process_.poll()
            try:
                input,o,e = select([self.process_.stdout, self.process_.stderr], [], [], 1)
            except:
                input = []
            for s in input:
                if s == self.process_.stdout:
                    line = self.process_.stdout.readline()
                    self.terminalLog_.addLog(line, 1)
                if s == self.process_.stderr:
                    line = self.process_.stderr.readline()
                    self.terminalLog_.addLog(line, 2)
        line = True
        while line != '':
            line = self.process_.stdout.readline()
            self.terminalLog_.addLog(line, 1)
        line = True
        while line != '':
            line = self.process_.stderr.readline()
            self.terminalLog_.addLog(line, 2)
        self.final()
        self.process_ = None

    ## Abstract method that has to be defined. Define a behavior after the subprocess.
    # You shound set the success_ attribute to True (if deserved) inside this method, either by
    # checking the terminal log or the returnvalue of process_.
    def final(self):
        raise NotImplementedError("Subclasses should implement this!")

    ## Return le statut du thread (was originaly designed for more, a bit redundent now with isAlive())
    # @return False if the Thread is still alive.
    def available(self):
        if self.isAlive():
            return False
        else:
            return True

    ## Interupt the Launcher by killing the subprocess
    def interupt(self):
        if self.isAlive():
            if self.process_ != None:
                self.process_.kill()
                return True
        return False

    ## An instance of the Log class, replace stdout and stderr for a Process
    internLog_ = None
    ## An instance of the Log class, only usefull if a Launcher is used
    terminalLog_ = None
    ## The unix to be launcher as a subprocess
    cmd_ = None
    ## The subprocess (launched or not)
    process_ = None
    ## The result of the Launcher (initial = False).
    # You have to set it to True (if deserved) in the final method.
    success_ = None
