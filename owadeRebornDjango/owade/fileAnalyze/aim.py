
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

import base64
from M2Crypto import EVP,m2

class GetAIMAccounts:

    _descr = "Retreive and decrypt every account for AIM in registry"

    dependency = []

    Key = ("0000000000000000990086a527aa9d7f"+
           "58aaaeb90b473a35aae0ea9566fbe49f"+
           "cbf7161ca392e61c96069b5b2930bfaf"
           "ec1129c8895bb857").decode("hex")


# From ntuser.dat -> Software/America Online/AIM6/
# Subkeys : [ 'Passwords', 'HashedPasswords' ]
# Each subkey contains list of values (login,password)
####
# example of corresponding .reg file
#
# [HKEY_CURRENT_USER\Software\America Online\AIM6\Passwords]
# "monlogin1" = "encryptedpassword"
# "monlogin2" = "encryptedpassword2"
#
# [HKEY_CURRENT_USER\Software\America Online\AIM6\HashedPasswords]
# "monlogin3" = "0123456789ABCDDEFFEDCBA9876543210"
#
## Expecting this python struct :
#
# { "HashedPasswords": { "monlogin3": "0123456789ABCDDEFFEDCBA9876543210" },
#   "Passwords": { "monlogin1": "encryptedpassword", "monlogin2": "encryptedpassword2" }
# }

    def main(self, registryKeys):
        values = {}

        ## first process hashed password
        for k in registryKeys["HashedPasswords"].keys():
            values[k] = { "login": k, "raw-md5": registryKeys["HashedPasswords"][k] }

        ## Then encrypted passwords
        for k in registyKeys["Passwords"].keys():
            p = base64.b64decode(registryKeys["Passwords"][k])
            cipher = EVP.Cipher("bf_ecb", p[:8], "", m2.decrypt, 0)
            password = cipher.update(p[8:]) + cipher.final()
            values[k] = { "login": k, "encryptedPassword": registryKeys["Passwords"][k],
                          "password": password }


        return { self.__class__.__name__: values }

# vim:ts=4:expandtab:sw=4
