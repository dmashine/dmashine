#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Скрипт для обновления [[Википедия:Список Википедий в инкубаторе]]
Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware."""

import wikipedia, catlib, re
from httphelp import httphelp, save

class IncubatorException(Exception):
    """just an exception"""
    pass

class WikiInfo:
    """Info about a wiki in incubator"""
    def __init__(self, cat):
        self.cat = cat
        self.articles = u"-"
        self.pages = u"-"
        self.redir = u"-"
        self.editors = u"-"
        self.edits = u"-"
        self.littleedits = u"-"
        
        if self.cat.titleWithoutNamespace()[:2] == u"Wp":
            self.lang = self.cat.titleWithoutNamespace()[3:].encode("utf-8")
            self.localname = self.lang
            self.rusname = u"---"
        else:
            raise IncubatorException
        for tl in self.cat.templatesWithParams():
            if tl[0] == u"Test language":
                #self.localname = tl
                for param in tl[1]:
                    if param.find(u"localname") > 0:
                        self.localname =  param[param.find(u"=")+1:].strip()
                        break
        self.conn = httphelp()
        self.conn.server     = "toolserver.org"
        self.conn.scriptname = "/~pathoschild/catanalysis/index.php?title=Wp/%s&wiki=incubatorwiki_p&cat=0" % self.lang
        self.conn.parameters = {}
        self.conn.codepage = "utf-8"
        self.lines = self.conn.lines("GET")
        for l in self.lines:
            # i fucking LOVE unicode
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
                self.littleedits= m.group(1).encode("utf-8")
        
    def __repr__(self):
        return u"|%s||%s||%s||%s||%s||%s||%s||%s||%s||%s" % (0, 0, 0, 0, self.articles, self.pages, self.redir, self.editors, self.edits, self.littleedits)
        #return self.lang + self.localname

if __name__ == "__main__": 
    site = wikipedia.getSite('incubator', 'incubator')
    text = u"""== Разделы Википедии в инкубаторе ==
{| border="1" cellpadding="2" cellspacing="0" style="background: #ffffff; border: 1px solid #777777; border-collapse: collapse; white-space: nowrap; text-align: right" class="sortable plainlinksneverexpand"
! style="background:#dde2e2; text-align: center" |{{comment|№|Порядковый номер раздела (по количеству статей)}}
! style="background:#dde2e0; text-align: center" |Код
! style="background:#dde2e2; text-align: center" |Язык
! style="background:#dde2e2; text-align: center" |Самоназвание
! style="background:#dde2e2; text-align: center" |Статей
! style="background:#dde2e2; text-align: center" |{{comment|Стр.|Число страниц}}
! style="background:#dde2e2; text-align: center" |{{comment|Редир.|Число перенаправлений}}
! style="background:#dde2e2; text-align: center" |{{comment|Участн.|Число участников}}
! style="background:#dde2e2; text-align: center" |{{comment|Правок|Число правок, в том числе малых}}
! style="background:#dde2e2; text-align: center" |{{comment|Малых|Число малых правок}}\r\n""".encode("utf-8")
    for c in catlib.Category(site, u"Category:Incubator:All_test_wikis").subcategories():
        try:
            i = WikiInfo(c)
            text += (u"|-\r\n%s\r\n" % i).encode("utf-8")
        except IncubatorException:
            pass
    text += u"|}".encode("utf-8")
    print text
    save(wikipedia.getSite(), text=text, pagename=u"Википедия:Список Википедий в инкубаторе/Тест", comment=u"Список Википедий в инкубаторе")
