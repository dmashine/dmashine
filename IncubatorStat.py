#!/usr/bin/env python
# -*- coding: utf-8-*-
""" Скрипт для обновления [[Википедия:Список Википедий в инкубаторе]]
Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware."""

import wikipedia, catlib

class IncubatorException(Exception):
    """just an exception"""
    pass

class WikiInfo:
    """Info about a wiki in incubator"""
    def __init__(self, cat):
        self.cat = cat
        self.articles = len(self.cat.articlesList(recurse = 3))
        self.pages = 0
        self.redir = 0
        self.users = 0
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

    def __repr__(self):
        return "Lang:%s\tLocalname:%s\tA:%s\tP:%s\tR:%s\tU:%s" % (self.lang, self.localname, self.articles, self.pages, self.redir, self.users)
        #return self.lang + self.localname

if __name__ == "__main__":
    f = open('/home/drakosh/IncubatorStat.txt', 'w+')    
    site = wikipedia.getSite('incubator', 'incubator')
    for c in catlib.Category(site, u"Category:Incubator:All_test_wikis").subcategories():
        try:
            i = WikiInfo(c)
            f.write("%s\r\n" % i)
            f.flush()
            print i
        except IncubatorException:
            pass
    f.close()
