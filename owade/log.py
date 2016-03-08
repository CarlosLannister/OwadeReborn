
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
__date__ ="$Jun 3, 2011 3:09:44 PM$"

import sys
import threading

## Log class of Owade, keep stdout and stderr to be displayed on the ui.
# Log is thread safe
class Log():
    ## Constructor
    # @param flush If true, log size is respected and one line is droped when one is added.
    # Don't set to False for a terminal Log !
    # @param size The size of the log, useless if flush = False
    def __init__(self, flush = True, size = 20):
        self.log_ = []
        self.logSize_ = size
        self.flush_ = flush
        self.lock_ = threading.Lock()

    ## Add one line to the log
    # @param line The line to be added
    # @param std 1 for stdout, 2 for stderr
    def addLog(self, line, std):
        if (std != 1 and std != 2):
            return False
        if (len(line) == 0):
            return True
        self.lock_.acquire()
        if self.flush_ and len(self.log_) >= self.logSize_:
            self.log_.pop(0)
        if line[-1] == '\n':
            self.log_.append({"std":std, "line":line[:-1]})
        else:
            self.log_.append({"std":std, "line":line})
        self.lock_.release()
        return True

    ## Get the current state of the log
    # @param size if size <= 0 (default), all the log is given, else size lines
    def getLog(self, size = 0):
        self.lock_.acquire()
        curSize = len(self.log_)
        if size <= 0 or curSize <= size:
            log = self.log_[:]
        else:
            log = self.log_[-size:]
        self.lock_.release()
        return log

    ## Print the content of the log on stdout and stderr
    def dump(self):
        for line in self.log_:
            if line.std == 1:
                print line.line
            if line.std == 2:
                print >>sys.stderr, line.line

    ## List of the lines from stdout and stderr
    log_ = None
     ## If True, the log drops one line everytime a new line made him go over logSize_
    flush_ = None
    ## The max size of the log if flush_ == True
    logSize_ = None
    ## The lock for the list to be thread safe
    lock_ = None
