#!/usr/bin/env python
# -*- coding: utf-8-*-
""" Скрипт разделяет статьи, предложенные к улучшению в ru.wikipedia
по тематическим страницам. Извиняюсь за мешанину с unicode(хотя старался исправить) и стиль.
Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware.
Для длинных списков <div style="height:200px; overflow:auto; padding:3px"></div>"""

import traceback, datetime, sys, locale
import wikipedia
import httphelp
import sqlite3
from threading import Thread
from time import localtime, strftime
from CategoryIntersect import CategoryIntersect

Months = {'01':u'января',
        '02':u'февраля',
        '03':u'марта',
        '04':u'апреля',
        '05':u'мая',
        '06':u'июня',
        '07':u'июля',
        '08':u'августа',
        '09':u'сентября',
        '10':u'октября',
        '11':u'ноября',
        '12':u'декабря'}
base = {#u'Авиация':'Aвиация',
# u'Адмиралтейство':'Флот',
 u'Азербайджан':'Азербайджан',
 u'Аниме':'Аниме', 
 u'Биология':['Биология', 'Организмы'], # u'Биология':'Биология',
 u'Ботаника':'Ботаника',
 u'География':'География',
 u'Бронетехника':'Бронетехника',
 u'Ирландия':'Ирландия',
 u'Кино':'Кинематограф',
 u'Компьютерные игры':'Компьютерные игры',
 u'Медицина':'Медицина',
 u'Права человека': 'Права человека',
# u'Молдавия':'Молдавия',
 u'Персоналии':'Персоналии по алфавиту',
 u'Музыка':'Музыка',
 u'Право':'Право',
 u'Православие':'Православие',
 u'Программное обеспечение':'Программное обеспечение',
 u'Санкт-Петербург':'Санкт-Петербург',
 u'Свободное программное обеспечение':'Свободное программное обеспечение',
# u'Транспорт':'Транспорт',
 u'Экономика':'Экономика',
 u'Филология':'Филология',
 u'Феминизм':'Феминизм',
 u'Футбол':'Футбол',
 u'Япония':'Япония'}

