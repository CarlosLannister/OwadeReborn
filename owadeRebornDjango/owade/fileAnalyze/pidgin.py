
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

from xml.etree.ElementTree import ElementTree
from struct import *

#%APPDATA%.purple\\accounts.xml
class GetPidginAccounts:
    def main(self, accountXML):
        tree = ElementTree()
        tree.parse(accountXML)

        values = {}
        i = 0
        for nodes in tree.iter('account'):
            account = {}
            for node in list(nodes):
                if node.tag == "name":
                    account["name"] = node.text
                if node.tag == "password":
                    account["password"] = node.text
                if node.tag == "protocol":
                    account["protocol"] = node.text
            if "name" in account:
                i += 1
                values["user%d" % i] = account

        return {self.__class__.__name__:values}
    
# vim:ts=4:expandtab:sw=4
