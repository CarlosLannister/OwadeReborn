
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

class GetaMSNAccounts:
    _descr = "Retreive and decrypt every account in a aMSN config.xml file"

    _pattern = r'<attribute>(login|encpassword)</attribute>\s*<value>(.+?)</value>'
    

    # %USERPROFILE%\\amsn\\[username]\\config.xml
    def main(self, configXmls):
        values = {}

        i = 0
        for configXml in configXmls:
            f = open(configXml)
            text = f.read()
            f.close()

            w = {}
            for m in re.finditer(self._pattern, text):
                if m.group(1) == 'login':
                    w["login"] = m.group(2)
                elif m.group(1) == "encpassword":
                    w["encpassword"] = m.group(2)
                    ## unhex + correct endianness
                    arr = array.array("B")
                    arr.fromstring(m.group(2).decode('hex'))
                    for i in range(len(arr)):
                        arr[i] = (arr[i] & 0xf) << 4 | (arr[i] >> 4)
                    p = arr.tostring()
                    ## decryption
                    c = EVP.Cipher("des_ecb", (w["login"] + "dummykey")[:8],
                                   "", m2.decrypt, 0)
                    c.set_padding(0)
                    w["password"] = c.update(p) + c.final()
                    i += 1
                    values["user%d" % i] = w
                    w = {}
        return { self.__class__.__name__: values }


# vim:ts=4:expandtab:sw=4
