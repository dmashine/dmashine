#!/usr/bin/env python
# -*- coding: utf-8-*-
""" Скрипт для обновления [[Википедия:Список Википедий в инкубаторе]]
Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware."""

import httplib, urllib, wikipedia, catlib, locale

class IncubatorException(Exception):
    pass

class WikiInfo:
    def __init__(self, cat):
        self.cat = cat
        self.localname= None
        if self.cat.titleWithoutNamespace()[:2] == u"Wp":
            self.lang = self.cat.titleWithoutNamespace()[3:].encode("utf-8")
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
        return "%s %s" % (self.lang, self.localname)
        #return self.lang + self.localname

if __name__ == "__main__":
    site = wikipedia.getSite('incubator', 'incubator')
    cat = catlib.Category(site, u"Category:Incubator:All_test_wikis")
    for c in cat.subcategories():
        try:
            i = WikiInfo(c)
            print i
        except IncubatorException:
            pass
