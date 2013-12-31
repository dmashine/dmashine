#!/usr/bin/env python
# -*- coding: utf-8-*-
""" Скрипт разделяет статьи, предложенные к улучшению в ru.wikipedia
по тематическим страницам.
Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware.
Для длинных списков:
        <div style="height:200px; overflow:auto; padding:3px"></div>"""

import traceback, sys, locale
import wikipedia
import httphelp
from Storage import Storage
from AllAFI import AllAFI, TemplateRandom
from ReplicsCounter import ReplicsCounter
from threading import Thread
from datetime import datetime, date
from CategoryIntersect import CategoryIntersect#, \
                              #CategoryIntersectException

MONTHS = [u'января', u'февраля', u'марта',  \
          u'апреля', u'мая',     u'июня',   \
          u'июля', u'августа', u'сентября', \
          u'октября', u'ноября', u'декабря' ]

D = {-1: '', 90:'class="highlight"|', 180: 'class="bright"|'}

class CleanupTematic(Thread):
    """One thread of bot that cleans one theme"""
    def __init__(self, pagename, catname):
        Thread.__init__(self)
        self.pagename = pagename
        self.catname = catname
        self.text = ''
        self.cache = Storage()
        self.cache.create("updates", {"topic":"TEXT", "ts":"DATE", "n":"INT"})
        self.cache.create("articles", \
                    {"oldid":"INT UNIQUE", "name":"TEXT", "ts":"DATE", "replics": "INT"})

    def save(self, minoredit=True, botflag=True, dry=False):
        """Saves data to wikipedia page"""
        httphelp.save(SITE, text = self.text,
            pagename = u"Википедия:К улучшению/Тематические обсуждения/"+self.pagename, \
            comment  = u"Статьи для срочного улучшения (3.3) тематики "\
                + self.pagename, minoredit=minoredit, botflag=botflag, dry=dry)
  
    def addline(self, article):
        """Gets article name. Adds to self.text one line of table. """

        p = wikipedia.Page(SITE, article)
        
        title = p.titleWithoutNamespace()
        parm = ''
        for tl in p.templatesWithParams():
            if tl[0] == u'К улучшению':
                try:
                    parm = tl[1][0].split('-')
                    ts1 = date(int(parm[0]), int(parm[1]), int(parm[2]))
                except (IndexError, UnicodeEncodeError, ValueError), e:
                    wikipedia.output(u"Ошибка в дате статьи %s:%s"%(article, e))
                    self.text += u'|class="shadow"|[[%s]]||colspan="3"|Некорректные параметры шаблона КУЛ\n|-\n' % (article)
                    return # afi date not found
                break
        if parm == '':
            self.text += u'|class="shadow"|[[%s]]||colspan="3"|Не обнаружен шаблон КУЛ\n|-\n' % (article)
            wikipedia.output(u"Статья %s без шаблона! " % (article))
            # what a mess, has a category, and no template
            return
        try:
            hist = p.fullVersionHistory(False, False, True)
            edits = len(hist) #number of edits made
        except wikipedia.Error, e:
            traceback.print_tb(sys.exc_info()[2])
            self.text += u'|class="shadow"|[[%s]]||colspan="3"|Не удалось обработать\n|-\n' % (article)
            return
        replics = 0
        f = self.cache.findone("articles", {"name":article}, ["oldid", "ts", "replics"])
        if f == None: # Статья не найдена, обрабатываем
        # Определяем рост статьи с момента выставления шаблона
        # ts  = дата простановки шаблона,
        #         хранится в кэше/первый раз берется в истории
        # ts1 = дата в шаблоне, ссылка на страницу обсуждения

            diff = len(p.get()) #инициализация переменных чтоб не падало
            oldid = 0
            
            ts = ts1
            for l in hist:
                try:
                    text = l[3].decode("utf-8", "ignore")
                except UnicodeEncodeError, e:
                    text = l[3]
                edits = edits-1 # эта правка без шаблона
                if (text.find(u'{{к улучшению') != -1) or \
                   (text.find(u'{{К улучшению') != -1):
                    oldid = l[0] # первая версия, где стоит шаблон
                    diff -= len(text) # Изменение объёма статьи
                    # Момент выставления шаблона
                    ts  = date(int(l[1][0:4]), int(l[1][5:7]), int(l[1][8:10]))
                    break

            cached = u"(saved to cache)"
            self.cache.insert("articles", (0, oldid, ts, title))
        else:# Статья найдена в кеше
            cached = u"(taken from cache)"
            (oldid, ts, replics) = f
            diff = len(p.get()) - len(p.getOldVersion(oldid)) # found size
            for l in hist:
                edits = edits-1
                if l[0] == oldid:
                    break
        # lighting by due date from the date of nomination
        style = D[max([_ for _ in D if _ < (date.today()-ts).days])]

        month = MONTHS[ts1.month-1]
        wikipedia.output((u"Статья %s /%s/ выставлена %s, реплик %s, изменение %s, правок %s %s") % (title, self.pagename, ts1, replics, diff, edits, cached))
        self.text += u"|%s[[%s]]||%s[[Википедия:К улучшению/%s %s %s#%s|%s]]||%s%s||%s[http://ru.wikipedia.org/w/index.php?title=%s&diff=cur&oldid=%s %s]||%s%s \n|-\n" % \
                    (style, article, style, ts1.day, month, ts1.year, article, ts1, style, replics, style, self.cache.quote(article), oldid, diff, style, edits)
  
    def run(self):
        """Получает тематику и родительскую категорию
        Формирует и сохраняет тематическую страницу"""
        self.cache = Storage()
        try:
            self.text  = u'{|class="standard sortable" width="75%"\n'
            self.text += u"!Статья||Дата КУЛ||{{comment|Реплик|Строк в обсуждении}}||{{comment|Изменение|объём в символах}}||Правок сделано\n"
            self.text += u"|- \n"
            ci = CategoryIntersect('Википедия:Статьи для срочного улучшения', \
                                    self.catname)
            for name in ci:
                self.addline(name) # дописали текст
        except Exception, e:
            wikipedia.output(u"Ошибка получения данных тематики %s: %s"% \
                                    (self.pagename, e))
            traceback.print_tb(sys.exc_info()[2])
            self.cache = None
            self.run()
            return
        self.text += "|}"
        self.text += u"<noinclude>[[Категория:Википедия:Списки статей к улучшению]]</noinclude>"
        self.save()
        cache = Storage()
        cache.delete("updates", {"topic":self.pagename})
        cache.insert("updates", \
                    (self.pagename, datetime.date(datetime.now()), len(ci)))

