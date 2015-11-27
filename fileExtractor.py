#!/usr/bin/python
# Sample program or step 1 in becoming a DFIR Wizard!
# No license as this code is simple and free!
import sys
import pytsk3
import datetime
import os
from chromePass import GetChromePasswords
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
                            if done:
                                self.getChromeLogin(myPath, userDir,
                                                    filesystemObject)  # Try to get chrome passwords' database from each user (must have the masterkey for that user)
                                print "Done"

                            self.getChromeHistoryFile(myPath, userDir, filesystemObject)




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

                    # Resto de modulos de extraer datos aqui

                    else:
                        print "Unable to decrypt. Password required."

                    self.getChromeHistoryInfo(myPath)
                    self.getChromeDowloadInfo(myPath)

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
        except:
            print "[++++]Can't find chrome history[++++]"

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
                    history += 'URL = %s\n' % str(row[0])
                    history += 'URL Title = %s\n' % (row[1]).encode("utf-8")
                    history += 'Number of Visits = %s\n' % str(row[2])
                    history += 'Last Visit (UTC) = %s\n' % str(row[4])
                    history += 'First Visit (UTC) = %s\n' % str(row[5])
                    if (str(row[6]) == 'User typed the URL in the URL bar'):
                        history += 'Description = %s\n\n' % (str(row[6]))
                        history += 'Number of Times Typed = %s\n' % (str(row[3]))
                    else:
                        history += 'Description = %s\n\n' % (str(row[6]))
                except Exception, e:
                    print e
                    continue
            print history
            return history

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


    def getChromeDowloadInfo(self,myPath):
        """
            From https://github.com/OsandaMalith/ChromeFreak/blob/master/ChromeFreak.py CC license
        """
        downloads = ''
        try:
            sqlitePath = myPath + "/chrome/" + self.chromeHistoryFile
            connexion = sqlite3.connect(sqlitePath)
            c = connexion.cursor()
            c.execute("SELECT url, current_path, target_path,datetime((end_time/1000000)-11644473600,'unixepoch', 'localtime'),\
			 datetime((start_time/1000000)-11644473600,'unixepoch', 'localtime'),\
			 received_bytes, total_bytes FROM downloads,\
			 downloads_url_chains where downloads.id = downloads_url_chains.id")

            for row in c:
                try:
                    downloads += 'URL = %s\n' % str(row[0])
                    downloads += 'Current Path = %s\n' % str(row[1])
                    downloads += 'Target Path = %s\n' % str(row[2])
                    downloads += 'End Time = %s\n' % str(row[3])
                    downloads += 'Start Time = %s\n' % str(row[4])
                    if float(row[5]) < 1024:
                        downloads += 'Received Bytes = %.2f Bytes\n' % (float(row[5]))
                    if float(row[5]) > 1024 and float(row[5]) < 1048576:
                        downloads += 'Received Bytes = %.2f KB\n' % (float(row[5]) / 1024)
                    elif (float(row[5]) > 1048576 and float(row[5]) < 1073741824):
                        downloads += 'Received Bytes = %.2f MB\n' % (float(row[5]) / 1048576)
                    else:
                        downloads += 'Received Bytes = %.2f GB\n' % (float(row[5]) / 1073741824)

                    if (float(row[6]) < 1024):
                        downloads += 'Total Bytes = %.2f Bytes\n\n' % (float(row[6]))
                    if (float(row[6]) > 1024 and float(row[6]) < 1048576):
                        downloads += 'Total Bytes = %.2f KB\n\n' % (float(row[6]) / 1024)
                    elif (float(row[6]) > 1048576 and float(row[6]) < 1073741824):
                        downloads += 'Total Bytes = %.2f MB\n\n' % (float(row[6]) / 1048576)
                    else:
                        downloads += 'Total Bytes = %.2f GB\n\n' % (float(row[6]) / 1073741824)
                except UnicodeError:
                    continue
            print downloads
            return downloads
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
