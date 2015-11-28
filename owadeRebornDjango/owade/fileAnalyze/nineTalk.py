
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
#!/usr/bin/env python

import re
import array
from M2Crypto import EVP,m2

class GetNineTalkAccounts():
    _descr = "Retreive and decrypt the 9Talk SIP account in user.config file"

    _pattern = r'<login><!\[CDATA\[(.+?)\]\]></login>.*<password><!\[CDATA\[(.+?)\]\]></password>'

    #FIXME : It was ninetalf.config in my ninetalk version, is it generic ?
    ## USERPROFILE%\\neuftalk\\user.config
    def main(self, userConfig):
        values = {}

        f = open(userConfig)
        text = f.read()
        f.close()

        w = {}
        i = 0
        for m in re.finditer(self._pattern, text):
            w["login"] = m.group(1)
            w["encpassword"] = m.group(2)
            ## decryption
            arr.fromstring(m.group(2).decode('hex'))
            for i in len(arr):
                arr[i] ^= 9
            w["password"] = arr.tostring()
            i += 1
            values["user%d" % i] = w
            w = {}

     
        return { self.__class__.__name__: values }


# vim:ts=4:expandtab:sw=4
