#!/usr/bin/env python
# -*- coding: utf-8-*-
# file with some stuff, sorry for style
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware
import httplib, urllib, wikipedia
class httphelp:
    """ Helper class to read lines with httplib"""
    def __init__(self):
        pass
    def lines(self):
        self.conn = httplib.HTTPConnection(self.server)
        p = urllib.urlencode(self.parameters)
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}

        self.conn.request("POST", self.scriptname, p, headers)
        response = self.conn.getresponse()
        #print response.status, response.reason
        return [l.decode(self.codepage, "ignore") for l in response.read().splitlines()]
    def __del__(self):
        self.conn.close()

def save(site, text="", pagename = None, filename = None, comment=None, minorEdit=True, botflag=True, dry=False):
# helper fun to save text to wiki
    page=wikipedia.Page(site, pagename)
    if not dry:
        try:
            page.put(text, comment, minorEdit=minorEdit, botflag=botflag)
        except wikipedia.LockedPage:
            wikipedia.output(u"Страница %s заблокирована; пропускаю." % page.title(asLink=True))
        except wikipedia.EditConflict:
            wikipedia.output(u'Пропускаю %s, конфликт правок'% (page.title()))
        except wikipedia.SpamfilterError, error:
            wikipedia.output(u'Пропущена страница %s, не пускает спамфильтр %s' % (page.title(), error.url))
    if filename <> None: # need to save locally
        f = open(filename, 'w+')
        f.write(text.encode('utf-8'))
        f.close()
    

