
import os
import exceptions
import sys
import subprocess

def checkConstant(dir, isdir=True):
    if isdir:
        if not os.path.isdir(dir):
            raise exceptions.IOError('Directory not found %s' % dir)
    else:
        if not os.path.isfile(dir):
            raise exceptions.IOError('File not found %s' % dir)

#################
### MAIN DIR
#################
##Project main directory
PROJECT_DIR = "/opt/"
PROJECT_NAME = "OwadeReborn/"
checkConstant(PROJECT_DIR + PROJECT_NAME)


TIMELINE_FILE = PROJECT_DIR + PROJECT_NAME + "templates/timeline.html"
HASHCAT_DIR = PROJECT_DIR + PROJECT_NAME + "owade/hashcatLib/hashcat"
#################
### DATABASE CONFIGURATION
#################
DATABASE_NAME='owade'
DATABASE_USER='postgres'
DATABASE_PASSWORD='postgres'
DATABASE_HOST='localhost'
DATABASE_PORT='5432'

#################
### STOCKAGE DIR (need a lot of disk space)
#################
##Where to stock disk image after ddrescue
              #/media/USERNAME/HDNAME/
#EXT_HDRIVE = subprocess.check_output("find /media -name storage", shell=True).rstrip()

EXT_HDRIVE = "/media/lannister/TOSHIBA EXT/storage"
#Aqui metodo post

IMAGE_DIR = EXT_HDRIVE + "/image"
IMAGE_FTP = EXT_HDRIVE + "/ftp"
checkConstant(IMAGE_DIR)
##Where to stock files
FILE_DIR = EXT_HDRIVE + "/file"
checkConstant(FILE_DIR)


#################
### DJANGO DIR (shouldn't be modified)
#################

##Where to find the template
TEMPLATE_DIR = PROJECT_DIR + "OwadeReborn/templates/"
checkConstant(TEMPLATE_DIR)

######################
#Forensic constants

# SAM
samPath = "/Windows/System32/config/SAM"

# SYSTEM
systemPath = "/Windows/System32/config/SYSTEM"

# SECURITY
securityPath = "/Windows/System32/config/SECURITY"

#System MasterKey
systemMasterKey = "/Windows/System32/Microsoft/Protect/S-1-5-18/User/"
mySystemMasterKey = "/systemMasterKey/"

# User Masterkey
protectDir = "/Appdata/Roaming/Microsoft/Protect/"
credhistFile = "CREDHIST"
NTUser = "NTUSER.DAT"

# Wifi
wifiDir = "/ProgramData/Microsoft/Wlansvc/"
myWifiProfile = "/wifi/"

# Chrome
chromeLoginFile = "Login Data"
chromeLogin = "/AppData/Local/Google/Chrome/User Data/Default/" + chromeLoginFile
chromeHistoryFile = "History"
chromeHistory = "/AppData/Local/Google/Chrome/User Data/Default/" + chromeHistoryFile

# Firefox
firefoxHistoryFile = "places.sqlite"
firefoxProfiles = "/AppData/Roaming/Mozilla/Firefox/Profiles/"

