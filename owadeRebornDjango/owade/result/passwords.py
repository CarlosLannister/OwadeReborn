
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
__date__ ="$Aug 2, 2011 4:09:16 PM$"

import re

from owade.process import Process
from owade.tools.sizeList import SizeList

class Passwords(Process):
    def __init__(self, internLog, terminalLog, partition):
        Process.__init__(self, internLog, terminalLog)
        self.partition_ = partition

    def credentials(self):
        credentials = []
        passwords = SizeList()
        users = SizeList()
        mails = SizeList()
        program = self.getDbGenericDic('ProgramAnalyze', self.partition_)
        for user in program:
            user = program[user]
            for creds in [('GetIE7Passwords', 'Internet Explorer'),
                ('GetFirefoxPasswords', 'Firefox'),
                ('GetChromePasswords', 'Chrome'),
                ('GetSafariPasswords', 'Safari'),
                ('GetTrillianAccounts', 'Trillian'),
                ('GetGTalkAccounts', 'GTalk')]:
                software = creds[1]
                creds = user.get(creds[0], {})
                for cred in creds:
                    cred = creds[cred]
                    if type(cred) is not dict:
                        continue
                    dic = {'password':cred['password'], 'login':cred['login'],
                        'domain':cred.get('domain', ''), 'software':software}
                    if not dic in credentials:
                        credentials.append(dic)
                    passwords.add(cred['password'])
                    login = cred['login']
                    users.add(login)
                    if isMail(login): mails.add(login)

            for forms in ['GetFirefoxHistory', 'GetChromeHistory']:
                forms = user.get(forms, {'forms':{}})
                forms = forms['forms']
                for form in forms:
                    form = forms[form]
                    value = form['value']
                    if form['fieldname'].lower() in ['username', 'user', 'login']:
                        users.add(value)
                    if isMail(value):
                        mails.add(value)

        self.credentials_ = credentials
        self.passwords_ = passwords.getList()
        self.users_ = users.getList()
        self.mails_ = mails.getList()

    def run(self):
        self.credentials()

    partition_ = None
    credentials_ = None
    passwords_ = None
    users_ = None
    mails_ = None

def isMail(value):
    if re.match(r'^[^@]+@[^.]+.[^.]{2,3}(.[^.]{2,3})?$', value):
        return True
    return False