#!/usr/bin/python
# Sample program or step 1 in becoming a DFIR Wizard!
# No license as this code is simple and free!
import sys
import pytsk3
import datetime
import os
from chromePass import GetChromePasswords
from firefoxHistory import firefox_decrypt
import re
import hashlib
from DPAPI.Core import masterkey
import sqlite3
import json


class Paths:
    ntfs = "NTFS (0x07)"
    usersPath = "/Users/"

    # Storage
    myHD = "/media/lannister/TOSHIBA EXT/storage"
    myImagePath = myHD + "/image/"
    myFilesPath = myHD + "/new_files/"

    # Masterkey
    protectDir = "/Appdata/Roaming/Microsoft/Protect/"

    # SAM
    samPath = "/Windows/System32/config/SAM"

    # SYSTEM
    systemPath = "/Windows/System32/config/SYSTEM"

    # Chrome
    chromeLoginFile = "Login Data"
    chromeHistoryFile = "History"
    chromeLogin = "/AppData/Local/Google/Chrome/User Data/Default/" + chromeLoginFile
    chromeHistory = "/AppData/Local/Google/Chrome/User Data/Default/" + chromeHistoryFile

    # Firefox
    firefoxKeysFile = "key3.db"
    firefoxHistoryFile = "places.sqlite"
    firefoxProfiles = "/AppData/Roaming/Mozilla/Firefox/Profiles/"


