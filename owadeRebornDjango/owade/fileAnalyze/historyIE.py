
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

import os
import sys
import tempfile
import re
import subprocess as subp

from owade.constants import MSIECF_DIR
from owade.tools.domainFormater import format


class GetIEHistory:
    #indexes is a list of the path :
    #%USERPROFILE%Ashee/Local Settings/History/index.dat
    #%USERPROFILE%Ashee/Local Settings/History/*/index.dat
    def main(self, indexes):
        placeValues = {}
        formValues = {}

        binary = '%s/msiecftools/msiecfexport' % MSIECF_DIR
        if not os.path.isfile(binary):
            print >>sys.stderr, "Binary %s not found" % binary
            return {self.__class__.__name__:{'places':placeValues, 'forms':formValues}}

        i = 0
        for index in indexes:
            temp = tempfile.NamedTemporaryFile()
            subp.call([binary, index], universal_newlines=True, stdout=temp)
            temp.seek(0)
            url = ""
            date = ""
            for line in temp:
                if len(line) != 0 and line[-1] == '\n':
                    line = line[:-1]
                if line == "":
                    if url != "" and date != "":
                        i += 1
                        placeValues['place%d' % i] = {'url':url, 'date':date,
                            'domain':format(url)}
                    url = ""
                    date = ""
                    continue
                #FIXME: other "Location" that the "Visited" one but the other means less sense
                # Should be intereting to see if it's not forms or cookies related
                match = re.match(r'^Location[^:]*: Visited:[^@]*@(.*)$', line)
                if match != None:
                    url = match.group(1)
                match = re.match(r'^Primary filetime[^:]*: (.*)$', line)
                if match != None:
                    date = match.group(1)
            temp.close()

        return {self.__class__.__name__:{'places':placeValues, 'forms':formValues}}