def get_base():
    """Gets topic and categories from online"""
    p = wikipedia.Page(SITE, u'Википедия:К улучшению/Тематические обсуждения/Service').get().split("\n")
    b = {}
    for l in p:
        l = l.strip()
        if len(l) > 0 and l[0]!='!':
            [H, T] = l.split(':')
            b[H] =  T.split(',')
    return b

def runThreads(l):
    l2 = []
    for t in l:
        l2.append(CleanupTematic(t, BASE[t]))
        l2[-1].start()
#        l2[-1].join()
    for t in l2:
        t.join()

if __name__ == "__main__":
    # start point
    SITE = wikipedia.getSite()
    #CACHE = Storage("articles.db")    
    BASE = get_base()

    if len(sys.argv) >= 2: # got arguments in command line
        if sys.argv[1] == "stats" or sys.argv[1] == "all":
            AllAFI(sys.argv[1]).run()
            sys.exit()
        uBASE = [unicode(i, locale.getpreferredencoding()) for i in sys.argv[1:]]
        runThreads(uBASE)
        print "fin"
    else: # no arguments, full run
        ReplicsCounter().countCat(u"Категория:Википедия:Незакрытые обсуждения статей для улучшения")
        runThreads(BASE)
        AllAFI("all").run()
    TemplateRandom().save()
