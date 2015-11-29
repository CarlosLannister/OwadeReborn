
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
__date__ ="$Jul 29, 2011 8:53:50 PM$"

import re

#FIXME : done in one minute and ugly
def format(url):
    if not re.match(r'^http', url):
        return None
    if re.match(r'https?://[^/.]*(:[0-9]{1,5})?(/.*)?$', url):
        return None
    match = re.match(r'^https?://([^/]*\.)*([^/.]*\.[^/.]{2}\.[^/.]{2,3})(:[0-9]{1,5})?(/.*)?$', url)
    if match == None:
        match = re.match(r'^https?://([^/]*\.)*([^/.]*\.com\.[^/.]{2,3})(:[0-9]{1,5})?(/.*)?$', url)
        if match == None:
            match = re.match(r'^https?://([^/]*\.)*([^/.]*\.[^/.]{2,4})(:[0-9]{1,5})?(/.*)?$', url)
            if match == None:
                match = re.match(r'^https?://([^/]*\.)*([^/.]*)(:[0-9]{1,5})?(/.*)?$', url)
                if match != None:
                    return match.group(1) + match.group(2)
                raise Exception("One case isn't dealed with: %s" % url)
    return match.group(2)
