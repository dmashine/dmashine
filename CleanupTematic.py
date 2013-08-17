#!/usr/bin/env python
# -*- coding: utf-8-*-
""" Скрипт разделяет статьи, предложенные к улучшению в ru.wikipedia
по тематическим страницам.
Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware.
Для длинных списков:
        <div style="height:200px; overflow:auto; padding:3px"></div>"""

import traceback, datetime, sys, locale
import wikipedia
import httphelp
import sqlite3
from threading import Thread
from CategoryIntersect import CategoryIntersect#, \
                              #CategoryIntersectException

MONTHS = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']

class Storage(object):
    """ Interface to sqlite."""
    def __new__(cls):
        """Makes it singleton"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Storage, cls).__new__(cls)
        return cls.instance

    def __init__(self, name = "articles.db"):
        self.quote = lambda s: s.replace(" ", "_").replace('"', "'")
        self.conn = sqlite3.connect(name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, check_same_thread = False)
        #self.conn = sqlite3.connect(name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cursor = self.conn.cursor()
        try:  # Create table
            self.cursor.execute(u'''CREATE TABLE articles (oldid INT UNIQUE, name TEXT, ts DATE)''')
            self.cursor.execute(u'''CREATE TABLE updates (topic TEXT, ts TIMESTAMP, n INT)''')
            print "tables created"
            # CREATE TABLE IF NOT EXISTS
        except sqlite3.Error:
            #table already created
            pass
        print "Connection started %s " % self.cursor

    def insert(self, table, values):
        """Insert a row of values to table"""
        try:
            v = u", ".join([u"\""+self.quote(u"%s" % s)+u"\"" for s in values])
            s = u"INSERT INTO %s VALUES (%s);" % (table, v)
            self.cursor.execute(s)
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
            
    def find(self, name):
        """Finds article in articles table"""
        name2 = self.quote(name)
        re = self.cursor.execute(u"SELECT oldid, ts FROM articles WHERE name = \"%s\"" % name2)
        return re.fetchone()
        
    def delete(self, table, cond = None):
        """Deletes rows from table, by condition cond.
            Cond is dict: col = value"""
        # bug here, when len(cond) > 1
        c = ""
        if cond:
            c = u" WHERE "
            for l in cond:
                c += "%s = \"%s\"" % (l, self.quote(cond[l]))
        s = u"DELETE FROM %s%s;" % (table, c)
        self.cursor.execute(s)

    def _clean(self):
        """Cleans all tables. Not used."""
        self.cursor.execute(u"DELETE FROM articles")
        self.cursor.execute(u"DELETE FROM updates")
        self.conn.commit()

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
        self.cache = Storage()

    def save(self, minoredit=True, botflag=True, dry=False):
        """Saves data to wikipedia page"""
        httphelp.save(SITE, text=self.text, pagename=u"Википедия:К улучшению/Тематические обсуждения/"+self.pagename, comment=u"Статьи для срочного улучшения (3.2) тематики "+self.pagename, minoredit=minoredit, botflag=botflag, dry=dry)
  
    def addline(self, article):
        """Gets article name. Adds to self.text one line of table. """
        p = wikipedia.Page(SITE, article)
        
        title = p.titleWithoutNamespace()
        param = ''
        for tl in p.templatesWithParams():
            if tl[0] == u'К улучшению':
                try:
                    param = tl[1][0]
                    ts1 = datetime.date(int(param[0:4]), int(param[5:7]), int(param[8:10]))
                except IndexError, e:
                    wikipedia.output(u"Ошибка в дате статьи %s:%s"%(article, e))
                    self.text += u'|class="shadow"|[[%s]]||colspan="3"|Некорректные параметры шаблона КУЛ\n|-\n' % (article) # afi date not found
                    return
                break
        if param == '':
            self.text += u'|class="shadow"|[[%s]]||colspan="3"|Не обнаружен шаблон КУЛ\n|-\n' % (article)
            wikipedia.output(u"Статья %s без шаблона! " % (article))
            # what a mess, has a category, and no template
            return

        f = self.cache.find(article)

        if f == None: # Статья не найдена, обрабатываем
        # Определяем рост статьи с момента выставления шаблона
        # ts  = дата простановки шаблона,
        #         хранится в кэше/первый раз берется в истории
        # ts1 = дата в шаблоне, ссылка на страницу обсуждения
        
            try:
                edits = len(p.getVersionHistory(False, False, True)) #number of edits made
                size1 = 0 #инициализация переменных чтоб не падало
                oldid = 0
                ts = ts1
                for l in p.fullVersionHistory(getAll = False, skipFirst = False, reverseOrder = True):
                    try:
                        text = l[3].decode("utf-8", "ignore")
                    except UnicodeEncodeError, e:
                        text = l[3]
                    edits = edits-1 #эта правка без шаблона
                    if (text.find(u'{{к улучшению') != -1) or (text.find(u'{{К улучшению') != -1):
                        oldid = l[0] #первая версия, где стоит шаблон
                        size1 = len(text) # её объём
                         # Момент выставления шаблона
                        ts  = datetime.date(int(l[1][0:4]), int(l[1][5:7]), int(l[1][8:10]))
                        break
                diff = len(p.get())-size1 # Изменение объёма статьи с момента простановки шаблона
            except Exception, e:
                traceback.print_tb(sys.exc_info()[2])
                self.text += u'|class="shadow"|[[%s]]||colspan="3"|Не удалось обработать\n|-\n' % (article)
                return
            cached = u"(saved to cache)"
            self.cache.insert("articles", (oldid, title, ts))
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
        style = ''
        past = (datetime.date.today()-ts).days
        if past > 180: # lighting by due date from the date of nomination
            style = 'class="bright"|'
        elif past > 90:
            style = 'class="highlight"|'
        
        
        month = MONTHS[ts1.month-1]
        wikipedia.output((u"Статья %s /%s/ выставлена %s, изменение %s, правок %s %s") % (title, self.pagename, param, diff, edits, cached))
        self.text += u"|%s[[%s]]||%s[[Википедия:К улучшению/%s %s %s#%s|%s]]||%s[http://ru.wikipedia.org/w/index.php?title=%s&diff=cur&oldid=%s %s]||%s%s \n|-\n" % (style, article, style, ts1.day, month, ts1.year, article, param, style, self.cache.quote(article), oldid, diff, style, edits)
  
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
        cache = Storage()
        cache.delete("updates", {"topic":self.pagename})
        cache.insert("updates", (self.pagename, datetime.datetime.now(), len(ci)))

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

if __name__ == "__main__":
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
