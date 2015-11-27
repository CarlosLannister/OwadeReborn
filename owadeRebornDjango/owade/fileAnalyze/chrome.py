from DPAPI.Probes import chrome
from DPAPI.Core import masterkey
import sqlite3
import hashlib
from owade.constants import *

class GetChromePasswords:

    _descr = "Retreive and decrypt the Google Chrome database"

    def getChromePass(self, sqldbs, mkp, sid, h):
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

    def main(self, myPath, mkpDir, sid, password):
        print "--", "Getting chrome passwords"
        try:
            database = []
            database.append(myPath + "/chrome/" + chromeLoginFile)

            mkp = masterkey.MasterKeyPool()
            mkp.loadDirectory(mkpDir)

            passHash = hashlib.sha1(password.encode("UTF-16LE")).hexdigest().decode('hex')

            pwords = self.getChromePass(database, mkp, sid, passHash)
            return pwords
        except Exception, e:
            print e
            return None
