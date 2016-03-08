from DPAPI.Core import masterkey
from DPAPI.Core import registry
from DPAPI.Probes import dropbox
from DPAPI.Core import blob
import sqlite3
import re
import os
import binascii

class GetOutlookPassword:

    def getOutlookPassword(self, mkpDir, sid, credHist, ntUser, userPassword):
        dic = {}

        '''
        OutlokkMasterkey = "/home/hackaton/Escritorio/dropbox/Archivos necesarios/Protect/S-1-5-21-3173276068-3308429807-3105269238-1000"
        OutlookSID = "S-1-5-21-3173276068-3308429807-3105269238-1000"
        OutlookCredhist = "/home/hackaton/Escritorio/dropbox/Archivos necesarios/Protect/CREDHIST"
        Ntuser = "/home/hackaton/Escritorio/dropbox/Archivos necesarios/NTUSER.DAT"
        Userpassword = "lazarus2015"'''

        mkp = masterkey.MasterKeyPool()

        mkp.loadDirectory(mkpDir)
        mkp.addCredhistFile(sid, credHist)
        mkp.try_credential(sid, userPassword)  # Credential of the USER

        email = []
        password = []
        # Open the registry
        with open(ntUser, 'rb') as f:
            r = registry.Registry.Registry(f)
            # Path of the Outlook file in Registry
            directory = r.open(
                'Software\\Microsoft\\Office\\15.0\\Outlook\\Profiles\\Outlook\\9375CFF0413111d3B88A00104B2A6676')
            for reg in directory.subkeys():
                auxreg = []
                for regnumber in reg.values():  # 000001 000002 000003.....
                    auxreg.append(regnumber.name())
                    # For IMAP
                    if "IMAP Password" in auxreg:
                        username = reg.value('Email').value()
                        password = reg.value('IMAP Password').value()
                        break
                    # For POP3
                    if "POP3 Password" in auxreg:
                        username = reg.value('Email').value()
                        password = reg.value('POP3 Password').value()
                        break
                    # Function de hacer cosas
        for char in username:
            if char.encode("hex") != "00":
                email.append(char)
        finalusername = ''.join(email)
        dic['user'] = finalusername

        # File to create the blob
        fi = open("blob", 'w')

        notruncate = password  # This password is not truncated, need to delete the first byte
        passwordhex = password.encode("hex")  # Convert the hex to hexadecimal
        binstr = binascii.unhexlify(passwordhex[2:])  # The blop does not need the first byte.
        fi.write(binstr)  # Write the blop in a file
        fi.close()

        blob1 = blob.DPAPIBlob(open('blob', 'rb').read())  # Load the blop from the file
        finalpass = []
        mks = mkp.getMasterKeys(blob1.mkguid)
        for mk in mks:
            if mk.decrypted:
                blob1.decrypt(mk.get_key())
                if blob1.decrypted:
                    password = blob1.cleartext
                    for char in password:
                        if char.encode("hex") != "00":
                            finalpass.append(char)
        finalpassword = ''.join(finalpass)
        dic['password'] = finalpassword
        try:
            os.remove("blob")
        except:
            pass
        return { self.__class__.__name__: dic }

    def main(self, mkpDir, sid, credHist, ntUser, userPassword):
        dic = self.getOutlookPassword(mkpDir, sid, credHist, ntUser, userPassword)
        return dic