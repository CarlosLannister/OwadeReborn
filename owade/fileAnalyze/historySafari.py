
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
__date__ ="$Jul 26, 2011 10:56:51 AM$"

import CFPropertyList as cfp

from owade.tools.domainFormater import format

class GetSafariHistory:
    #%APPDATA%\\Apple Computer\\Safari\\History.plist
    def main(self, history):
        placeValues = {}
        formValues = {}

        places = cfp.CFPropertyList(history)
        places.load()
        places = cfp.native_types(places.value)
        i = 0
        for place in places.get('WebHistoryDates', []):
            i += 1
            placeValues['place%d' % i] = {'url':place[''], 'title':place['title'],
                'count':place['visitCount'], 'date':place['lastVisitedDate'],
                'domain':format(place[''])}

        return {self.__class__.__name__:{'places':placeValues, 'forms':formValues}}