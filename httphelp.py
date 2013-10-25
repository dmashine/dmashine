#!/usr/bin/env python
# -*- coding: utf-8-*-
# file with some stuff, sorry for style
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware
import httplib, urllib, wikipedia

class HttpHelpException(Exception):
    """just exception"""
    pass

class httphelp:
    """ Helper class to read lines with httplib"""
    def __init__(self):
        pass
    def lines(self, method="POST"):
        """Connects to server, reads and returns lines"""
        self.conn = httplib.HTTPConnection(self.server)
        p = urllib.urlencode(self.parameters)        
        headers = {"Content-type": "application/x-www-form-urlencoded", \
                   "Accept": "text/plain"}

        self.conn.request(method, self.scriptname, p, headers)
        response = self.conn.getresponse()
        #print response.status, response.reason
        if response.status != 200:
            print response.status, response.reason
            raise HttpHelpException(u"Response status %s %s" % (response.status, response.reason))

        return [l.decode(self.codepage, "ignore") for l in response.read().splitlines()]
    def __del__(self):
        self.conn.close()

def save(site, text="", pagename = None, filename = None, comment=None, minoredit=True, botflag=True, dry=False):
    """ Helper fun to save text to wiki"""
    page = wikipedia.Page(site, pagename)
    #print filename
    #if (filename <> None) and (page.exists()): # need to save locally, do not overwrite
    if (filename != None): # need to save locally, do not overwrite
        f = open(filename, 'w+')
        f.write(text.encode('utf-8'))
        f.close()
        return
    if not dry:
        try:
            page.put(text, comment, minorEdit=minoredit, botflag=botflag)
        except wikipedia.LockedPage:
            wikipedia.output(u"Страница %s заблокирована; пропускаю." % page.title(asLink=True))
        except wikipedia.EditConflict:
            wikipedia.output(u'Пропускаю %s, конфликт правок'% (page.title()))
        except wikipedia.SpamfilterError, error:
            wikipedia.output(u'Пропущена страница %s, не пускает спамфильтр %s' % (page.title(), error.url))

    

