
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
__date__ ="$Aug 3, 2011 5:00:56 AM$"

from owade.process import Process
from owade.tools.sizeList import SizeList

class History(Process):
    def __init__(self, internLog, terminalLog, partition):
        Process.__init__(self, internLog, terminalLog)
        self.partition_ = partition

    def run(self):
        dic = self.getDbGenericDic('ProgramAnalyze', self.partition_)
        if dic == None:
            self.domains_ = []
            return

        domains = SizeList()
        for user in dic:
            user = dic[user]
            if not type(user) == dict:
                continue
            for name in ['GetIEHistory', 'GetChromeHistory',
                'GetFirefoxHistory', 'GetSafariHistory']:
                places = user.get(name)
                if places == None:
                    continue
                places = places.get('places')
                if places == None:
                    continue
                for place in places:
                    place = places[place]
                    if place['domain'] != None:
                        domains.add(place['domain'])

        self.domains_ = domains.getTuples()


    partition_ = None
    domains_ = None