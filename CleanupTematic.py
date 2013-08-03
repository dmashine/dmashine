#!/usr/bin/env python
# -*- coding: utf-8-*-
""" Скрипт разделяет статьи, предложенные к улучшению в ru.wikipedia
по тематическим страницам.
Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware.
Для длинных списков^
        <div style="height:200px; overflow:auto; padding:3px"></div>"""

import traceback, datetime, sys, locale
import wikipedia
import httphelp
import sqlite3
from threading import Thread
from CategoryIntersect import CategoryIntersect, \
                              CategoryIntersectException

MONTHS = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']

class Storage:
    """ Interface to sqlite."""

    def __init__(self, name):
        self.conn = sqlite3.connect(name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cursor = self.conn.cursor()
        try: # time waste here?
            # Create table
            self.cursor.execute(u'''CREATE TABLE articles (oldid INT UNIQUE, name TEXT, ts DATE)''')
            self.cursor.execute(u'''CREATE TABLE updates (topic TEXT, ts TIMESTAMP)''')
            print "tables created"
        except sqlite3.Error:
            #table already created
            pass
    def update_topic(self, topic):
        """Updates one topic in updates table"""
        try:
            self.cursor.execute(u"DELETE FROM updates WHERE topic = \"%s\"" % topic)
            self.cursor.execute(u"INSERT INTO updates VALUES (\"%s\", \"%s\")" % (topic, datetime.datetime.now()))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def insert(self, oldid, name, timestamp):
        """Insert a row of data"""
        try:
            #ts = datetime.datetime(int(year), int(month), int(date))
            self.cursor.execute(u"INSERT INTO articles VALUES (%s, \"%s\",\"%s\")" % (oldid, name.replace(" ", "_"), timestamp))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
            
    def find(self, name):
        """Finds article in articles table"""
        re = self.cursor.execute(u"SELECT oldid, ts FROM articles WHERE name = \"%s\"" % name.replace(" ", "_"))
        return re.fetchone()

    def _clean(self):
        """Cleans all tables. Not used."""
        self.cursor.execute(u"DELETE FROM articles")
        self.cursor.execute(u"DELETE FROM updates")
        self.conn.commit()
        
    def _print_stats(self):
        """Some stats. Not used, actually"""
        re = self.cursor.execute(u"SELECT date, topic FROM updates ORDER BY DATE;")
        for l in re.fetchall():
            print u"%s %s" % l
        re = self.cursor.execute(u"SELECT count(*) FROM articles;")
        for l in re.fetchall():
            print u"count: %s" % l

    def __del__(self):
        """We can also close the connection if we are done with it.
        Just be sure any changes have been committed or they will be lost."""
        self.conn.commit()
        self.conn.close()


class CleanupTematic(Thread):
    """One thread of bot that cleans one theme"""
    def __init__(self, pagename, catname):
        Thread.__init__(self)
        self.pagename = pagename
        self.catname = catname
        self.text = ''

    def save(self, minoredit=True, botflag=True, dry=False):
        """Saves data to wikipedia page"""
        httphelp.save(SITE, text=self.text, pagename=u"Википедия:К улучшению/Тематические обсуждения/"+self.pagename, comment=u"Статьи для срочного улучшения (3.1) тематики "+self.pagename, minoredit=minoredit, botflag=botflag, dry=dry)
  
    def addline(self, article):
        """Gets article name. Adds to self.text one line of table. """
        p = wikipedia.Page(SITE, article)
        
        title = p.titleWithoutNamespace()
        param = ''
        for tl in p.templatesWithParams():
            if tl[0] == u'К улучшению':
                try:
                    param = tl[1][0]
                    ts = datetime.date(int(param[0:4]), int(param[5:7]), int(param[8:10]))
                except IndexError, e:
                    wikipedia.output(u"Ошибка в дате статьи %s: %s"%(article, e))
                    self.text += u'|class="shadow"|[[%s]]||colspan="3"|Некорректные параметры шаблона КУЛ\n|-\n' % (article) # afi date not found
                    return
                break
        if param == '':
            self.text += u'|class="shadow"|[[%s]]||colspan="3"|Не обнаружен шаблон КУЛ\n|-\n' % (article)
            wikipedia.output(u"Статья %s без шаблона! " % (article))
            # what a mess, has a category, and no template
            return
        else:
            style = ''
            past = (datetime.date.today()-ts).days
        
            if past > 180: # lighting by due date from the date of nomination
                style = 'class="bright"|'
            elif past > 90:
                style = 'class="highlight"|'

        cache = Storage("articles.db")
        
        # Если статья есть в кеше, заполняем значения param, diff, edits
        # Иначе обрабатываем и записываем в кеш
        f = cache.find(article)

        if f == None: # Статья не найдена, обрабатываем
        # Определяем рост статьи с момента выставления шаблона
            try:
                edits = len(p.getVersionHistory(False, False, True)) #number of edits made
                size1 = 0 #инициализация переменных чтоб не падало
                oldid = 0 
                for l in p.fullVersionHistory(False, False, True):
                    try:
                        text = l[3].decode("utf-8", "ignore")
                    except UnicodeEncodeError, e:
                        text = l[3]
                    edits = edits-1 #эта правка без шаблона
                    if (text.find(u'{{к улучшению') != -1) or (text.find(u'{{К улучшению') != -1):
                        oldid = l[0] #первая версия, где стоит шаблон
                        size1 = len(text) # её объём
#                       term  = l[1] # Момент выставления шаблона
                        break
                diff = len(p.get())-size1 # Изменение объёма статьи с момента простановки шаблона
            except (CategoryIntersectException, httphelp.HttpHelpException), e:
                traceback.print_tb(sys.exc_info()[2])
                self.text += u'|class="shadow"|[[%s]]||colspan="3"|Не удалось обработать\n|-\n' % (article)
                return
            cached = u"(saved to cache)"
            cache.insert(oldid, title, ts)
        else:# Статья найдена в кеше
            cached = u"(taken from cache)"
            (oldid, ts) = f
            diff = len(p.get()) - len(p.getOldVersion(oldid)) # found size
            edits = 0
            for l in p.getVersionHistory(forceReload=False, reverseOrder=False, getAll=True):
                if l[0] != oldid:
                    edits = edits+1
                else:
                    break

        month = MONTHS[ts.month-1]
        wikipedia.output((u"Статья %s /%s/ выставлена %s, изменение %s, правок %s %s") % (title, self.pagename, param, diff, edits, cached))
        self.text += u"|%s[[%s]]||%s[[Википедия:К улучшению/%s %s %s#%s|%s]]||%s[http://ru.wikipedia.org/w/index.php?title=%s&diff=cur&oldid=%s %s]||%s%s \n|-\n" % (style, article, style, ts.day, month, ts.year, article, param, style, article.replace(" ", "_"), oldid, diff, style, edits)
  
    def run(self):
        """Получает тематику и родительскую категорию
        Формирует и сохраняет тематическую страницу"""
        try:
            self.text  = u'{|class="standard sortable" width="75%"\n'
            self.text += u"!Статья||Дата КУЛ||{{comment|Изменение|объём в символах}}||Правок сделано\n"
            self.text += u"|- \n"
            ci = CategoryIntersect('Википедия:Статьи для срочного улучшения', self.catname)
            for name in ci:
                self.addline(name) # дописали текст
        except Exception, e:
            wikipedia.output(u"Ошибка получения данных тематики %s: %s"%(self.pagename, e))
            traceback.print_tb(sys.exc_info()[2])
            #self.run()
            return
        self.text += "|}"
        self.save()
        cache = Storage("articles.db")
        cache.update_topic(self.pagename)

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

# start point
SITE = wikipedia.getSite()
#CACHE = Storage("articles.db")    
BASE = get_base()

if len(sys.argv) >= 2: # got arguments in command line
    for i in sys.argv[1:]:
        #j = unicode(i, "mbcs") # windows
        j = unicode(i, locale.getpreferredencoding())
        th = CleanupTematic(j, BASE[j])
        th.start()
else:
    for i in BASE:
        th = CleanupTematic(i, BASE[i])
        th.start()
