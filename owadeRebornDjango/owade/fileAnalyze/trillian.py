
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

from curses.ascii import isprint
import base64

class GetTrillianAccounts:
    _descr = "Retreive and decrypt every account in a Trillian accounts.ini file"

    _xorKey = ("f32681c43986db9271a3b9e6537a957c"+
            "000000000000ff000080000000808000ff"+
            "00000080008000808000000080ff008000"+
            "ff0080808000556e61626c6520746f2072"+
            "65736f6c766520485454502070726f7800").decode("hex")

    def format(self, value):
        str = value[:]
        while not isprint(str[-1]):
            str = str[:-1]
        return str

    # %APPDATA%Trillian\\users\\global\\accounts.ini
    # Account=<login>
    # Display Name=<display>
    # Password=ODc0OUY1QUIwOEI0RThBNgA=
    def main(self, accountFile):
        values = {}

        f = open(accountFile)
        l = f.readline()
        w = {}
        i = 0
        while l != "":
            if l[:8] == "Account=":
                w["login"] = self.format(l[8:])

            elif l[:13] == "Display Name=":
                w["displayName"] = self.format(l[13:])

            elif l[:9] == "Password=":
                password = l[9:]
                w["encpassword"] = self.format(password)
                p = base64.b64decode(password)[:-1].decode('hex')
                w["password"] = "".join([chr(ord(x) ^ ord(y))
                    for (x,y) in zip(p+"\0"*len(self._xorKey),self._xorKey)])[:len(p)]
                w["password"] = self.format(w["password"])
                i += 1
                values["user%d" % i] = w
                w = {}

            l = f.readline()
        f.close()

        return { self.__class__.__name__: values }

# vim:ts=4:expandtab:sw=4
