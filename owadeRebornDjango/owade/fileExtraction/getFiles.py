from owade.constants import *
from owade.process import Process
import pytsk3
import os
import shutil
from subprocess import call
from stat import ST_SIZE
from owade.fileExtraction.foremost import Foremost
from owade.fileExtraction.mmls import Mmls
from owade.fileExtraction.hash import Hash
from owade.fileExtraction.mount import Mount
from owade.fileExtraction.umount import Umount
from owade.models import HardDrive, Partition, File, FileInfo
from owade.constants import *


class GetFiles(Process):
    def __init__(self, internLog, terminalLog, hardDrive, overWrite):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive = hardDrive
        self.overWrite = overWrite

    def getSAM(self, myPath, filesystemObject):  # Gets the SAM file
        self.internLog_.addLog("Getting SAM", 1)
        fileobject = filesystemObject.open(samPath)
        fullPath = myPath + "/SAM/"
        try:
            os.makedirs(fullPath)
        except:
            pass
        outfile = open(fullPath + "SAM", 'w')
        filedata = fileobject.read_random(0, fileobject.info.meta.size)
        outfile.write(filedata)
        outfile.close()

    def getSYSTEM(self, myPath, filesystemObject):  # Gets the SYSTEM file
        self.internLog_.addLog("Getting SYSTEM", 1)
        fileobject = filesystemObject.open(systemPath)
        fullPath = myPath + "/SYSTEM/"
        try:
            os.makedirs(fullPath)
        except:
            pass
        outfile = open(fullPath + "SYSTEM", 'w')
        filedata = fileobject.read_random(0, fileobject.info.meta.size)
        outfile.write(filedata)
        outfile.close()

    def getMasterKey(self, myPath, userDir,
                     filesystemObject):  # Tries to get the masterkey looking for the protect directory in each user folder
        self.internLog_.addLog("Getting masterkey", 1)
        protectPath = "/Users/" + userDir + protectDir
        try:
            self.get_All(protectPath, myPath, filesystemObject)  # Search recursive for the files
            self.internLog_.addLog("[++++]User: " + userDir + ", is  valid, masterkey obteined[++++]y", 1)
            return True  # It has found the file/s
        except:
            self.internLog_.addLog("[++++]User: " + userDir + ", is not valid, it doesn't have masterkey[++++]y", 1)
            try:
                os.removedirs(
                    myPath + protectPath)  # If user is not valid, we delete the directory in users folder (users like 'all users', 'default' should fail)
            except:
                pass
            return False

    def get_All(self, directory, myPath, filesystemObject):  # Get all files recursively from a given directory
        fullPath = myPath + directory
        try:
            os.makedirs(fullPath)  # Tries to create the subfolder for future saving
        except:
            pass
        directoryObject = filesystemObject.open_dir(directory)
        for entryObject in directoryObject:
            try:
                entryName = entryObject.info.name.name
                if entryName != '.' and entryName != '..':
                    ObjectName = directory + entryName
                    if entryObject.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                        self.get_All(ObjectName + "/", myPath, filesystemObject)
                    else:
                        fileobject = filesystemObject.open(ObjectName)
                        outfile = open(fullPath + entryName, 'w')
                        filedata = fileobject.read_random(0, fileobject.info.meta.size)
                        outfile.write(filedata)
                        outfile.close()
            except Exception, e:
                print e
                pass

    def getChromeLogin(self, myPath, userDir,
                       filesystemObject):  # Tries to get the chrome passwords' database looking for the chromeLogin file
        self.internLog_.addLog("Getting chrome passwords' database", 1)
        try:
            chromeUserLogin = "/Users/" + userDir + chromeLogin
            fileobject = filesystemObject.open(chromeUserLogin)
            myChromePath = myPath + "/Users/" + userDir + "/chrome/"
            try:
                os.makedirs(myChromePath)
            except:
                pass
            outfile = open(myChromePath + chromeLoginFile, 'w')
            filedata = fileobject.read_random(0, fileobject.info.meta.size)
            outfile.write(filedata)
            outfile.close()
        except:
            self.internLog_.addLog("[++++]Can't find chrome passwords database[++++]", 1)

    def getChromeHistoryFile(self, myPath, userDir, filesystemObject):
        self.internLog_.addLog("Getting chrome History", 1)
        try:
            chromeUserHistory = self.usersPath + userDir + self.chromeHistory
            fileobject = filesystemObject.open(chromeUserHistory)
            myChromePath = myPath + self.usersPath + userDir + "/chrome/"
            try:
                os.makedirs(myChromePath)
            except:
                pass
            outfile = open(myChromePath + self.chromeHistoryFile, 'w')
            filedata = fileobject.read_random(0, fileobject.info.meta.size)
            outfile.write(filedata)
            outfile.close()
        except:
            self.internLog_.addLog("[++++]Can't find chrome history[++++]", 1)

    def getFirefoxProfiles(self, myPath, userDir, filesystemObject):
        try:
            firefoxUserProfiles = self.usersPath + userDir + self.firefoxProfiles
            directoryObject = filesystemObject.open_dir(firefoxUserProfiles)
            myFirefoxPath = myPath + self.usersPath + userDir + "/firefox/"
            try:
                os.makedirs(myFirefoxPath)
            except:
                pass
            for folder in directoryObject:
                folderName = folder.info.name.name
                if folderName != '.' and folderName != '..':
                    firefoxProfileFolder = firefoxUserProfiles + folderName + "/"
                    myFirefoxProfilePath = myFirefoxPath + folderName + "/"
                    self.getFirefoxKeys(myFirefoxProfilePath, firefoxProfileFolder, filesystemObject)
                    self.getFirefoxHistory(myFirefoxProfilePath, firefoxProfileFolder, filesystemObject)
        except:
            self.internLog_.addLog("[++++]Can't find firefox profiles[++++]", 1)

    def getFirefoxKeys(self, myPath, userDir,
                       filesystemObject):  # Tries to get the firefox passwords' database looking for the chromeLogin file
        self.internLog_.addLog("Getting firefox passwords database", 1)
        try:
            firefoxUserKeys = userDir + self.firefoxKeysFile
            fileObject = filesystemObject.open(firefoxUserKeys)
            try:
                os.makedirs(myPath)
            except:
                pass
            outfile = open(myPath + self.firefoxKeysFile, 'w')
            filedata = fileObject.read_random(0, fileObject.info.meta.size)
            outfile.write(filedata)
            outfile.close()

        except:
            self.internLog_.addLog("[++++]Can't find firefox passwords' database[++++]", 1)

    def getFirefoxHistory(self, myPath, userDir,
                          filesystemObject):  # Tries to get the firefox history database looking for the chromeLogin file
        self.internLog_.addLog("Getting firefox history database", 1)
        try:
            firefoxUserHistory = userDir + self.firefoxHistoryFile
            fileobject = filesystemObject.open(firefoxUserHistory)
            try:
                os.makedirs(myPath)
            except:
                pass
            outfile = open(myPath + self.firefoxHistoryFile, 'w')
            filedata = fileobject.read_random(0, fileobject.info.meta.size)
            outfile.write(filedata)
            outfile.close()
        except:
            self.internLog_.addLog("[++++]Can't find firefox history database[++++]", 1)

    def run(self):  # Main function for extract the important files from the harddrive (only extract files from NTFS partitions)
        self.internLog_.addLog("ProgramAnalyze process launched", 1)
        print self.hardDrive.image_path()
        print self.hardDrive.log_path()
        imagehandle = pytsk3.Img_Info(self.hardDrive.image_path())
        partitionTable = pytsk3.Volume_Info(imagehandle)

        for partition in partitionTable:
            myPath = FILE_DIR + "/" + self.hardDrive.serial + "_" + str(partition.addr)  # Add partition to myPath
            myPath = str(myPath)
            if partition.desc == "NTFS (0x07)":
                print partition.addr, partition.desc, "%ss(%s)" % (
                    partition.start, partition.start * 512), partition.len
                filesystemObject = pytsk3.FS_Info(imagehandle, offset=partition.start * 512)  # Mount each partition
                try:
                    self.getSAM(myPath, filesystemObject)  # Gets the SAM file
                    self.getSYSTEM(myPath, filesystemObject)  # Gets the SYSTEM file
                    # Resto de modulos sin usuario
                    print "-", "USERS:"
                    directoryObject = filesystemObject.open_dir("/Users/")  # Open users directory
                    for entryObject in directoryObject:
                        userDir = entryObject.info.name.name
                        if userDir != '.' and userDir != '..':  # Quit . and .. directories
                            print "--", userDir
                            done = self.getMasterKey(myPath, userDir,
                                                     filesystemObject)  # Try to get masterkey from users
                            if done:  # We must have the masterkey for that user
                                self.getChromeLogin(myPath, userDir,
                                                    filesystemObject)  # Try to get chrome passwords' database from each user
                                self.getChromeHistoryFile(myPath, userDir,
                                                          filesystemObject)  # Try to get chrome hystory database from each user
                                self.getFirefoxProfiles(myPath, userDir,
                                                        filesystemObject)  # Try to get firefox profiles from each user (where passwords and history is stored)

                                # Resto de modulos de navegador
                                print "Done"
                except Exception as e:
                    print e
                    print "[++++]Partition has no user information[++++]"
