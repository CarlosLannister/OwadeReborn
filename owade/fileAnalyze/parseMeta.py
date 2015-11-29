
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

import struct
import os, base64, tempfile
from M2Crypto import X509

#%appdata%\Microsoft\CryptnetUrlCache\Metadata et
#%WINDIR%\System32\config\SystemProfile\Application\Data\Microsoft\CryptnetUrlCache
#FIXME: Integration only made for the first one
class GetCryptnetCRL:
    def main(self, files):

        values = {}
        i = 0
        for f in files:
            fd = open(f["meta"])
            data = fd.read()
            fd.close()

            off = 0
            offset = struct.unpack_from("<L", data, off)[0]
            off += struct.calcsize("<L")
            offset += off

            struct.unpack_from("<2L", data, off)
            off += struct.calcsize("<2L")

            length = struct.unpack_from("<L", data, off)[0]
            off += struct.calcsize("<L")

            tstamp = struct.unpack_from("<Q", data, off)[0]
            off += struct.calcsize("<Q")

            url = data[offset:offset+length].decode("UTF-16LE")[:-1]

            if tstamp > 0:
                tstamp /= 10000000
                tstamp -= 11644473600

            ## dealing with CRL ASN.1 file now
            try:
                fd = open(f["content"])
                content = base64.b64encode(fd.read())
                fd.close()
                t = [ '-----BEGIN X509 CRL-----']
                while len(content) > 64:
                    t.append(content[:64])
                    content = content[64:]
                t.append(content)
                t.append('-----END X509 CRL-----')
                t.append('')
                fd = tempfile.NamedTemporaryFile(delete=False)
                fd.write("\n".join(t))
                fd.close()
                crl = X509.load_crl(fd.name)
                t = map(lambda x: x.strip(), crl.as_text().splitlines())
                serial = t[t.index('X509v3 CRL Number:') + 1]
                os.unlink(fd.name)
            except:
                serial = None
                crl = None
            i += 1
            values["url%d" % i] = { 'timestamp': tstamp, 'url': url }
#            if crl is not None:
#                values["url%d" % i]['crl'] = crl.as_text()
            if serial is not None:
                values["url%d" % i]['serial'] = serial
        return { self.__class__.__name__: values }

if __name__ == '__main__':
    import os, sys

    tmp = []
    d = sys.argv[1]
    for f in os.listdir(os.path.join(d, 'MetaData')):
        tmp.append(f)
    files = []
    for f in tmp:
        files.append({ 'content': os.path.join(d, 'Content', f),
            'meta': os.path.join(d, 'MetaData', f) })
    probe = GetCryptnetCRL()
    print probe.main(files)

# vim:ts=4:expandtab:sw=4

