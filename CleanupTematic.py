#!/usr/bin/env python
# -*- coding: utf-8-*-
# Скрипт разделяет статьи, предложенные к улучшению в ru.wikipedia
#   по тематическим страницам. Извиняюсь за мешанину с unicode(хотя старался исправить) и стиль.
# Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
# Лицензирование: GNU GPL v3 / Beerware.
# Для длинных списков <div style="height:200px; overflow:auto; padding:3px"></div>

import traceback, exceptions, datetime, sys, locale
import wikipedia
import httphelp
from threading import Thread
from CategoryIntersect import CategoryIntersect

months={'01':u'января',
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
base={#u'Авиация':'Aвиация',
# u'Адмиралтейство':'Флот',
 u'Азербайджан':'Азербайджан',
 u'Аниме':'Аниме', 
 u'Биология':'Биология',
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
# u'Транспорт':'Транспорт',
 u'Экономика':'Экономика',
 u'Филология':'Филология',
 u'Футбол':'Футбол',
 u'Япония':'Япония'}
		

class CleanupTematic(Thread):
  def __init__(self, pagename, catname):
    Thread.__init__(self)
    self.pagename=pagename
    self.catname=catname
    self.text=''
  def save(self, minorEdit=True, botflag=True, dry=False):
    httphelp.save(site, text=self.text, pagename=u"Википедия:К улучшению/Тематические обсуждения/"+self.pagename, comment=u"Статьи для срочного улучшения (2.5) тематики "+self.pagename, minorEdit=minorEdit, botflag=botflag)
  
  def addline(self, article):
    """ Gets article name. Returns string- one line of table. """
    p=wikipedia.Page(site, article)
    title=p.titleWithoutNamespace()
    param=''
    for tl in p.templatesWithParams():
        if tl[0] ==u'К улучшению':
          try:
            param= tl[1][0]
          except:
            wikipedia.output(u"Статья %s без даты выставления! "%(article))
            self.text+= u'|class="shadow"|[[%s]]||colspan="3"|Некорректные параметры шаблона КУЛ\n|-\n'%(article) # afi date not found
            return
          break
    if param=='':
      self.text+= u'|class="shadow"|[[%s]]||colspan="3"|Некорректные параметры шаблона КУЛ\n|-\n'%(article)
      # what a mess, has a category, and no template
      return
    try:  
      month=months[param[5:7]] # Словесное название месяца из даты
      year=param[0:4]
      date=param[8:10]
      if date[0]=='0': # remove non-significant 0 from date
        date=date[1]
      d=datetime.date(int(year), int(param[5:7]), int(date))
      style=""
      past=(datetime.date.today()-d).days
      if past > 180: # lighting by due date from the date of nomination
        style='class="bright"|'
      elif past > 90:
        style='class="highlight"|'
    except: # errors in date conversion
      self.text+= u'|class="shadow"|[[%s]]||colspan="3"|Некорректные параметры шаблона КУЛ\n|-\n'%(article)
      return

    # Определяем рост статьи с момента выставления шаблона
    edits=len(p.getVersionHistory(False, False, True)) #number of edits made
    size1=0; oldid=0 #инициализация переменных чтоб не падало
    try:
        for l in p.fullVersionHistory(False, False, True):
          try:
             text=l[3].decode("utf-8", "ignore") 
          except:
             text=l[3]
          edits=edits-1 #эта правка без шаблона
          if (text.find(u'{{к улучшению') <> -1) or (text.find(u'{{К улучшению') <> -1):
            oldid=l[0] #первая версия, где стоит шаблон
            size1=len(text) # её объём
            break
        diff=len(p.get())-size1 # Изменение объёма статьи с момента простановки шаблона
    except:
        self.text+= u'|class="shadow"|[[%s]]||colspan="3"|Не удалось обработать\n|-\n'%(article)
        return            
    wikipedia.output((u"Статья %s /%s/ выставлена %s, изменение %s, правок %s")%(title, self.pagename, param, diff, edits))
    self.text+= u"|%s[[%s]]||%s[[Википедия:К улучшению/%s %s %s#%s|%s]]||%s[http://ru.wikipedia.org/w/index.php?title=%s&diff=cur&oldid=%s %s]||%s%s \n|-\n"%(style, article, style, date, month, year, article, param, style, article.replace(" ", "_"), oldid, diff, style, edits)
  
  def run(self):
    """Получает тематику и родительскую категорию
    Формирует и сохраняет тематическую страницу"""
    try:
      #self.text="== "+self.pagename+" == \n"
      self.text=u'{|class="standard sortable" width="75%"\n'
      self.text+=u"!Статья||Дата КУЛ||{{comment|Изменение|объём в символах}}||Правок сделано\n"
      self.text+=u"|- \n"
      ci = CategoryIntersect('Википедия:Статьи для срочного улучшения', self.catname)
      for name in ci:
        self.addline(name) # дописали текст
    except Exception, e:
      wikipedia.output(u"Ошибка получения данных тематики %s: %s"%(self.pagename, e))
      traceback.print_tb(sys.exc_info()[2])
      self.run()
      return
    self.text+="|}"
    self.save()
# start point
site = wikipedia.getSite()
if len(sys.argv)>=2: # got arguments in command line
  for i in sys.argv[1:]:
    #j=unicode(i, "mbcs") # windows
    j=unicode(i, locale.getpreferredencoding())
    th=CleanupTematic(j, base[j])
    th.start()
else:
  for i in base:
    th=CleanupTematic(i, base[i])
    th.start()
