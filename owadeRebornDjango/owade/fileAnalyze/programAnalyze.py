import sys
import re
from owade.constants import *
from owade.process import Process
from owade.models import *


# BROWSER

from owade.fileAnalyze.historyFirefox import GetFirefoxHistory
from owade.fileAnalyze.chrome import GetChromePasswords
from owade.fileAnalyze.historyChrome import GetChromeHistory
from owade.fileAnalyze.hashcatLib.pwdump import PwDump
from owade.fileAnalyze.firefox import GetFirefoxPasswords

'''
class Paths:
    ntfs = "NTFS (0x07)"
    usersPath = "/Users/"
'''


class ProgramAnalyze(Process):

    def __init__(self, internLog, terminalLog, hardDrive, overWrite, dictionary, chromePassword,
                 chromeHistory, firefoxPassword, firefoxHistory):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive = hardDrive
        self.overWrite = overWrite
        self.dictionary = dictionary
        self.chromePassword = chromePassword
        self.chromeHistory = chromeHistory
        self.firefoxPassword = firefoxPassword
        self.firefoxHistory = firefoxHistory

    def run(self):
        self.internLog_.addLog("Getting data from extracted files", 1)

        folders = os.listdir(FILE_DIR)
        for folder in folders:
            if self.hardDrive.serial in folder:  # check if harddrive is in the folder's name
                sam = FILE_DIR + "/" + folder + "/SAM/SAM"  # Here is the SAM
                system = FILE_DIR + "/" + folder + "/SYSTEM/SYSTEM"  # Here is the SYSTEM

                # Password Cracking
                if self.dictionary == "":
                    mod = PwDump()
                else:
                    mod = PwDump(self.dictionary)

                passwordDic = mod.main(system, sam)
                partitionPath = FILE_DIR + "/" + folder + "/Users/"
                users = os.listdir(partitionPath)
                infos = {}

                for user in users:  # For each user in partition
                    userInfos = {}
                    myPath = partitionPath + user
                    userProtectDir = myPath + protectDir
                    self.password = passwordDic[user]
                    files = os.listdir(userProtectDir)
                    for fi in files:
                        if re.match("S-1-5-21-[0-9]+-[0-9]+-[0-9]+-[0-9]+",
                                    fi):  # User's sid is the name of the only folder in protect
                            sid = fi  # Here is the SID
                    mkpDir = userProtectDir + sid  # Here is the masterkey directory

                    # Start getting the data
                    if self.chromePassword:
                        self.internLog_.addLog("Getting Chrome passwords", 1)
                        if self.password != None:
                            mod = GetChromePasswords()
                            dic = mod.main(myPath, mkpDir, sid, self.password)
                            print dic
                            if dic != None:
                                userInfos.update(dic)
                            else:
                                self.internLog_.addLog("Can't find Chrome passwords' database", 1)
                        else:
                            self.internLog_.addLog("Unable to decrypt Chrome passwords' databae.", 1)

                    if self.chromeHistory:
                        self.internLog_.addLog("Getting Chrome history", 1)
                        mod = GetChromeHistory()
                        dic = mod.main(myPath)
                        print dic
                        if dic != None:
                            userInfos.update(dic)
                        else:
                            self.internLog_.addLog("Can't find Chrome history database", 1)

                    if self.firefoxPassword:
                        self.internLog_.addLog("Getting Firefox passwords", 1)
                        mod = GetFirefoxPasswords()
                        dic = mod.main(myPath)
                        print dic
                        if dic != None:
                            userInfos.update(dic)
                        else:
                            self.internLog_.addLog("Can't find Firefox passwords' database", 1)

                    if self.firefoxHistory:
                        self.internLog_.addLog("Getting Firefox history", 1)
                        mod = GetFirefoxHistory()
                        dic = mod.main(myPath)
                        print dic
                        if dic != None:
                            userInfos.update(dic)
                        else:
                            self.internLog_.addLog("Can't find Firefox history database", 1)

                    infos[user] = userInfos
                    for user in infos:
                        print user
                        print infos[user]

                    #self.updateDbGenericDic({self.__class__.__name__:infos}, partitionPath)
                    # Resto de modulos de extraer datos aqui


