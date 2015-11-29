#!/usr/bin/python

__author__ = 'CarlosLannister'

import sys
import os
import os.path
import getopt
import subprocess as sub
from owade.constants import *
import psycopg2

## Check options (-h ...) and rights and launch Django server
class Owade:
    ## opt method : check and use opt given to Owade
    def opt(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
        except getopt.error, msg:
            print >>sys.stderr, msg
            self.usage(2)
        for o, a in opts:
            if o in ("-h", "--help"):
                self.usage(0)
        for arg in args:
            print arg

    ## Print usage
    # @param ret Return value of the exit after printing
    def usage(self, ret=0):
        print ""
        sys.exit(ret)

    def updateBD(self, IMG_DIR):
        id = 1
        for filename in os.listdir(IMG_DIR):
            print filename
            st = os.stat(IMG_DIR + "/" + filename)
            size = str(st.st_size)
            print size
            try:
                conn = psycopg2.connect("dbname='" + DATABASE_NAME + "' user='" + DATABASE_USER
                                        + "' host='" + DATABASE_HOST + "'password='"
                                        + DATABASE_PASSWORD + "'")
            except:
                print "Unable to connect to database"
            cur = conn.cursor()

            query = "INSERT INTO owade_harddrive (id, \"serial\", \"size\") "  \
                    "SELECT \'" + str(id) +"\',\'" + filename + "\',\'" + size + "\' WHERE NOT EXISTS " \
                    "(SELECT id,\"serial\", \"size\" FROM owade_harddrive WHERE id=\'" + str(id) + "\'"  \
                    " AND serial=\'" + filename + "\' AND size=\'" + size + "\');"
            print query
            try:
                cur.execute(query)
                conn.commit()
            except Exception as e:
                print e
            id = id + 1

    ## Create django db if first launching, then launch the server
    def launch(self):
        self.opt()
        if os.geteuid() != 0:
            print >>sys.stderr, "You need to be root to launch Owade"
            sys.exit(1)
        self.updateBD(IMAGE_DIR)
        #sub.call("./manage.py syncdb", shell=True)
        sub.call("./manage.py runserver 8080", shell=True)
        sys.exit(0)

if __name__ == "__main__":
    Owade().launch()