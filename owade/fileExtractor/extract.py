import pytsk3
import os
import shutil
from owade.constants import *
from owade.process import Process
import logging

class GetFiles(Process):

    def __init__(self, internLog, terminalLog, hardDrive, report, chromePassword,
                 chromeHistory, firefoxPassword, firefoxHistory, wifi, outlook):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive = hardDrive
        self.report = report
        self.chromePassword = chromePassword
        self.chromeHistory = chromeHistory
        self.firefoxPassword = firefoxPassword
        self.firefoxHistory = firefoxHistory
        self.wifi = wifi
        self.outlook = outlook

    def getSAM(self, savePath, filesystemObject):  # Gets the SAM file
        self.internLog_.addLog("Getting SAM", 1)
        print savePath
        fileobject = filesystemObject.open(samPath)
        fullPath = savePath + "/SAM/"
        try:
            os.makedirs(fullPath)
        except:
            print "Error trying create directory"
            pass
        outfile = open(fullPath + "SAM", 'w')
        filedata = fileobject.read_random(0, fileobject.info.meta.size)
        outfile.write(filedata)
        outfile.close()

    def getSYSTEM(self, savePath, filesystemObject):  # Gets the SYSTEM file
        self.internLog_.addLog("Getting SYSTEM", 1)
        fileobject = filesystemObject.open(systemPath)
        fullPath = savePath + "/SYSTEM/"
        try:
            os.makedirs(fullPath)
        except:
            print "Error trying create directory"
            pass
        outfile = open(fullPath + "SYSTEM", 'w')
        filedata = fileobject.read_random(0, fileobject.info.meta.size)
        outfile.write(filedata)
        outfile.close()

    def getSECURITY(self, savePath, filesystemObject):  # Gets the SYSTEM file
        print "Getting SECURITY"
        self.internLog_.addLog("Getting SECURITY", 1)
        fileobject = filesystemObject.open(securityPath)
        fullPath = savePath + "/SECURITY/"
        try:
            os.makedirs(fullPath)
        except:
            print "Error trying create directory"
            pass
        outfile = open(fullPath + "SECURITY", 'w')
        filedata = fileobject.read_random(0, fileobject.info.meta.size)
        outfile.write(filedata)
        outfile.close()


    def getSystemMasterKey(self,  savePath, filesystemObject):
        print "Getting system masterkey"
        self.internLog_.addLog("Getting system masterkey", 1)
        try:
            self.get_All(systemMasterKey, savePath + mySystemMasterKey, filesystemObject)  # Search recursive for the files
            return True  # It has found the file/s
        except:
            print "[++++]Can't have system masterKey[++++]"
            self.internLog_.addLog("[++++]Can't have system masterKey[++++]", 1)
            try:
                os.removedirs(
                    savePath + mySystemMasterKey)  # If user is not valid, we delete the directory in users folder (users like 'all users', 'default' should fail)
            except:
                pass
            return False


    def getWifiFiles(self,  savePath, filesystemObject):
        print "Getting wifi files"
        self.internLog_.addLog("Getting wifi files", 1)
        try:
            self.get_All(wifiDir, savePath + myWifiProfile, filesystemObject)  # Search recursive for the files
            return True  # It has found the file/s
        except:
            print "[++++]Can't have wifi files[++++]"
            self.internLog_.addLog("[++++]Can't have wifi files[++++]", 1)
            try:
                os.removedirs(
                    savePath + myWifiProfile)  # If user is not valid, we delete the directory in users folder (users like 'all users', 'default' should fail)
            except:
                pass
            return False

    def getMasterKey(self, savePath, userDir, filesystemObject):  # Tries to get the masterkey looking for the protect directory in each user folder
        print "Getting masterkey"
        self.internLog_.addLog("Getting masterkey", 1)
        protectPath = "/Users/" + userDir + protectDir
        try:
            self.get_All(protectPath, savePath + protectPath, filesystemObject)  # Search recursive for the files
            print "[++++]User: " + userDir + ", is  valid, masterkey obteined[++++]y"
            self.internLog_.addLog("[++++]User: " + userDir + ", is  valid, masterkey obteined[++++]y", 1)
            return True  # It has found the file/s
        except:
            print "[++++]User: " + userDir + ", is not valid, it doesn't have masterkey[++++]y"
            self.internLog_.addLog("[++++]User: " + userDir + ", is not valid, it doesn't have masterkey[++++]y" , 1)
            try:
                os.removedirs(
                    savePath + protectPath)  # If user is not valid, we delete the directory in users folder (users like 'all users', 'default' should fail)
            except:
                pass
            return False


    def get_All(self, path, savePath, filesystemObject):  # Get all files recursively from a given directory
        try:
            os.makedirs(savePath)  # Tries to create the subfolder for future saving
        except:
            pass
        directoryObject = filesystemObject.open_dir(path)
        for entryObject in directoryObject:
            try:
                entryName = entryObject.info.name.name
                if entryName != '.' and entryName != '..':
                    ObjectName = path + entryName
                    if entryObject.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:   #If directory
                        directory = ObjectName + "/"
                        myNewPath = savePath + entryName + "/"
                        self.get_All(directory, myNewPath, filesystemObject)
                    else:                                                           #If file
                        fileobject = filesystemObject.open(ObjectName)
                        outfile = open(savePath + "/" + entryName, 'w')
                        filedata = fileobject.read_random(0, fileobject.info.meta.size)
                        outfile.write(filedata)
                        outfile.close()
            except Exception, e:
                print e
                pass


    def getChromeLogin(self, savePath, userDir, filesystemObject):  # Tries to get the chrome passwords' database looking for the chromeLogin file
        print "Getting chrome passwords' database"
        self.internLog_.addLog("Getting chrome passwords' database", 1)
        try:
            chromeUserLogin = "/Users/" + userDir + chromeLogin
            fileobject = filesystemObject.open(chromeUserLogin)
            myChromePath = savePath + "/Users/" + userDir + "/chrome/"
            try:
                os.makedirs(myChromePath)
            except:
                pass
            outfile = open(myChromePath + chromeLoginFile, 'w')
            filedata = fileobject.read_random(0, fileobject.info.meta.size)
            outfile.write(filedata)
            outfile.close()
        except:
            print "[++++]Can't find chrome passwords database[++++]"
            self.internLog_.addLog("[++++]Can't find chrome passwords database[++++]", 1)

    def getChromeHistoryFile(self, savePath, userDir, filesystemObject):
        print "Getting chrome History"
        self.internLog_.addLog("Getting chrome History", 1)
        try:
            chromeUserHistory = "/Users/" + userDir + chromeHistory
            fileobject = filesystemObject.open(chromeUserHistory)
            myChromePath = savePath + "/Users/" + userDir + "/chrome/"
            try:
                os.makedirs(myChromePath)
            except:
                pass
            outfile = open(myChromePath + chromeHistoryFile, 'w')
            filedata = fileobject.read_random(0, fileobject.info.meta.size)
            outfile.write(filedata)
            outfile.close()
        except:
            self.internLog_.addLog("[++++]Can't find chrome history[++++]", 1)
            print "[++++]Can't find chrome history[++++]"

    def getFirefoxProfiles(self, savePath, userDir, filesystemObject):
        try:
            firefoxUserProfiles = "/Users/" + userDir + firefoxProfiles
            directoryObject = filesystemObject.open_dir(firefoxUserProfiles)
            myFirefoxPath = savePath + "/Users/" + userDir + "/firefox/"
            try:
                os.makedirs(myFirefoxPath)
            except:
                pass
            for folder in directoryObject:
                try:
                    folderName = folder.info.name.name
                    if folderName != '.' and folderName != '..':
                        firefoxProfileFolder = firefoxUserProfiles + folderName + "/"
                        myFirefoxProfilePath = myFirefoxPath + folderName + "/"
                        self.get_All(firefoxProfileFolder, myFirefoxProfilePath, filesystemObject)
                except:
                    self.internLog_.addLog("Error getting firefox files", 1)
                    print "Error getting firefox files"
        except:
            self.internLog_.addLog("[++++]Can't find firefox profiles[++++]", 1)
            print "[++++]Can't find firefox profiles[++++]"


    def getNTUser(self, savePath, userDir, filesystemObject):
        print "Getting NTUSER.dat for Outlook"
        self.internLog_.addLog("[++++]Getting NTUSER.dat for Outlook[++++]", 1)
        try:
            ntuserFile = "/Users/" + userDir + "/" + NTUser
            fileobject = filesystemObject.open(ntuserFile)
            myNTUserPath = savePath + "/Users/" + userDir + "/NTUSER/"
            try:
                os.makedirs(myNTUserPath)
            except:
                pass
            outfile = open(myNTUserPath + NTUser, 'w')
            filedata = fileobject.read_random(0, fileobject.info.meta.size)
            outfile.write(filedata)
            outfile.close()
        except:
            self.internLog_.addLog("[++++]Can't find NTUSER.dat[++++]", 1)
            print "[++++]Can't find NTUSER.dat[++++]"

    def run(self):

        image_path = self.hardDrive.image_path()

        #print self.hardDrive.image_path()
        #print self.hardDrive.log_path()

        imageName = image_path.split('/')
        imageName = imageName[-1]

        imagehandle = pytsk3.Img_Info(image_path)
        partitionTable = pytsk3.Volume_Info(imagehandle)



        for partition in partitionTable:
            savePath = FILE_DIR + "/" + self.hardDrive.serial + "_" + str(partition.addr)  # Add partition to myPath
            newPath = FILE_DIR + "/" + imageName + "_" + str(partition.addr)  # Add partition to myPath

            if partition.desc == "NTFS / exFAT (0x07)":
                print partition.addr, partition.desc, "%ss(%s)" % (
                    partition.start, partition.start * 512), partition.len

                filesystemObject = pytsk3.FS_Info(imagehandle, offset=partition.start * 512)  # Mount each partition

                try:
                    self.getSAM(newPath, filesystemObject)  # Gets the SAM file
                    self.getSYSTEM(newPath, filesystemObject)  # Gets the SYSTEM file
                    self.getSECURITY(newPath, filesystemObject)  # Gets the SECURITY file
                    self.getSystemMasterKey(newPath, filesystemObject)
                    self.getWifiFiles(newPath, filesystemObject)

                    print "-", "USERS:"
                    directoryObject = filesystemObject.open_dir("/Users/")  # Open users directory
                    for entryObject in directoryObject:
                        userDir = entryObject.info.name.name
                        if userDir != '.' and userDir != '..':  # Quit . and .. directories
                            print "--", userDir
                            done = self.getMasterKey(newPath, userDir, filesystemObject)  # Try to get masterkey from users

                            if done:  # We must have the masterkey for that user

                                #if self.outlook:
                                self.getNTUser(newPath, userDir, filesystemObject) # Try to get NTUSER.dat from each user for outlook

                                #if self.chromePassword:
                                self.getChromeLogin(newPath, userDir, filesystemObject)  # Try to get chrome passwords' database from each user

                                #if self.chromeHistory:
                                self.getChromeHistoryFile(newPath, userDir, filesystemObject)  # Try to get chrome hystory database from each user

                                #if self.firefoxHistory or self.firefoxPassword:
                                self.getFirefoxProfiles(newPath, userDir, filesystemObject)  # Try to get firefox profiles from each user (where passwords and history is stored)

                                # Resto de modulos de navegador
                    self.internLog_.addLog("[++++]Extract Files Finished[++++]", 1)
                except Exception as e:
                    print e
                    self.internLog_.addLog("[++++]Partition has no user information[++++]", 1)
                    print "[++++]Partition has no user information[++++]"