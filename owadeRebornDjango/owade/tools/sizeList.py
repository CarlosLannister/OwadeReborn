
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
__date__ ="$Aug 2, 2011 12:14:36 AM$"

class SizeList():
    def __init__(self):
        self.values_ = {}

    def add(self, value):
        if value in self.values_:
            self.values_[value] += 1
        else:
            self.values_[value] = 1

    def getList(self):
        return sorted(self.values_, key=self.values_.get, reverse=True)

    def getTuples(self):
        tuples = []
        for key in sorted(self.values_, key=self.values_.get, reverse=True):
            tuples.append((key, self.values_[key]))
        return tuples

    values_ = None