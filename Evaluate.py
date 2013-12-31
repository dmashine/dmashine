#!/usr/bin/env python
# -*- coding: utf-8-*-
"""Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware.
"""

import wikipedia, os, sys, time, math
from catlib import Category
from Storage import Storage
#from threading import Thread

class Evaluate():
    """Class to evaluate an article"""
    def __init__(self, pagename):
        #Thread.__init__(self)
        self.pagename = pagename
        site = wikipedia.getSite()
        self.page = wikipedia.Page(site, pagename)
    def eval(self):
        """Return quality of given article"""
        p = self.page
        templates = len(p.templatesWithParams())
        # remove good templates
        
        edits = len(p.getVersionHistory()) # до 10 - мало, до 100-норм, от 500- много
        l = len(p.get())                   # До 1к мало, до 2 к- норм, от 2 - много 
        cats = len(p.categories())         # 1-2 мало, 3-5 норм, больше 5 много
        linked = len(p.linkedPages())      # ??????
        referenced = len(list(p.getReferences())) # ????
        images =  len(p.imagelinks())      # 1-2 норм, 
        iwiki = len(p.interwiki())         # 1-5 мало 5-10 норм
        sections = len(p.getSections())    # 1-2 мало 3-4 норм
        users   = len(p.contributingUsers()) 
        return (self.pagename, templates, edits, l, cats, linked, referenced, images, iwiki, sections, users)
    def run(self):
        """Saves page to db"""
        db = Storage()
        db.execute("""CREATE TABLE IF NOT EXISTS quality
                    (name TEXT, templates INT, edits INT, len INT,
                    cats INT, linked INT, referenced INT, images INT,
                    iwiki INT, sections INT, users INT)""")
        db.delete("quality", {"name": self.pagename})
        db.insert("quality", self.eval())
        
class Corellations():
    """Рассчитать и распечатать статистические данные
    Количество статей
    Средние величины
    Корелляции
    see http://stackoverflow.com/questions/3949226/calculating-pearson-correlation-and-significance-in-python"""
    
    def average(self, x):
        assert len(x) > 0
        return float(sum(x)) / len(x)
    
    def sq_avg(self, x):
        s = 0
        for i in x:
            s+=i*i
        return math.sqrt((s/len(x)))
    
    def sq_dev(self, x):
        s = 0
        avg = self.average(x)
        for i in x:
            s += (i-avg)**2
        return math.sqrt((s/len(x)))
        
    def pearson_def(self, x, y):
        assert len(x) == len(y)
        n = len(x)
        assert n > 0
        avg_x = self.average(x)
        avg_y = self.average(y)
        diffprod = 0
        xdiff2 = 0
        ydiff2 = 0
        for idx in range(n):
            xdiff = x[idx] - avg_x
            ydiff = y[idx] - avg_y
            diffprod += xdiff * ydiff
            xdiff2 += xdiff * xdiff
            ydiff2 += ydiff * ydiff
        return diffprod / math.sqrt(xdiff2 * ydiff2)

    def __init__(self):
        """инициализируем и хреначим массив"""
        self.data = []
        for i in xrange(0, 12):
                self.data.append([])
        self.db = Storage()
        s = u"""SELECT name, templates, edits, len,
                    cats, linked, referenced, images,
                    iwiki, sections, users FROM quality ORDER BY name;"""
        re = self.db.execute(s)
        for l in re.fetchall():
            #print l[0]
            for i in xrange(1, 11):
                self.data[i].append(l[i])
    def print_stats(self):
        #print self.data
        stats =  u"Articles count %s \r\n" % len(self.data[1])
        val = ["", "templ", "edi", "len", "cat", "links", "refs", "img", "iwiki", "sect", "users"]



        stats += "          math avg     root mean      deviation        max    min \r\n"
        for i in xrange(1, 11):
            stats += "%8s: %-12.10g %-12.10g  %-12.10g %8g %6g \r\n"% (val[i], self.average(self.data[i]), self.sq_avg(self.data[i]), self.sq_dev(self.data[i]), max(self.data[i]), min(self.data[i]))
        r = ""
        stats += "\r\n"
        stats += "Corellations table \r\n"
        for v in val:
            r += "%10s"%(v)
        stats += r+"\r\n"
        r = ""
        p = {}
        for i in xrange(1, 11):
            for j in xrange(1, 11):
                d = self.pearson_def(self.data[i], self.data[j])
                r+="%-10.4g " % d
                if i > j:
                    p["%s-%s"%(val[i], val[j])] = d
            stats += "%8s %s\r\n"%(val[i], r)
            r=""
        stats += "\r\n"
        stats += " Maximum values           | Minimum values \r\n"
        up = sorted(p.items(), key=lambda x: -abs(x[1]))
        #print up[0]
        for l in xrange(0, 12):
            stats += "%12s %6.12s | %12s %6.12s \r\n" % (up[l][0], up[l][1], up[-l-1][0], up[-l-1][1])
        return stats
    def print_sel(self):
        """Распечатываем максимальные и минимальные статьи"""
       
        k = (1000, 1000, 1, 1000, 1000, 1000, 1000, 1000, 1000, 1000)

        s = """SELECT name, ((templates * %s) + (edits * %s) + (len * %s) +
               (cats * %s) + (linked * %s) + (referenced * %s) + (images * %s) +
               (iwiki * %s) + (sections * %s) + (users * %s)) AS value FROM quality ORDER BY value ASC LIMIT 10;""" % k
        re = self.db.execute(s)
        for l in re.fetchall():
            print "%s %s" % l
        
        print "------------"
        
        s = """SELECT name, ((templates * %s) + (edits * %s) + (len * %s) +
               (cats * %s) + (linked * %s) + (referenced * %s) + (images * %s) +
               (iwiki * %s) + (sections * %s) + (users * %s)) AS value FROM quality ORDER BY value DESC LIMIT 10;""" % k
        re = self.db.execute(s)
        for l in re.fetchall():
            print "%s %s" % l

if __name__ == "__main__":
    #Corellations().print_sel()
    #sys.exit()
    if len(sys.argv) >= 2:
        if sys.argv[1] == "stats":
            while True:
                p = Corellations().print_stats()
                os.system('clear')
                print p
                time.sleep(10)
        else:
            while True:
                os.system('clear')
                Corellations().print_sel()
                time.sleep(10)

    else:
        site = wikipedia.getSite()
        cat = Category(site, u"Категория:Музыка")
        x=0
        #while True:
        for p in cat.articles(recurse=3):
        #    p = site.randompage()
            if (p.namespace() == 0) and (not p.isDisambig()) and (not p.isRedirectPage()):
                Evaluate(p.title()).run()
                x += 1
                print x
                #if x == 10:
                #    time.sleep(10)
                #    x = 0


# SELECT name, len from quality where (len < (select avg(len) from quality) / 4 and cats < (select avg(len) from quality) / 4) order by len;