class Storage:
    """ Interface to sqlite.
    TODO: https://ru.wikipedia.org/wiki/Double_checked_locking"""

    def __init__(self, name):
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()
        try: # time waste here?
            # Create table
            self.cursor.execute(u'''CREATE TABLE articles (oldid INT UNIQUE, name TEXT, date TEXT, month TEXT, year TEXT)''')
            self.cursor.execute(u'''CREATE TABLE updates (topic TEXT, date TEXT)''')
            print "tables created"
        except:
            #table already created
            pass
    def update_topic(self, topic):
        try:
            self.cursor.execute(u"DELETE FROM updates WHERE topic = \"%s\"" % topic)
            self.cursor.execute(u"INSERT INTO updates VALUES (\"%s\", \"%s\")" % (topic, strftime("%d %b %Y %H:%M:%S", localtime())))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def print_stats(self):
        re = self.cursor.execute(u"SELECT date, topic FROM updates ORDER BY DATE;")
        for l in re.fetchall():
            print u"%s %s" % l
        re = self.cursor.execute(u"SELECT count(*) FROM articles;")
        for l in re.fetchall():
            print u"count: %s" % l

    def insert(self, oldid, name, date, month, year):
        """Insert a row of data"""
        try:
            self.cursor.execute(u"INSERT INTO articles VALUES (%s, \"%s\", \"%s\", \"%s\", \"%s\")" % (oldid, name.replace(" ", "_"), date, month, year))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
            
    def find(self, name):
        re = self.cursor.execute(u"SELECT oldid, date, month, year FROM articles WHERE name = \"%s\"" % name.replace(" ", "_"))
        return re.fetchone()

    def clean(self):
        self.cursor.execute(u"DELETE FROM articles")

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
        httphelp.save(site, text=self.text, pagename=u"Википедия:К улучшению/Тематические обсуждения/"+self.pagename, comment=u"Статьи для срочного улучшения (3.0) тематики "+self.pagename, minoredit=minoredit, botflag=botflag, dry=dry)
  
    def addline(self, article):
        """Gets article name. Adds to self.text one line of table. """
        p = wikipedia.Page(site, article)

        title = p.titleWithoutNamespace()
        param = ''
        for tl in p.templatesWithParams():
            if tl[0] == u'К улучшению':
                try:
                    param = tl[1][0]
                except Exception, e:
                    wikipedia.output(u"Статья %s без даты выставления! " % (article))
                    self.text += u'|class="shadow"|[[%s]]||colspan="3"|Некорректные параметры шаблона КУЛ\n|-\n' % (article) # afi date not found
                    return
                break
        if param == '':
            self.text += u'|class="shadow"|[[%s]]||colspan="3"|Не обнаружен шаблон КУЛ\n|-\n' % (article)
            wikipedia.output(u"Статья %s без шаблона! " % (article))
            # what a mess, has a category, and no template
            return
        cache = Storage("articles.db")
        
        # Если статья есть в кеше, заполняем значения param, diff, edits
        # Иначе обрабатываем и записываем в кеш
        f = cache.find(article)
        
        if f == None: # Статья не найдена, обрабатываем        
            try:
                month = Months[param[5:7]] # Словесное название месяца из даты
                year = param[0:4]
                date = param[8:10]
                if date[0] == '0': # remove non-significant 0 from date
                    date = date[1]
            #except: # errors in date conversion
            except Exception, e:
                wikipedia.output(u"Ошибка конвертации даты %s: %s"%(article, e))
                traceback.print_tb(sys.exc_info())#[2])
                self.text += u'|class="shadow"|[[%s]]||colspan="3"|Некорректные параметры шаблона КУЛ\n|-\n' % (article)
                return

        # Определяем рост статьи с момента выставления шаблона
            try:
                edits = len(p.getVersionHistory(False, False, True)) #number of edits made
                size1 = 0 #инициализация переменных чтоб не падало
                oldid = 0 #TODO обойти както...
                for l in p.fullVersionHistory(False, False, True):
                    try:
                        text = l[3].decode("utf-8", "ignore")
                    except Exception, e:
                        text = l[3]
                    edits = edits-1 #эта правка без шаблона
                    if (text.find(u'{{к улучшению') != -1) or (text.find(u'{{К улучшению') != -1):
                        oldid = l[0] #первая версия, где стоит шаблон
                        size1 = len(text) # её объём
                        break
                diff = len(p.get())-size1 # Изменение объёма статьи с момента простановки шаблона
            except Exception, e:
                self.text += u'|class="shadow"|[[%s]]||colspan="3"|Не удалось обработать\n|-\n' % (article)
                return
            cached = u"(saved to cache)"
            cache.insert(oldid, title, date, month, year)
        else:  # Статья найдена в кеше
            cached = u"(taken from cache)"
            (oldid, date, month, year) = f
            currenttext = len(p.get())
            diff = currenttext - len(p.getOldVersion(oldid)) # found size
            edits = 0
            for l in p.getVersionHistory(forceReload=False, reverseOrder=False, getAll=True):
                if l[0] != oldid:
                    edits = edits+1
                else:
                    break

        style = ""
        d = datetime.date(int(year), int(param[5:7]), int(date))
        past = (datetime.date.today()-d).days
        if past > 180: # lighting by due date from the date of nomination
            style = 'class="bright"|'
        elif past > 90:
            style = 'class="highlight"|'
        wikipedia.output((u"Статья %s /%s/ выставлена %s, изменение %s, правок %s %s") % (title, self.pagename, param, diff, edits, cached))
        self.text += u"|%s[[%s]]||%s[[Википедия:К улучшению/%s %s %s#%s|%s]]||%s[http://ru.wikipedia.org/w/index.php?title=%s&diff=cur&oldid=%s %s]||%s%s \n|-\n" % (style, article, style, date, month, year, article, param, style, article.replace(" ", "_"), oldid, diff, style, edits)
  
    def run(self):
        """Получает тематику и родительскую категорию
        Формирует и сохраняет тематическую страницу"""
        try:
            #self.text="== "+self.pagename+" == \n"
            self.text  = u'{|class="standard sortable" width="75%"\n'
            self.text += u"!Статья||Дата КУЛ||{{comment|Изменение|объём в символах}}||Правок сделано\n"
            self.text += u"|- \n"
            ci = CategoryIntersect('Википедия:Статьи для срочного улучшения', self.catname)
            for name in ci:
                self.addline(name) # дописали текст
        except Exception, e:
            wikipedia.output(u"Ошибка получения данных тематики %s: %s"%(self.pagename, e))
            #wikipedia.output(u"Ошибка получения данных тематики %s"%(self.pagename))
            traceback.print_tb(sys.exc_info()[2])
            #self.run()
            return
        self.text += "|}"
        self.save()
        cache = Storage("articles.db")
        cache.update_topic(self.pagename)
# start point
site = wikipedia.getSite()

#cache = Storage("articles.db")

if len(sys.argv) >= 2: # got arguments in command line
    for i in sys.argv[1:]:
        #j = unicode(i, "mbcs") # windows
        j = unicode(i, locale.getpreferredencoding())
        th = CleanupTematic(j, base[j])
        th.start()
else:
    for i in base:
        th = CleanupTematic(i, base[i])
        th.start()
