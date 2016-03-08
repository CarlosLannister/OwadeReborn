#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2015, Francesco "dfirfpi" Picasso <francesco.picasso@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Windows system WiFi password offline and online decryptor."""

import optparse
import os
import re
import sys
from DPAPI.Core import blob
from DPAPI.Core import masterkey
from DPAPI.Core import registry


class GetWifiPassword:

    def getwifipassword(self, systemhive, securityhive, masterkeydir, profiledirectory):
        """
        getwifipassword returns all wifi passwords located at X:/ProgramData/Microsoft/Wlansvc
        """
        reg = registry.Regedit()
        secrets = reg.get_lsa_secrets(securityhive, systemhive)
        dpapi_system = secrets.get('DPAPI_SYSTEM')['CurrVal']

        mkp = masterkey.MasterKeyPool()
        mkp.loadDirectory(masterkeydir)
        mkp.addSystemCredential(dpapi_system)
        mkp.try_credential_hash(None, None)

        finalpass= dict()

        for root, _, files in os.walk(profiledirectory):
            for file in files:
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    file_data = f.read().replace('\x0a', '').replace('\x0d', '')
                    wifi_name = re.search('<name>([^<]+)</name>', file_data)
                    wifi_name = wifi_name.group(1)
                    key_material_re = re.search(
                        '<keyMaterial>([0-9A-F]+)</keyMaterial>', file_data)
                    if not key_material_re:
                        continue
                    key_material = key_material_re.group(1)
                    wblob = blob.DPAPIBlob(key_material.decode('hex'))
                    wifi_pwd = '<not decrypted>'
                    mks = mkp.getMasterKeys(wblob.mkguid)
                    for mk in mks:
                        if mk.decrypted:
                            wblob.decrypt(mk.get_key())
                            if wblob.decrypted:
                                wifi_pwd = wblob.cleartext
                            break
                    print 'Wifi:{} Password:{}'.format(wifi_name, wifi_pwd)
                    finalpass[wifi_name] = wifi_pwd
        print finalpass
        return finalpass

    def main(self, systemhive, securityhive, masterkeydir, profiledirectory):

        dic = self.getwifipassword(systemhive, securityhive, masterkeydir, profiledirectory)
        return dic