#!/usr/bin/env python
# -*- coding: utf-8-*-
"""Author Drakosh <cpsoft@gmail.com>
 License GNU GPL v3 / Beerware """
import wikipedia, catlib
from Storage import Storage

class ReplicsCounter():
    def __init__(self):
        self.cache = Storage()
        self.cache.create("articles", \
                    {"oldid":"INT UNIQUE", "name":"TEXT", "ts":"DATE", "replics": "INT"})
    def countPage(self, page):
        """Counts repics at AFI page"""
        sections = {}
        sect = None
        n = -1 # one line for header
        for s in page.getSections():
            if sect != None:
                sections[sect] = (n, s[0])
            sect = s[3]
            n = s[0]
        sections[sect] = (n, len(page.get())) # last one
        
        for s in sections:
            replics = -1 # one for header
            text = page.get()[sections[s][0]:sections[s][1]].splitlines()
        
            for line in text:
                sline = line.strip()
                if (len(sline) > 2):
                    if sline[:2] != "{{" and sline[:-2] != "}}":
                        replics += 1
                        #print "%s %s" % (replics, line)
            wikipedia.output( u"%s %s %s" % (s, sections[s], replics))
            self.cache.execute(u'UPDATE articles SET replics = %s WHERE name = "%s";' % (replics, self.cache.quote(s)))
    def countCat(self, catname):
        cat = catlib.Category(wikipedia.getSite(), catname)
        for page in cat.articles():
            print page
            self.countPage(page)
    def replicsPage(self, pagename):
        r = self.cache.findone('articles', {"name":pagename}, what = ["replics"])
        if r == None:
            return "-"
        else:
            return r[0]
if __name__ == "__main__":
    counter = ReplicsCounter()
    counter.countCat(u"Категория:Википедия:Незакрытые обсуждения статей для улучшения")
    #counter.countPage(wikipedia.Page(wikipedia.getSite(), u"Википедия:К улучшению/5 августа 2013"))
    print counter.replicsPage(u"Килдерри")
    print counter.replicsPage(u"АМХ-40")
