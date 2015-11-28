#!/usr/bin/env python

#############################################################################
##                                                                         ##
## This file is part of DPAPIck                                            ##
## Windows DPAPI decryption & forensic toolkit                             ##
##                                                                         ##
##                                                                         ##
## Copyright (C) 2010, 2011 Cassidian SAS. All rights reserved.            ##
## This document is the property of Cassidian SAS, it may not be copied or ##
## circulated without prior licence                                        ##
##                                                                         ##
##  Author: Jean-Michel Picod <jmichel.p@gmail.com>                        ##
##                                                                         ##
## This program is distributed under GPLv3 licence (see LICENCE.txt)       ##
##                                                                         ##
#############################################################################

from DPAPI.Probes import chrome
from DPAPI.Core import masterkey
import sqlite3
import hashlib, os
from optparse import OptionParser
import sys

class GetChromePasswords:

    _descr = "Retreive and decrypt the Google Chrome database"

    ## sqlite database is located under
    ## %LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Web Data (old)
    ## %LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Login Data (new)
    ## For winXP, %LOCALAPPDATA% = %USERPROFILE%\\Local Settings\\Application Data
    ## For Vista/win7, %LOCALAPPDATA% already exists in the environment
    def main(self, sqldbs, mkp, sid, h):
        values = {}
        i = 0

        fields = [ 'origin_url', 'action_url', 'username_element',
                   'username_value', 'password_element', 'password_value',
                   'date_created' ]

        for db in sqldbs:
            conn = sqlite3.connect(db)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT %s FROM logins" % ",".join(fields))
            for row in c:
                w = {}
                for f in fields:
                    w[f] = row[f]
                b = chrome.ChromePassword(w["password_value"])
                if b.try_decrypt_with_hash(h, mkp, sid):
                    w["password_value"] = b.cleartext
                else:
                    w["password_value"] = "<unable to decrypt>"
                values["chromeEntry%d" % i] = w
                i += 1
            c.close()
            conn.close()

        return { self.__class__.__name__: values }

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--sid", metavar="SID", dest="sid")
    parser.add_option("--masterkey", metavar="DIRECTORY", dest="masterkeydir")
    parser.add_option("--credhist", metavar="FILE", dest="credhist")
    parser.add_option("--password", metavar="PASSWORD", dest="password")
    parser.add_option("--hash", metavar="HASH", dest="h")
    parser.add_option("--chrome", metavar="CHROMEDB", dest="chromedbs",
                      action="append")

    (options, args) = parser.parse_args()

    if options.password and options.h:
        print >>sys.stderr,"Choose either password or hash option"
        sys.exit(1)
    if options.password:
        options.h = hashlib.sha1(options.password.encode("UTF-16LE")).hexdigest()
    options.h = options.h.decode('hex')

    mkp = masterkey.MasterKeyPool()
    mkp.loadDirectory(options.masterkeydir)

    if options.credhist != None:
        mkp.addCredhistFile(options.sid, options.credhist)

    fields = [ 'origin_url', 'action_url', 'username_element',
               'username_value', 'password_element', 'password_value',
               'date_created' ]

    values = []
    for db in options.chromedbs:
        if not os.path.isfile(db):
            continue
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT %s FROM logins" % ",".join(fields))
        for row in c:
            w = {}
            for f in fields:
                w[f] = row[f]
            b = chrome.ChromePassword(w["password_value"])
            if b.try_decrypt_with_hash(options.h, mkp, options.sid):
                w["password_value"] = b.cleartext
            else:
                w["password_value"] = "<unable to decrypt>"
            values.append(w)
        c.close()
        conn.close()

    s = [ "Chrome passwords" ]
    for e in values:
        s.append('-'*40)
        for f in fields:
            s.append("%s: %s" % (f, e[f]))
    print "\n".join(s)