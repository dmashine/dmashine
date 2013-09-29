#!/usr/bin/env python
# -*- coding: utf-8-*-
"""Author Drakosh <cpsoft@gmail.com>
 License GNU GPL v3 / Beerware """
import wikipedia, catlib
from Storage import Storage

class ReplicsCounter():
    def __init__(self):
        self.cache = Storage()
        self.cache.create("replics", {"name":"TEXT", "n":"INT"})
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
            # print u"%s %s %s" % (s, sections[s], replics)
            self.cache.delete('replics', {"name":s})
            self.cache.insert('replics', (s, replics))
    def countCat(self, catname):
        self.cache.delete('replics')
        cat = catlib.Category(wikipedia.getSite(), catname)
        for page in cat.articles():
            print page
            self.countPage(page)
    def replicsPage(self, pagename):
        r = self.cache.findone('replics', {"name":pagename})
        if r == None:
            return -1
        else:
            return r[1]
if __name__ == "__main__":
    counter = ReplicsCounter()
    counter.countCat(u"Категория:Википедия:Незакрытые обсуждения статей для улучшения")
    print counter.replicsPage(u"Килдерри")
    print counter.replicsPage(u"ыфукпук")
