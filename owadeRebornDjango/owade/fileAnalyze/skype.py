
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

from DPAPI.Probes import skype

class GetSkypeAccounts:

    _descr = "Decrypt Skype account password"

    ## login = skype login
    ## regtoken = registry value located @ HKCU\Software\Skype\ProtectedStorage\0
    ##
    ## xmlfile = config.xml file located @ %APPDATA%\Skype\[login]\config.xml
    ##
    ## Note that the DPAPI Probe is also able to be given directly the content
    ## of the xml file. To do so, change the parameter 'xmlfile' to 'xml' if the
    ## call of try_decrypt_with_hash()
    def main(self, accounts, regtoken, mkp, sid, h):
        values = {}
        i = 0
        #b = skype.SkypeAccount(regtoken)

        for account in accounts:
            login = account
            xmlfile=accounts[account]
            b = skype.SkypeAccount(regtoken)
            if b.try_decrypt_with_hash(h, mkp, sid, login=login, xmlfile=xmlfile):
                i += 1
                values['user%d' % i] = { 'login': login, 'hash': b.cleartext[:32],
                        'shadow': b.jtr_shadow(), 'data': b.cleartext }

        return { self.__class__.__name__: values }

if __name__ == '__main__':
    import sys, os, hashlib
    from DPAPI.Core import *

    base = os.path.join('', 'skype')
    sid = 'S-1-5-21-1275210071-602609370-1801674531-1003'
    password = ''

    account='project.owade'
    skypepwd='rootroot1'
    regkey="01000000d08c9ddf0115d1118c7a00c04fc297eb0100000022b4f0b2fac7c24d8b84c7e2794ce4c00000000002000000000003660000a80000001000000003948c08395431dc06177f2602c468b20000000004800000a000000010000000baa9484d86be95063509e6d47b99a4d820000000deb1931246e8718bbf9624e63fc8c6449dd55553b3c57a5de05fc085cbf426c1140000009f790b00c87d33ef4fee7b8c53781e79eb7f3bc8".decode('hex')

    mkp = masterkey.MasterKeyPool()
    mkp.loadDirectory(os.path.join(base, sid))
    #mkp.addCredhistFile(sid, os.path.join(base, 'CREDHIST'))

    skypehash = hashlib.md5(account+"\nskyper\n"+skypepwd).hexdigest()

    p = GetSkypePassword()
    rv = p.main(account, regkey, os.path.join(base,account,'config.xml'), mkp,
            sid, hashlib.sha1(password.encode("UTF-16LE")).digest())
    assert rv['GetSkypePassword'][account]['shadow'] == (account + ":md5_gen(1401)" + skypehash)
    print "OK"


# vim:ts=4:expandtab:sw=4
