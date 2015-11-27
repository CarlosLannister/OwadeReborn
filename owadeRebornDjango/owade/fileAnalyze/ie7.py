
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

from DPAPI.Probes import IE7

from owade.tools.domainFormater import format

class GetIE7Passwords:

    _descr = "Decrypt Internet Explorer 7+ autocomplete passwords"

    ## autocomplete are stored under
    ## HKLM\\Software\\Microsoft\\Internet Explorer\\IntelliForms\\Storage2
    ##
    ## regkeys is a dict of reg entries such as the key is the hash value and
    ## the value is the DPAPI blob
    ##
    ## urls is an array of URLs that will be used to decipher password entries
    def main(self, regkeys, places, mkp, sid, h):
        values = {}

        urls = self.formatUrls(places)
    
        i = 0
        b = IE7.IE7Autocomplete()
        if b.try_decrypt_with_hash(h, mkp, sid, values=regkeys, urls=urls):
            for k in b.entries.keys():
                if b.entries[k].entropy is None:
                    continue
                e = b.entries[k]
                u = e.entropy.decode('UTF-16LE')[:-1]
                i += 1
                key = 'password%d' % i
                values[key] = {'login': e.login, 'password': e.password,
                    'origin':u, 'domain':format(u)}
                for j in range(len(e.other)):
                    values[key]["secret%d" % j] = e.other[j]

        return { self.__class__.__name__: values }

    def formatUrls(self, places):
        urls = []

        for place in places:
            url = places[place]['url']
            if url[:4] != 'http':
#                print 'not http', url
                continue
            url = url.split('?')[0]

            posible = []
            posible.append(url[:])
            posible.append(url[7:] if url[4] != 's' else url[8:])
            if url[4] != 's' and url[7:11] == 'www.':
                posible.append(url[11:])
            elif url[4] == 's' and url[8:12] == 'www.':
                posible.append(url[12:])
            if url[4] == 's':
                posible.append('http%s' % url[5:])

            for url in posible:
                pieces = url.split('/')
                size = len(pieces)
                for i in range(size):
                    if i < 2:
                        continue
                    url = ""
                    for j in range(i + 1):
                        url = "%s%s/" % (url, pieces[j])
                    urls.append(url[:-1])
                    urls.append(url)

        urls = list(set(urls))
#        print '########################################'
#        print 'URLS:'
#        print '########################################'
#        for url in urls:
#            print url
        return urls

# vim:ts=4:expandtab:sw=4
