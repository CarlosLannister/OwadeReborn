
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

from DPAPI.Probes import credstore

class GetCredentialStore:

    _descr = "Retreive and decrypt credentials stores via Credstore API"

    ## %APPDATA%\\Microsoft\\Credentials\\[sid]\\Credentials
    ## %USERPRFILE%\\Local Settings\\Application Data\\Microsoft\\Credentials\\[sid]\\Credentials
    ## Starting from Windows Vista, several credstores are handled.
    ## Names are GUIDs
    ##
    ## Basically, any file in the Credentials directory is a credstore
    def main(self, credstores, mkp, sid, h):
        values = {}

        i = 0
        for c in credstores:
            f = open(c)
            b = credstore.CredentialStore(f.read())
            f.close()
            if b.try_decrypt_with_hash(h, mkp, sid):
                for e in b.store.creds:
                    i += 1
                    values["user%d" % i] = {
                            'type': e.credtype,
                            'persist': e.persist,
                            'name': e.name,
                            'username': e.username,
                            'comment': e.comment,
                            'alias': e.alias
                            }

        return { self.__class__.__name__: values }


# vim:ts=4:expandtab:sw=4