class Extrator(Paths):
    def __init__(self, harddrive, password=None):  # Each Object Extractor has its own harddrive
        self.harddrive = harddrive
        self.password = password

    def extractFiles(
            self):  # Main function for extract the important files from the harddrive (only extract files from NTFS partitions)
        imagefile = self.myImagePath + self.harddrive

        imagehandle = pytsk3.Img_Info(imagefile)
        partitionTable = pytsk3.Volume_Info(imagehandle)

        for partition in partitionTable:
            myPath = self.myFilesPath + self.harddrive + "_" + str(partition.addr)  # Add partition to myPath
            if partition.desc == self.ntfs:
                print partition.addr, partition.desc, "%ss(%s)" % (
                    partition.start, partition.start * 512), partition.len
                filesystemObject = pytsk3.FS_Info(imagehandle, offset=partition.start * 512)  # Mount each partition
                try:
                    self.getSAM(myPath, filesystemObject)  # Gets the SAM file
                    self.getSYSTEM(myPath, filesystemObject)  # Gets the SYSTEM file
                    # Resto de modulos sin usuario
                    print "-", "USERS:"
                    directoryObject = filesystemObject.open_dir(self.usersPath)  # Open users directory
                    for entryObject in directoryObject:
                        userDir = entryObject.info.name.name
                        if userDir != '.' and userDir != '..':  # Quit . and .. directories
                            print "--", userDir
                            done = self.getMasterKey(myPath, userDir,
                                                     filesystemObject)  # Try to get masterkey from users
                            if done:	#We must have the masterkey for that user
                                self.getChromeLogin(myPath, userDir,filesystemObject)  # Try to get chrome passwords' database from each user 
                                self.getChromeHistoryFile(myPath, userDir, filesystemObject)  # Try to get chrome hystory database from each user
                                self.getFirefoxProfiles(myPath, userDir,filesystemObject)   # Try to get firefox profiles from each user (where passwords and history is stored)

                                    # Resto de modulos de navegador
                                print "Done"
                except:
                    print "[++++]Partition has no user information[++++]"

    def extractData(self):
        print "\n\nGetting data from extracted files"
        folders = os.listdir(self.myFilesPath)
        for folder in folders:
            if self.harddrive in folder:  # check if harddrive is in the folder's name
                sam = self.myFilesPath + folder + "/SAM/SAM"  # Here is the SAM
                system = self.myFilesPath + folder + "/SYSTEM/SYSTEM"  # Here is the SYSTEM

                partitionPath = self.myFilesPath + folder + self.usersPath
                users = os.listdir(partitionPath)
                try:
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
	                    # Here try to crack password if not given
	                    if self.password != None:
	                        self.getChromePass(myPath, mkpDir, sid, self.password)
	                    else:
	                        print "Unable to decrypt. Password required."

	                    self.getFirefoxData(myPath)
	                    # Resto de modulos de extraer datos aqui

	                    self.getChromeHistoryInfo(myPath)
	                    self.getChromeDowloadInfo(myPath)
                except:
                    pass

    def getFirefoxData(self, myPath):
        fire = firefox_decrypt()
        myFirefoxPath = myPath + "/firefox/"
        profiles = os.listdir(myFirefoxPath)
        for profile in profiles:
            myFirefoxHistoryPath = myFirefoxPath + profile + "/" + self.firefoxHistoryFile
            print fire.getHistory(myFirefoxHistoryPath)
            print fire.getDownloads(myFirefoxHistoryPath)


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

    def getSAM(self, myPath, filesystemObject):  # Gets the SAM file
        print "-", "Getting SAM"
        fileobject = filesystemObject.open(self.samPath)
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
        print "-", "Getting SYSTEM"
        fileobject = filesystemObject.open(self.systemPath)
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
        print "----", "Getting masterkey"
        protectPath = self.usersPath + userDir + self.protectDir
        try:
            self.get_All(protectPath, myPath, filesystemObject)  # Search recursive for the files
            return True  # It has found the file/s
        except:
            print "[++++]User is not valid, it doesn't have masterkey[++++]"
            try:
                os.removedirs(
                    myPath + protectPath)  # If user is not valid, we delete the directory in users folder (users like 'all users', 'default' should fail)
            except:
                pass
            return False

    def getChromeLogin(self, myPath, userDir,
                       filesystemObject):  # Tries to get the chrome passwords' database looking for the chromeLogin file
        print "----", "Getting chrome passwords' database"
        try:
            chromeUserLogin = self.usersPath + userDir + self.chromeLogin
            fileobject = filesystemObject.open(chromeUserLogin)
            myChromePath = myPath + self.usersPath + userDir + "/chrome/"
            try:
                os.makedirs(myChromePath)
            except:
                pass
            outfile = open(myChromePath + self.chromeLoginFile, 'w')
            filedata = fileobject.read_random(0, fileobject.info.meta.size)
            outfile.write(filedata)
            outfile.close()
        except:
            print "[++++]Can't find chrome passwords database[++++]"

    def getChromeHistoryFile(self, myPath, userDir, filesystemObject):
        print "----", "Getting chrome History"
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
            print "[++++]Can't find chrome history[++++]"

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
            print "[++++]Can't find firefox profiles[++++]"

    def getFirefoxKeys(self, myPath, userDir, filesystemObject):  # Tries to get the firefox passwords' database looking for the chromeLogin file
        print "----", "Getting firefox passwords database"
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
            print "[++++]Can't find firefox passwords' database[++++]"

    def getFirefoxHistory(self, myPath, userDir, filesystemObject):   # Tries to get the firefox history database looking for the chromeLogin file
        print "----", "Getting firefox history database"
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
            print "[++++]Can't find firefox history database[++++]"

    def getChromePass(self, myPath, mkpDir, sid, password):
        print "--", "Getting chrome passwords"
        try:
            database = []
            database.append(myPath + "/chrome/" + self.chromeLoginFile)

            mkp = masterkey.MasterKeyPool()
            mkp.loadDirectory(mkpDir)

            passHash = hashlib.sha1(password.encode("UTF-16LE")).hexdigest().decode('hex')

            chromePassExtractor = GetChromePasswords()
            pwords = chromePassExtractor.main(database, mkp, sid, passHash)
            print pwords
        except Exception, e:
            print e
            pass

    def getChromeHistoryInfo(self, myPath):
        """
            From https://github.com/OsandaMalith/ChromeFreak/blob/master/ChromeFreak.py CC license
        """

        history = ''
        historyValues = {}
        try:
            sqlitePath = myPath + "/chrome/" + self.chromeHistoryFile
            connexion = sqlite3.connect(sqlitePath)
            c = connexion.cursor()
            c.execute("SELECT urls.url, urls.title, urls.visit_count,urls.typed_count, \
			    datetime((urls.last_visit_time/1000000)-11644473600,'unixepoch', 'localtime'),\
			    datetime((visits.visit_time/1000000)-11644473600,'unixepoch', 'localtime'), \
			    CASE (visits.transition & 255)\
			    WHEN 0 THEN 'User clicked a link'\
			    WHEN 1 THEN 'User typed the URL in the URL bar'\
			    WHEN 2 THEN 'Got through a suggestion in the UI'\
			    WHEN 3 THEN 'Content automatically loaded in a non-toplevel frame - user may not realize'\
			    WHEN 4 THEN 'Subframe explicitly requested by the user'\
			    WHEN 5 THEN 'User typed in the URL bar and selected an entry from the list - such as a search bar'\
			    WHEN 6 THEN 'The start page of the browser'\
			    WHEN 7 THEN 'A form the user has submitted values to'\
			    WHEN 8 THEN 'The user reloaded the page, eg by hitting the reload button or restored a session'\
			    WHEN 9 THEN 'URL what was generated from a replacable keyword other than the default search provider'\
			    WHEN 10 THEN 'Corresponds to a visit generated from a KEYWORD'\
			    END AS Description\
			    FROM urls, visits WHERE urls.id = visits.url")

            for row in c:
                try:
                    historyValues['URL %s' % row[0]] = {'title':row[1].encode("utf-8"), 'visitNumber':str(row[2]),
                    'lastVisit':str(row[4]), 'firstVisit':str(row[5])}
                except Exception, e:
                    print e
                    continue
            
            print historyValues
            return historyValues

        except sqlite3.OperationalError, e:
            e = str(e)
            if e == 'database is locked':
                print '[!] Make sure Google Chrome is not running in the background'
            elif e == 'no such table: urls':
                print '[!] Something wrong with the database name'
            elif e == 'unable to open database file':
                print '[!] Something wrong with the database path'
            else:
                print e


    def getChromeDowloadInfo(self, myPath):
        """
            From https://github.com/OsandaMalith/ChromeFreak/blob/master/ChromeFreak.py CC license
        """
        downloadValues = {}
        try:
            sqlitePath = myPath + "/chrome/" + self.chromeHistoryFile
            connexion = sqlite3.connect(sqlitePath)
            c = connexion.cursor()
            c.execute("SELECT url, current_path, target_path,datetime((end_time/1000000)-11644473600,'unixepoch', 'localtime'),\
			 datetime((start_time/1000000)-11644473600,'unixepoch', 'localtime'),\
			 received_bytes, total_bytes FROM downloads,\
			 downloads_url_chains WHERE downloads.id = downloads_url_chains.id")

            for row in c:
                receivedBytes = ''
                try:
                    #"%.2f" % receivedBytes
                    receivedBytes = "%.2f Bytes" % float(row[5])
                    #if receivedBytes < 1024:
                    #downloads += 'Received Bytes = %.2f Bytes\n' % (float(row[5]))
                    if float(row[5]) > 1024 and float(row[5]) < 1048576:
                        receivedBytes = "%.2f KB" % (float(row[5]) / 1024)
                    elif (float(row[5]) > 1048576 and float(row[5]) < 1073741824):
                        receivedBytes = "%.2f MB" % (float(row[5]) / 1048576)
                    else:
                        receivedBytes = "%.2f GB" % (float(row[5]) / 1073741824)

                    downloadValues['URL %s' % row[0]] = {'currentPath':str(row[1]), 'targetPath':str(row[2]),
                    'endTime':str(row[4]), 'startTime':str(row[5]), 'receivedBytes':str(receivedBytes)}

                except UnicodeError:
                    continue

            print downloadValues
            return downloadValues

        except sqlite3.OperationalError, e:
            e = str(e)
            if e == 'database is locked':
                print '[!] Make sure Google Chrome is not running in the background'
            elif e == 'no such table: downloads':
                print '[!] Something wrong with the database name'
            elif e == 'unable to open database file':
                print '[!] Something wrong with the database path'
            else:
                print e

harddrive = "777666AA_image"
ex = Extrator(harddrive, "lazarus2015")
ex.extractFiles()
ex.extractData()
