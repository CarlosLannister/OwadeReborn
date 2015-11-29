#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import os

__author__="ashe"
__date__ ="$Jul 6, 2011 5:50:34 PM$"

import tempfile
import subprocess
import re
import base64


from owade.models import *
from owade.process import Process


from owade.fileAnalyze.creddump.win32.hashdump import owade_get_hashes
from owade.fileAnalyze.creddump.win32.lsasecrets import get_file_secrets




class GetUserPassword:
    _striplen = 66
    def main(self, system, security, sam):
        users = owade_get_hashes(system, sam)
        ## clear passwords
        for u in users:
            users[u]['ntpass'] = None
            users[u]['lmpass'] = None

        ## First, output the LM & NT hashes into shadow files
        tempHash = tempfile.NamedTemporaryFile()
        tempHash.write("\n".join(["%s:%d:%s:%s" % (users[i]['name'].encode('utf-8'), users[i]['id'],
            users[i]['lmhash'], users[i]['nthash']) for i in users]))
        tempHash.flush()

        ## Try to crack LM hashes first
        subprocess.call(['./john', '--format=LM', '--single', tempHash.name], cwd=JOHN_DIR, stdout=None)
        subprocess.call(['./john', '--format=LM', '--rules', '--wordlist=password.lst', tempHash.name], stdout=None, cwd=JOHN_DIR)
        subprocess.call(['./john', '--format=LM', '--markov', tempHash.name], cwd=JOHN_DIR, stdout=None)

        ## Make a dictionnary out of cracked LM
        tempDict = tempfile.NamedTemporaryFile()
        process = subprocess.Popen(['./john', '--format=LM', '--show', tempHash.name], stdout=subprocess.PIPE, cwd=JOHN_DIR)
        output = process.communicate()[0]
        for line in output.split('\n'):
            match = re.search(r'^([^:]*):(.*)$', line)
            if match != None:
                tempDict.write("%s\n" % match.group(2)[:-self._striplen])
                if users.get(match.group(1)) != None:
                    users[match.group(1)]['lmpass'] = match.group(2)[:-self._striplen]
        tempDict.flush()

        ## Crack NT hash against computed dict
        subprocess.call(['./john', '--format=NT', '--wordlist=%s' % tempDict.name, '--rules=NT', tempHash.name], stdout=None, cwd=JOHN_DIR)

        tempDict.close()

        ## Crack remaining NT hashes
        subprocess.call(['./john', '--format=NT', '--single', tempHash.name], cwd=JOHN_DIR, stdout=None)
        subprocess.call(['./john', '--format=NT', '--rules', '--wordlist=password.lst', tempHash.name], cwd=JOHN_DIR, stdout=None)
        subprocess.call(['./john', '--format=NT', '--markov', tempHash.name], cwd=JOHN_DIR, stdout=None)

        process = subprocess.Popen(['./john', '--format=NT', '--show', tempHash.name], stdout=subprocess.PIPE, cwd=JOHN_DIR)
        output = process.communicate()[0]
        for line in output.split('\n'):
            match = re.search(r'^([^:]*):(.*)$', line)
            if match != None:
                if users.get(match.group(1)) != None:
                    users[match.group(1)]['ntpass'] = match.group(2)[:-self._striplen]

        tempHash.close()

        ## Append cracked password to password.lst :)
        dic = []
        f = open(os.path.join(JOHN_DIR, 'password.lst'), "a+")
        for u in users:
            if users[u]['ntpass'] != None:
                dic.append(users[u]['ntpass'])
            if users[u]['lmpass'] != None:
                if users[u]['lmpass'][:7] != '???????':
                    dic.append(users[u]['lmpass'][:7])
                if users[u]['lmpass'][7:] != '???????':
                    dic.append(users[u]['lmpass'][7:])
                if '???????' not in [users[u]['lmpass'][:7], users[u]['lmpass'][7:]]:
                    dic.append(users[u]['lmpass'])
        dic = set(dic)
        while True:
            l = f.readline()
            if l == '':
                break
            l = l.rstrip("\n")
            dic.discard(l)
        for l in dic:
            f.write("%s\n" % l)
        f.close()

        secrets = get_file_secrets(system, security)
        dpapi = ''
        if 'DPAPI_SYSTEM' in secrets:
            dpapi = secrets['DPAPI_SYSTEM']
            dpapi = base64.encodestring(dpapi)
        users['DPAPI_SYSTEM'] = dpapi

        return {self.__class__.__name__:users}


class UserPassword(Process):
    def __init__(self, internLog, terminalLog, hardDrive, overWrite):
        Process.__init__(self, internLog, terminalLog)
        self.hardDrive_ = hardDrive
        self.overWrite_ = overWrite

    def run(self):
        self.internLog_.addLog("UserPassword process launched", 1)
        for partition in Partition.objects.filter(harddrive=self.hardDrive_):
            mod = GetUserPassword()
            if not self.overWriteCategory(partition, mod.__class__.__name__, self.overWrite_):
                continue
            fileInfos = FileInfo.objects.filter(partition=partition)
            hives = self.getHives(fileInfos, ["system", "security", "sam"])
            if hives == None:
                continue
            self.internLog_.addLog("Getting DPAPI key for partition %s" % partition, 1)
            dic = mod.main(hives[0], hives[1], hives[2])
            self.updateDbGenericDic(dic, partition)

    hardDrive_ = None
    overWrite_ = None
