
import sys
import re
from owade.constants import *
from owade.process import Process
from owade.models import *


#BROWSER

from owade.fileAnalyze.historyFirefox import GetFirefoxHistory
from owade.fileAnalyze.chrome import GetChromePasswords
from owade.fileAnalyze.historyChrome import GetChromeHistory
from owade.fileAnalyze.hashcatLib.pwdump import Pwdump


'''
class Paths:
    ntfs = "NTFS (0x07)"
    usersPath = "/Users/"
'''

class ProgramAnalize(Process):

    def __init__(self, internLog, terminalLog, harddrive, overWrite):
        Process.__init__(self, internLog, terminalLog)  # Each Object Extractor has its own harddrive
        self.harddrive = harddrive
        self.overWrite = overWrite

    def run(self):
        print "\n\nGetting data from extracted files"
        folders = os.listdir(FILE_DIR)
        for folder in folders:
            if self.harddrive in folder:  # check if harddrive is in the folder's name
                sam = FILE_DIR + folder + "/SAM/SAM"  # Here is the SAM
                system = FILE_DIR + folder + "/SYSTEM/SYSTEM"  # Here is the SYSTEM

                mod = Pwdump()
                dic = mod.main(system, sam)
                if dic != None:
                    #Add to database
                    pass

                partitionPath = FILE_DIR + folder + "/Users/"
                users = os.listdir(partitionPath)
                for user in users:  # For each user in partition
                    myPath = partitionPath + user
                    userProtectDir = myPath + self.protectDir
                    files = os.listdir(userProtectDir)
                    for fi in files:
                        if re.match("S-1-5-21-[0-9]+-[0-9]+-[0-9]+-[0-9]+",
                                    fi):  # User's sid is the name of the only folder in protect
                            sid = fi  # Here is the SID
                    mkpDir = userProtectDir + sid  # Here is the masterkey directory

                    # Start getting the data

                    if self.password != None:
                        mod = GetChromePasswords()
                        dic = mod.main(myPath, mkpDir, sid, self.password)
                        if dic != None:
                            #Add to database
                            pass
                        mod = GetChromeHistory(myPath)
                        dic = mod.main(myPath)
                        if dic != None:
                            #Add to database
                            pass
                    else:
                        print "Unable to decrypt. Password required."

                    mod = GetFirefoxHistory()
                    dic = mod.main(myPath)      # no saca dic
                    if dic != None:
                        #Add to database
                        pass

                    # Resto de modulos de extraer datos aqui

'''
hdrive = "777666AA_image"
ex = Extrator(hdrive, "lazarus2015")
ex.extractFiles()
ex.extractData()'''
