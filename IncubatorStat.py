#!/usr/bin/env python
# -*- coding: utf-8-*-
""" Скрипт для обновления [[Википедия:Список Википедий в инкубаторе]]
Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware."""

import wikipedia, catlib, re
from httphelp import httphelp

class IncubatorException(Exception):
    """just an exception"""
    pass

class WikiInfo:
    """Info about a wiki in incubator"""
    def __init__(self, cat):
        self.cat = cat
        self.articles = 0# len(self.cat.articlesList(recurse = 3))
        self.pages = 0
        self.redir = 0
        self.editors = 0
        self.edits = 0
        self.littleedits = 0       
        
        if self.cat.titleWithoutNamespace()[:2] == u"Wp":
            self.lang = self.cat.titleWithoutNamespace()[3:].encode("utf-8")
            self.localname = self.lang
        else:
            raise IncubatorException
        for tl in self.cat.templatesWithParams():
            if tl[0] == u"Test language":
                #self.localname = tl
                for param in tl[1]:
                    if param.find(u"localname") > 0:
                        self.localname =  param[param.find(u"=")+1:].strip().encode("utf-8")
                        # i fucking LOVE unicode
                        break
        self.conn = httphelp()
        self.conn.server     = "toolserver.org"
        self.conn.scriptname = "/~pathoschild/catanalysis/index.php?title=Wp/%s&wiki=incubatorwiki_p&cat=0" % self.lang
        self.conn.parameters = {}
        self.conn.codepage = "utf-8"
        self.lines = self.conn.lines("GET")
        for l in self.lines:
            m = re.search(u'<li>(\d*) articles', l)
            if m != None:
                self.pages = m.group(1).encode("utf-8")
            m = re.search(u'<li>(\d*) editors', l)
            if m != None:
                self.editors= m.group(1).encode("utf-8")
            m = re.search(u'<li>(\d*) revisions', l)
            if m != None:
                self.edits= m.group(1).encode("utf-8")
            m = re.search(u'including (\d*) minor', l)
            if m != None:
                self.littleedits = m.group(1).encode("utf-8")
        
    def __repr__(self):
        return "Lang:%s\tLocalname:%s\tA:%s\tP:%s\tR:%s\tE:%s" % (self.lang, self.localname, self.articles, self.pages, self.redir, self.editors)
        #return self.lang + self.localname

if __name__ == "__main__":
    f = open('/home/drakosh/IncubatorStat.txt', 'w+')    
    site = wikipedia.getSite('incubator', 'incubator')
    for c in catlib.Category(site, u"Category:Incubator:All_test_wikis").subcategories():
        try:
            i = WikiInfo(c)
            print i
        except IncubatorException:
            pass
    f.close()
