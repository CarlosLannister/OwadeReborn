
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
#!/usr/bin/env python

from DPAPI.Probes import wifi

class GetXPWifiNetworks:

    _descr = "Retreive and decrypt WiFi networks in registry"

    ## wireless keys are stored under
    ## HKLM\\Software\\Microsoft\\WZCSVC\\Parameters\\Interfaces\\[GUID]
    ## Each value beginning with "Static#" is a network
    ## This module requires first that the masterkeypool is filled with
    ## => system masterkeys (located under
    ##   \\Windows\\system32\\Microsoft\\Protect
    ##   and
    ##   \\Windows\\system32\\Microsoft\\Protect\\User
    ## => DPAPI_SYSTEM token which is a LSA secret
    ##
    ## regkeys is an array of all "Static#---" values
    def main(self, regkeys, mkp):
        values = {}

        i = 0
        for reg in regkeys:
            b = wifi.WirelessInfo(reg)
            if b.try_decrypt_system(mkp):
                i += 1
                values["wifi%d" % i] = {
                        'bssid': b.wifiStruct.bssid,
                        'ssid':  b.wifiStruct.ssid,
                        'hexkey': b.cleartext.encode('hex'),
                        'last': b.wifiStruct.timestamp,
                        'nettype':
                            b.wifiStruct._networktype[b.wifiStruct.nettype],
                        'channel':
                            b.wifiStruct._wifichans[b.wifiStruct.configuration[3]],
                        'mode':
                            b.wifiStruct._networkinfra[b.wifiStruct.infrastructuremode],
                        'authentication':
                            b.wifiStruct._authmode[b.wifiStruct.authmode]
                        }

        return { self.__class__.__name__: values }


# vim:ts=4:expandtab:sw=4
