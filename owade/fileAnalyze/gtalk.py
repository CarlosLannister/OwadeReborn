
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

from DPAPI.Probes import gtalk

class GetGTalkAccounts:

    _descr = "Retreive and decrypt the Google Talk accounts in registry"

    ## Google talk accounts are stored in the registry, per user (ie ntuser.dat)
    ## HKCU\\Software\\Google\\Google Talk\\Accounts
    ## Every subkey is an account name (ie the login) that contains a "pw" value
    ##   which is the obfuscated DPAPI blob
    ## De-obfuscation requires 2 external values :
    ##  * windows account name (can be extracted either from ntuser.dat or
    ##      from the folder name that contains the ntuser.dat file
    ##  * netbios name of the computer that can be found in SOFTWARE hive
    ##      Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\DefaultDomainName value
    ##
    ##  accounts are expected as follow: 
    ##      { "login1": "<pw value>", "login2": "<pw value2>" }
    ##
    ## Finally, the last parameters are:
    ##  * mkp => the DPAPI masterkeypool (with keys already provisionned)
    ##  * sid => the user SID
    ##  * h => hashlib.sha1(userpassword.encode("UTF-16LE")).digest()
    def main(self, accounts, windowslogin, netbiosname, mkp, sid, h):
        values = {}

        i = 0
        for login in accounts.keys():
            b = gtalk.GTalkAccount(accounts[login])
            if b.try_decrypt_with_hash(h, mkp, sid,
                    login=login,
                    username=windowslogin,
                    computername=netbiosname):
                i += 1
                values["user%d" % i] = {
                        'login': login,
                        'password': b.cleartext
                        }

        return { self.__class__.__name__: values }

# vim:ts=4:expandtab:sw=4
