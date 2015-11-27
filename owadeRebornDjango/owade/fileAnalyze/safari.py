
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

from DPAPI.Probes import safari

from owade.tools.domainFormater import format

class GetSafariPasswords:

    _descr = "Retreive and decrypt the Safari keychain.plist"

    ## First parameter is the keychain file path, generally this is:
    ##     %APPDATA%\\Apple Computer\\Preferences\\keychain.plist
    ##
    ## Finally, the last parameters are:
    ##  * mkp => the DPAPI masterkeypool (with keys already provisionned)
    ##  * sid => the user SID
    ##  * h => hashlib.sha1(userpassword.encode("UTF-16LE")).digest()
    def main(self, keychainfile, mkp, sid, h):
        values = {}

        i = 0
        saf = safari.SafariFile()
        saf.preprocess( keychain=keychainfile )
        if saf.try_decrypt_with_hash(h, mkp, sid):
            for e in saf.entries:
                elems = e.copy()
                i += 1
                key = "password%d" % i
                values[key] = {}
                for elem in elems:
                    if elem == 'Account':
                        values[key]['login'] = elems[elem]
                    elif elem == 'Password':
                        values[key]['password'] = elems[elem]
                    elif elem == 'Server':
                        values[key]['origin'] = elems[elem]
                        values[key]['domain'] = elems[elem]
                    else:
                        values[key][elem] = elems[elem]

        return { self.__class__.__name__: values }


# vim:ts=4:expandtab:sw=4
