import sys
import re
from owade.constants import *
from owade.process import Process
from owade.models import *
import pandas as pd

# BROWSER

from owade.fileAnalyze.historyFirefox import GetFirefoxHistory
from owade.fileAnalyze.chrome import GetChromePasswords
from owade.fileAnalyze.historyChrome import GetChromeHistory
from owade.fileAnalyze.hashcatLib.pwdump import PwDump
from owade.fileAnalyze.firefox import GetFirefoxPasswords
from owade.fileAnalyze.wifi import GetWifiPassword
from owade.fileAnalyze.outlook import GetOutlookPassword
import datetime

class ProgramAnalyze(Process):

    def __init__(self, internLog, terminalLog, hardDrive, report, dictionary, chromePassword,
                 chromeHistory, firefoxPassword, firefoxHistory, wifi, outlook):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive = hardDrive
        self.report = report
        self.dictionary = dictionary
        self.chromePassword = chromePassword
        self.chromeHistory = chromeHistory
        self.firefoxPassword = firefoxPassword
        self.firefoxHistory = firefoxHistory
        self.wifi = wifi
        self.outlook = outlook

    def getReport(self, dic, myPath):
        self.getChromeHistoryReport(dic, myPath)
        self.getChromeDownloadsReport(dic, myPath)
        self.getChromePasswordsReport(dic, myPath)
        self.getFirefoxPasssordsReport(dic, myPath)
        self.getFirefoxHistoryReport(dic, myPath)
        self.getFirefoxDownloadsReport(dic,myPath)
        self.getOutlookReport(dic,myPath)

    def getChromeDownloadsReport(self, dic, myPath):
        urlList = []
        reportList = []
        for url in dic['GetChromeHistory']['download']:
            urlList.append(url.strip("URL "))
            urlList.append(dic['GetChromeHistory']['download'][url]["targetPath"])
            urlList.append(dic['GetChromeHistory']['download'][url]["endTime"])
            urlList.append(dic['GetChromeHistory']['download'][url]["receivedBytes"])
            reportList.append(urlList)
            urlList = []

        fullPath = myPath + "chromeDownloads.csv"
        ptest = pd.DataFrame(reportList , columns=['url', 'path', 'time', 'size' ])
        ptest.to_csv(fullPath, sep='\t', encoding='utf-8')
        self.internLog_.addLog("Chrome history report on " + fullPath, 1)

    def getChromeHistoryReport(self,dic, myPath):
        urlList = []
        reportList = []
        for url in dic['GetChromeHistory']['history']:
            urlList.append(url.strip("URL "))
            urlList.append(dic['GetChromeHistory']['history'][url]["lastVisit"])
            urlList.append(dic['GetChromeHistory']['history'][url]["firstVisit"])
            urlList.append(dic['GetChromeHistory']['history'][url]["visitNumber"])
            urlList.append(dic['GetChromeHistory']['history'][url]["title"])
            reportList.append(urlList)
            urlList = []

        fullPath = myPath + "chromeHistory.csv"
        ptest = pd.DataFrame(reportList , columns=['url', 'lastVisit', 'firstVisit', 'visitNumber', 'tittle' ])
        ptest.to_csv(fullPath, sep='\t', encoding='utf-8')
        self.internLog_.addLog("Chrome downloads report on " + fullPath, 1)

    def getChromePasswordsReport(self, dic, myPath):
        urlList = []
        reportList = []
        for entry in dic['GetChromePasswords']:
            urlList.append(dic['GetChromePasswords'][entry]['origin_url'])
            urlList.append(dic['GetChromePasswords'][entry]['username_value'])
            urlList.append(dic['GetChromePasswords'][entry]['password_value'])
            ms = dic['GetChromePasswords'][entry]['date_created']
            date = datetime.datetime.fromtimestamp(ms / 10000000.0)
            urlList.append(date)
            reportList.append(urlList)
            urlList = []

        fullPath = myPath + "chromePasswords.csv"
        ptest = pd.DataFrame(reportList , columns=['origin_url', 'username_value', 'password_value', 'date_created' ])
        ptest.to_csv(fullPath, sep='\t', encoding='utf-8')
        self.internLog_.addLog("Chrome passwords report on " + fullPath, 1)

    def getFirefoxPasssordsReport(self, dic, myPath):
        urlList = []
        reportList = []
        for entry in dic['GetFirefoxPasswords']:
            for url in dic['GetFirefoxPasswords'][entry]:
                urlList.append(entry)
                urlList.append(url)
                string = dic['GetFirefoxPasswords'][entry][url]
                splited = string.split(':')
                urlList.append(splited[0])
                urlList.append(splited[len(splited) - 1 ])
                reportList.append(urlList)
                urlList = []

        fullPath = myPath + "fireFoxPasswords.csv"
        ptest = pd.DataFrame(reportList , columns=['profile', 'url', 'username_value', 'password_value' ])
        ptest.to_csv(fullPath, sep='\t', encoding='utf-8')
        self.internLog_.addLog("Firefox passwords report on " + fullPath, 1)

    def getFirefoxHistoryReport(self, dic, myPath):
        urlList = []
        reportList = []
        for entry in dic['GetFirefoxHistory']:
            for url in dic['GetFirefoxHistory'][entry]:
                urlList.append(entry)
                urlList.append(url['url'])
                urlList.append(url['last_visit_date'])
                urlList.append(url['visit_count'])
                reportList.append(urlList)
                urlList = []

        fullPath = myPath + "fireFoxHistory.csv"
        ptest = pd.DataFrame(reportList , columns=['profile', 'url', 'last_visit_date', 'visit_count' ])
        ptest.to_csv(fullPath, sep='\t', encoding='utf-8')
        self.internLog_.addLog("Firefox history report on " + fullPath, 1)

    def getFirefoxDownloadsReport(self, dic, myPath):
        urlList = []
        reportList = []
        for entry in dic['GetFirefoxDownloads']:
            for url in dic['GetFirefoxDownloads'][entry]:
                urlList.append(entry)
                urlList.append(url['pathfile'])
                urlList.append(url['date'])
                urlList.append(url['size'])
                reportList.append(urlList)
                urlList = []


        fullPath = myPath + "fireFoxDownloads.csv"
        ptest = pd.DataFrame(reportList , columns=['profile', 'pathfile', 'date', 'size' ])
        ptest.to_csv(fullPath, sep='\t', encoding='utf-8')
        self.internLog_.addLog("Firefox downloads report on " + fullPath, 1)

    def getWifiReport(self, dic, myPath):
        urlList = []
        reportList = []
        for SSID in dic:
            urlList.append(SSID)
            urlList.append(dic[SSID])
            reportList.append(urlList)
            urlList = []

        fullPath = myPath + "wifi.csv"
        ptest = pd.DataFrame(reportList , columns=['SSID', 'password'])
        ptest.to_csv(fullPath, sep='\t', encoding='utf-8')
        self.internLog_.addLog("Wifi report on " + fullPath, 1)

    def getOutlookReport(self, dic, myPath):
        user = dic['GetOutlookPassword']['user']
        password = dic['GetOutlookPassword']['password']

        fullPath = myPath + "outlook.csv"
        ptest = pd.DataFrame([ [user, password] ] , columns=['user', 'password'])
        ptest.to_csv(fullPath, sep='\t', encoding='utf-8')
        self.internLog_.addLog("Outlook report on " + fullPath, 1)

    def run(self):
        self.internLog_.addLog("Getting data from extracted files", 1)
        infos = {}
        folders = os.listdir(FILE_DIR)
        for folder in folders:
            if self.hardDrive.serial in folder:  # check if harddrive is in the folder's name
                myPath = FILE_DIR + "/" + folder
                sam = myPath + "/SAM/SAM"  # Here is the SAM
                system = myPath + "/SYSTEM/SYSTEM"  # Here is the SYSTEM
                security = myPath + "/SECURITY/SECURITY"
                systemMaster = myPath + mySystemMasterKey
                wifiProfile = myPath + myWifiProfile

                if self.wifi:
                    self.internLog_.addLog("Getting Wifi data", 1)
                    mod = GetWifiPassword()
                    wifiDic = mod.main(system, security, systemMaster, wifiProfile)

                    if wifiDic == None:
                        self.internLog_.addLog("Can't find wifi files", 1)
                else:
                    pass

                # Password Cracking
                if self.dictionary == "":
                    mod = PwDump()
                else:
                    mod = PwDump(self.dictionary)

                passwordDic = mod.main(system, sam)
                partitionPath = FILE_DIR + "/" + folder + "/Users/"
                users = os.listdir(partitionPath)

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
                    credhist = userProtectDir + credhistFile
                    ntUserFile = myPath + "/NTUSER/" + NTUser
                    # Start getting the data

                    if self.outlook:
                        self.internLog_.addLog("Getting Outlook passwords", 1)
                        mod = GetOutlookPassword()
                        dic = mod.main(mkpDir, sid, credhist, ntUserFile, self.password)
                        print dic
                        if dic != None:
                            userInfos.update(dic)
                        else:
                            self.internLog_.addLog("Can't find Firefox history database", 1)

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

                    if self.report:
                        myReportPath = myPath + "/Reports/"
                        try:
                            os.makedirs(myReportPath)
                        except:
                            pass
                        if wifiDic != None:
                            self.getWifiReport(wifiDic, myReportPath)
                        self.getReport(userInfos, myReportPath)


