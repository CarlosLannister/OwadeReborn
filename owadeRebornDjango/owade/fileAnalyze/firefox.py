
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

import tempfile
import shutil
import subprocess as subp
import os
import sys
import re

from owade.constants import KEY3DB_DIR
from owade.tools.domainFormater import format


class GetFirefoxPasswords:

    #%APPDATA%Mozilla\\Firefox\\Profiles\\{userid}.default\\key3.db
    #%APPDATA%Mozilla\\Firefox\\Profiles\\{userid}.default\\signons.sqlite
    def main(self, key3, signons, cert8):
        values = {}

        path = tempfile.mkdtemp()
        shutil.copyfile(key3, "%s/key3.db" % path)
        shutil.copyfile(signons, "%s/signons.sqlite" % path)
        shutil.copyfile(cert8, "%s/cert8.db" % path)

        ff_key3db_dump = "%s/ff_key3db_dump" % KEY3DB_DIR
        if not os.path.isfile(ff_key3db_dump):
            print >>sys.stderr, "Binary %s not found" % ff_key3db_dump
            return {self.__class__.__name__:values}

        process = subp.Popen([ff_key3db_dump, path], universal_newlines=True, stderr=subp.PIPE, stdout=subp.PIPE)
        stdout, stderr = process.communicate()

        id = 0
        for line in stdout.split('\n'):
            match = re.match(r'^([^,]*),[^,]*,([^,]*),([^,]*),([^,]*),([^,]*),([^,]*)$', line)
            if match:
                id += 1
                values["password%s" % id] = {'origin':match.group(1), 'submit':match.group(2),
                    'loginField':match.group(3), 'passwordField':match.group(4),
                    'login':match.group(5), 'password':match.group(6),
                    'domain':format(match.group(1))}
            match = re.match(r'^master password: "([^"]*)"$', line)
            if match:
                values["masterpassword"] = match.group(1)
        return {self.__class__.__name__:values}

#        try:
#            db = sqlite3.connect(signons)
#        except Exception as exp:
#            print exp.message
#            return {self.__class__.__name__: values}
#
#        cur = db.execute('select encryptedUsername, encryptedPassword from moz_logins')
#        users = cur.fetchall()
#        db.close()
#
#        for user in users:
#            print user[0]
#            print base64.b64decode(user[0])

# vim:ts=4:expandtab:sw=4
