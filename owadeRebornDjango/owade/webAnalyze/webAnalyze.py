
#############################################################################
##                                                                         ##
## This file is part of Owade : www.owade.org                              ##
## Offline Windows Analyzer and Data Extractor                             ##
##                                                                         ##
##  Authors:                                                               ##
##  Elie Bursztein <owade@elie.im>                                         ##
##  Ivan Fontarensky <ivan.fontarensky@cassidian.com>                      ##
##  Matthieu Martin <matthieu.mar+owade@gmail.com>                         ##
##  Jean-Michel Picod <jean-michel.picod@cassidian.com>                    ##
##                                                                         ##
## This program is distributed under GPLv3 licence (see LICENCE.txt)       ##
##                                                                         ##
#############################################################################
__author__="ashe"
__date__ ="$Jul 28, 2011 4:24:15 PM$"

from owade.constants import FILE_DIR
from owade.process import Process
from owade.models import *
from owade.webAnalyze.spiderLinkedin import GetLinkedinContent
from owade.result.passwords import Passwords

class WebAnalyze(Process):
    def __init__(self, internLog, terminalLog, hardDrive, overWrite):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive_ = hardDrive
        self.overWrite_ = overWrite
        self.usernames_ = []
        self.mails_ = []
        self.passwords_ = []
        self.credentials_ = []

    #FIXME: Multiuser
    def linkedin(self):
        mod = GetLinkedinContent()
        infos = {}

        for mail in self.mails_:
            for password in self.passwords_:
                self.internLog_.addLog("Find prerequisite for Linkedin extraction", 1)
                try:
                    dic = mod.main(mail, password)
                except Exception as exp:
                    #print >>sys.stderr, exp.message
                    continue
                return dic
        return None

    def credentials(self, partition):
        passwords = Passwords(self.internLog_, self.terminalLog_, partition)
        passwords.start()
        passwords.join()
        self.credentials_ = passwords.credentials_
        self.passwords_ = passwords.passwords_
        self.users_ = passwords.users_
        self.mails_ = passwords.mails_


    def run(self):
        for partition in Partition.objects.filter(harddrive=self.hardDrive_):
            if not self.overWriteCategory(partition, self.__class__.__name__, self.overWrite_):
                continue
            self.credentials(partition)
            infos = {}

            dic = self.linkedin()
            if dic != None:
                pdf = dic['GetLinkedinContent']['pdf']
                #FIXME: Hard path
                path = '%s/linkedin.pdf' % FILE_DIR
                file = open(path, 'w')
                file.write(pdf)
                file.close()
                dic['GetLinkedinContent']['pdf'] = path
                infos.update(dic)

            self.updateDbGenericDic({self.__class__.__name__:infos}, partition)

    hardDrive_ = None
    overWrite_ = None

    users_ = None
    mails_ = None
    passwords_ = None
    credentials_ = None
