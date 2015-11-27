
import sys
import re
from owade.constants import *
from owade.process import Process
from owade.models import *


#BROWSER

from owade.fileAnalyze.historyFirefox import GetFirefoxHistory
from owade.fileAnalyze.chrome import GetChromePasswords
from owade.fileAnalyze.historyChrome import GetChromeHistory
from owade.fileAnalyze.hashcatLib.pwdump import PwDump

'''
class Paths:
    ntfs = "NTFS (0x07)"
    usersPath = "/Users/"
'''



class ProgramAnalyze(Process):

    def __init__(self, internLog, terminalLog, hardDrive, overWrite):
        Process.__init__(self, internLog, terminalLog)  # Each Object Extractor has its own harddrive
        self.hardDrive = hardDrive
        self.overWrite = overWrite

    def run(self):
        self.internLog_.addLog("Getting data from extracted files", 1)
        folders = os.listdir(FILE_DIR)
        for folder in folders:
            if self.hardDrive.serial in folder:  # check if harddrive is in the folder's name
                sam = FILE_DIR + folder + "/SAM/SAM"  # Here is the SAM
                system = FILE_DIR + folder + "/SYSTEM/SYSTEM"  # Here is the SYSTEM

                #Password Cracking
                passwordDic = {} #User;Password
                mod = PwDump()
                passwordDic = mod.main(system, sam)
                partitionPath = FILE_DIR + folder + "/Users/"
                users = os.listdir(partitionPath)
                infos = {}

                for user in users:  # For each user in partition
                    userInfos = {}
                    myPath = partitionPath + user
                    userProtectDir = myPath + self.protectDir
                    self.password = passwordDic[user]
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
                            userInfos.update(dic)

                        mod = GetChromeHistory(myPath)
                        dic = mod.main(myPath)
                        if dic != None:
                            userInfos.update(dic)

                    else:
                        self.internLog_.addLog("Unable to decrypt Chrome Password DB.", 1)


                    mod = GetFirefoxHistory()
                    dic = mod.main(myPath)      # no saca dic
                    if dic != None:
                        userInfos.update(dic)

                    infos[user] = userInfos
                    # self.updateDbGenericDic({self.__class__.__name__:infos}, partition)
                    # Resto de modulos de extraer datos aqui

'''
hdrive = "777666AA_image"
ex = Extrator(hdrive, "lazarus2015")
ex.extractFiles()
ex.extractData()'''
