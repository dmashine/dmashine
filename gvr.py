#!/usr/bin/env python
# -*- coding: utf-8-*-
import httplib, urllib, re, wikipedia
#from threading import Thread

template = u"""{{Озеро
 |Название                 = %(Название)s
  |Национальное название   = %(Названия)s
 |Изображение              = 
  |Подпись                 = 
  |lat_dir = N|lat_deg = |lat_min = |lat_sec = 
  |lon_dir = E|lon_deg = |lon_min = |lon_sec = 
  |region                  = 
  |CoordScale              = 
 |Страна                   = Россия
  |Регион                  = 
 |Высота над уровнем моря  = 
 |Длина                    = 
 |Ширина                   = 
 |Площадь                  = %(Площадь водоёма)s
 |Объём                    = 
 |Длина береговой линии    = 
 |Наибольшая глубина       = 
  |Средняя глубина         = 
 |Тип минерализации        = 
  |Солёность               = 
 |Прозрачность             = 
 |Площадь водосбора        = %(Водосборная площадь)s
  |Впадающие реки          = 
  |Вытекающая река         = %(Вытекает)s
 |Позиционная карта 1      = 
 |Позиционная карта 2      = 
 |Категория на Викискладе  = 
}}
'''%(Название)s''' — озеро в России. Местоположение - %(Местоположение)s. Площадь водоёма %(Площадь водоёма)s км²
== Данные водного реестра ==
По данным геоинформационной системы водохозяйственного районирования территории РФ, подготовленной Федеральным агентством водных ресурсов<ref name='МПР России'>{{cite web|url=http://textual.ru/gvr/index.php?card=%(card)s|title=Государственный водный реестр РФ: %(Название)s}}</ref>
* Код водного объекта — %(Код водного объекта)s
* Бассейновый округ — %(Бассейновый округ)s
* Речной бассейн — %(Речной бассейн)s
* Речной подбассейн — %(Речной подбассейн)s
* Код по гидрологической изученности (ГИ) — %(Код по гидрологической изученности)s
* Номер тома по ГИ — %(Номер тома по ГИ)s, %(Выпуск по ГИ)s
* Выпуск по ГИ — %(Выпуск по ГИ)s

== Примечания == 
{{примечания}} 

== Ссылки == 
* {{Водный реестр}}

[[:Категория:Озёра Карелии]]
<br clear="all">
"""

class request:
    def __init__():
        pass

class GVRException(Exception):
    pass

class GVRObject:
    """Represents object of GVR site."""    
    def __init__(self, card):     
        self._card = card
        self._conn = httplib.HTTPConnection("textual.ru")
        self._params = urllib.urlencode({'card': card})
        self._headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        self._data={}
        self._data[u"Названия"] = ""
        self._data[u"Вытекает"] = ""
        self._data[u"card"] = card
        self._conn.request("POST", "/gvr/index.php", self._params, self._headers)
        response = self._conn.getresponse()
        #print self._card, response.status, response.reason
        lines = [l.decode("windows-1251") for l in response.read().splitlines()]

        for l in lines:
            if l.find('class="cardv"')>0:
                key=""
                for s in re.split('<.+?>', l):
                    if s<>"":
                        if key<>"":
                            # workarounds for different keys
                            if key == u"Площадь водоёма" or key == u"Водосборная площадь":
                                self._data[key]=unicode(s[:-9])
                            elif key == u"Название" and s.find("(")>0:
                                self._data[key] = unicode(s[:s.find("(")])
                                self._data[u"Названия"] = unicode(s[s.find("(")+1:s.find(")")])
                            elif key == u"Вытекает" and s.find(u"река")==0:
                                if s.find("(") >0:
                                    self._data[u"Вытекает"] = unicode(s[5:s.find("(")])
                                else:
                                    self._data[u"Вытекает"] = s[5:]
                            elif key == u"Бассейновый округ" or key == u"Речной бассейн" or key == u"Речной подбассейн":
                                if s.find("(") >0:
                                    self._data[key]=unicode(s[:s.find("(", -5)])
                            else: # get it 
                                self._data[key]=unicode(s)
                        else: #first string in response is key, second is parameter
                            key=unicode(s)
    def get_data(self):
        return self._data
    def __repr__(self):
        return u"GVRObject "+self._card+u"\r"
    def __del__(self):
        self._conn.close()
class GVRList:
    """Represents list of GVR objects.
        init parameters as in official site, may be omitted"""
    def __init__(self, bo="", rb="", subb="", hep="", wot="", name="", num="", loc="", start=0):
        # http://textual.ru/gvr/index.php?bo=1&rb=68&subb=0&hep=0&wot=11&name=&num=&loc=&s=%CF%EE%E8%F1%EA
        self.conn = httplib.HTTPConnection("textual.ru")
        self.params = urllib.urlencode({'bo': bo, "rb":rb, "subb":subb, "hep":hep, "wot": wot, "name":name, "num":num, "loc":loc, "start":start})
        self.headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        self._data=[]
        self.conn.request("POST", "/gvr/index.php", self.params, self.headers)
        response = self.conn.getresponse()
        print response.status, response.reason, start
        lines = [l.decode("windows-1251") for l in response.read().splitlines()]
        for l in lines:
            b=l.find('/gvr/index.php?card=')
            if b>0:
                self._data+=[l[b+20:l.find('&',b)]]
            if l.find(u'следующая страница результатов')>1: # results divided into pages.
                self._data+=GVRList(bo, rb, subb, hep, wot, name, num, loc, start+200).get_data()
       #self.test()
    def test(self):
        for l in self:
            print ">"+l
    def get_data(self):
        return self._data
    def __iter__(self):
        return self
    def next(self): #__next__() in >3.0
        if len(self._data) == 0:
          raise StopIteration	
        return GVRObject(self._data.pop(0))
    def __del__(self):
        self.conn.close()

def save(text, minorEdit=True, botflag=True, dry=False):  
    # save text to wiki
    # TODO move somewhere
    # Статьи по названию name нет? пишем.
    #   если есть - пишем в name(Озеро)
    page=wikipedia.Page(site, u"Участник:Drakosh/Озеро")
    if not dry:
      try:
        # Сохраняем
        page.put(text,  u"Тестовая заливка озер", minorEdit=minorEdit, botflag=True)
      except wikipedia.LockedPage:
        wikipedia.output(u"Страница %s заблокирована; пропускаю." % page.title(asLink=True))
      except wikipedia.EditConflict:
        wikipedia.output(u'Пропускаю %s, конфликт правок'% (page.title()))
      except wikipedia.SpamfilterError, error:
        wikipedia.output(u'Пропущена страница %s, не пускает спамфильтр %s' % (page.title(), error.url))
      else:
        return True
      return False
if __name__=="__main__":
    site = wikipedia.getSite()
    
    #gvrobj = GVRObject("150939")
    #print template%gvrobj.get_data()
    #save(template%gvrobj.get_data())
    gvrlist = GVRList(bo="1", rb="67", hep="591",subb="86", wot="11")
    r="__NOTOC__"
    for o in gvrlist:
        print o
        r +=template%o.get_data()
    save(r)
    
