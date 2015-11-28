
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

## This file is part of OWADE
##
## Author: Jean-Michel Picod <jean-michel.picod@cassidian.com>

__author__ = 'jm'
__date__ = '$Date$'

import mechanize,re, base64
from BeautifulSoup import BeautifulSoup

class GetLinkedinContent:
    _base = 'http://www.linkedin.com'

    def main(self, login, password):
        br = mechanize.Browser()
        br.open(self._base)
        br.select_form(name='login')
        br['session_key'] = login
        br['session_password'] = password
        br.submit()
        br.follow_link(url_regex=r'/profile/view\?id=')
        resp = br.follow_link(text='PDF')
        pdf = resp.read()
        br.back()
        br.follow_link(url_regex=r'/connections\?trk=')
        resp = br.follow_link(url_regex=r'/connectionsnojs\?trk=')
        pages = set(map(lambda x:'/'.join([self._base,x.url]),
            br.links(url_regex=r'connectionsnojs\?split_page=')))

        abook = {}
        i = 0
        while resp:
            soup = BeautifulSoup(resp.read())
            for contact in soup.findAll('tr', {'name':'connection'}):
                try:
                    c = {}
                    tmp = contact.find('a', {'name': 'fullProfile'})
                    c['name'] = tmp.text
                    c['url'] = '/'.join([self._base, tmp['href']])
                    c['headline'] = contact.find('td', {'name': 'headline'}).text
                    try:
                        c['id'] = re.findall(r'id=(\d+)', tmp['href'])[0]
                    except:
                        c['id'] = None
                    try:
                        c['vcard'] = br.open(contact.find('a', { 'name':
                            lambda(x): x[:12] == '_exportVCard'})['href']).read()
                        br.back()
                    except:
                        c['vcard'] = None
                    try:
                        soup2 = BeautifulSoup(br.open(tmp['href']).read())
                        img = base64.b64encode(br.open(soup2.find('img',
                            { 'class': 'photo' })['src']).read())
                        br.back()
                        br.back()
                        c['img'] = img
                    except:
                        c['img'] = None
                    i += 1
                    abook["contact%d" % i] = c
                except:
                    pass
            if len(pages) == 0:
                resp = None
            else:
                resp = br.open(pages.pop())

        return { self.__class__.__name__: { 'pdf': pdf, 'abook': abook } }

if __name__ == '__main__':
    import sys
    s = GetLinkedinContent()
    print s.main(sys.argv[1], sys.argv[2])

# vim:ts=4:expandtab:sw=4

