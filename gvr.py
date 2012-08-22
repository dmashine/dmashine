#!/usr/bin/env python
# -*- coding: utf-8-*-
import re, wikipedia, datetime
from httphelp import *

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
  |Регион                  = Карелия
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
'''%(Название)s''' — озеро в России, республика Карелия. Местоположение - %(Местоположение)s. Площадь водоёма %(Площадь водоёма)s км²

%(Реки)s
== Данные водного реестра ==
По данным геоинформационной системы водохозяйственного районирования территории РФ, подготовленной Федеральным агентством водных ресурсов<ref name='МПР России'>{{cite web|url=http://textual.ru/gvr/index.php?card=%(card)s|title=Государственный водный реестр РФ: %(Название)s|accessdate=%(accessdate)s}}</ref>
* Код водного объекта — %(Код водного объекта)s
* Бассейновый округ — %(Бассейновый округ)s
* Речной бассейн — %(Речной бассейн)s
* Речной подбассейн — %(Речной подбассейн)s
* Код по гидрологической изученности (ГИ) — %(Код по гидрологической изученности)s
* Номер тома по ГИ — %(Номер тома по ГИ)s
* Выпуск по ГИ — %(Выпуск по ГИ)s

{{tl|Непроверенное озеро}}
== Примечания == 
{{примечания}} 

== Ссылки == 
* {{Водный реестр}}

[[:Категория:Озёра Карелии]]
<br clear="all">
"""

class GVRException(Exception):
    pass

class GVRObject:
    """Represents object of GVR site."""    
    def __init__(self, card):
        conn = httphelp()
        conn.server     = "textual.ru"
        conn.codepage   = "windows-1251" 
        conn.scriptname = "/gvr/index.php"
        conn.parameters = {'card': card}    
    
        self._card = card
        self._data={}
        self._data[u"Названия"] = ""
        self._data[u"Вытекает"] = ""
        self._data[u"Реки"] = ""
        self._data[u"Площадь водоёма"] = ""
        self._data[u"Водосборная площадь"] = ""
        self._data[u"card"] = card
        self._data[u"accessdate"] = datetime.date.today()

        for l in conn.lines():
            if l.find('class="cardv"')>0:
                key=""
                for s in re.split('<.+?>', l):
                    if s<>"":
                        if key<>"":
                            # workarounds for different keys
                            if key == u"Площадь водоёма" or key == u"Водосборная площадь":
                                if s.find("0")<>0 and s.find("999")<>0:
                                    # data errors
                                    self._data[key] = unicode(s[:-9])                                
                                else:
                                    self._data[key] = ""
                            elif key == u"Название" and s.find("(")>0:
                                self._data[key] = unicode(s[:s.find("(")-1])
                                self._data[u"Названия"] = unicode(s[s.find("(")+1:s.find(")")])
                            elif key == u"Вытекает" and s.find(u"река")==0:
                                if s.find("(") >0:
                                    self._data[u"Вытекает"] = unicode(s[5:s.find("(")])
                                else:
                                    self._data[u"Вытекает"] = unicode(s[5:])
                            elif key == u"Бассейновый округ" or key == u"Речной бассейн" or key == u"Речной подбассейн":
                                if s.find("(") >0:
                                    self._data[key]=unicode(s[:s.rfind("(")])
                            else: # get it 
                                self._data[key]=unicode(s)
                        else: #first string in response is key, second is parameter
                            key=unicode(s)
            if l.find(u'<td valign="top"><a href="')>=0:
                    # get rivers from page
                    s=u"\nВ озеро впадают: "
                    for l in re.split( "<.+?>", l):
                        if l=="":
                            continue
                        a=l.find(" ")+1 # wikification
                        b=l.find("(")-1
                        if b==-2: b=len(l)
                        s+=l[:a]+u"[["+l[a:b]+u"]]"+l[b:]+", "
                    s=s[:-2]+"."
                    self._data[u"Реки"] = s
    def get_data(self):
        return self._data
    def __repr__(self):
        return u"GVRObject "+self._card+u"\r"

class GVRList:
    """Represents list of GVR objects.
        init parameters as in official site, may be omitted"""
    def __init__(self, bo="", rb="", subb="", hep="", wot="", name="", num="", loc="", start=0):
        # http://textual.ru/gvr/index.php?bo=1&rb=68&subb=0&hep=0&wot=11&name=&num=&loc=&s=%CF%EE%E8%F1%EA
        conn = httphelp()
        conn.server     = "textual.ru"
        conn.codepage   = "windows-1251"
        conn.scriptname = "/gvr/index.php"
        conn.parameters = {'bo': bo, "rb":rb, "subb":subb, "hep":hep, "wot": wot, "name":name, "num":num, "loc":loc, "start":start}

        self._data=[]
        for l in conn.lines():
            b=l.find('/gvr/index.php?card=')
            if b>0:
                self._data+=[l[b+20:l.find('&',b)]]
            if l.find(u'следующая страница результатов')>1: # results divided into pages.
                self._data+=GVRList(bo, rb, subb, hep, wot, name, num, loc, start+200).get_data()
       #self.test()
    def update(self, bo="", rb="", subb="", hep="", wot="", name="", num="", loc="", start=0):
        """updates one gvrlist with other data. keeps sorted"""
        self._data + GVRList(bo, rb, subb, hep, wot, name, num, loc).get_data()
        self._data.sort()
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

if __name__=="__main__":
    site = wikipedia.getSite()
    
    gvrobj = GVRObject("150939")
    #print template%gvrobj.get_data()
    #save(template%gvrobj.get_data(), title=gvrobj.get_data()[u"Название"])
    #gvrlist = GVRList(bo="1", rb="67", hep="591",subb="86", wot="11")
    #r="__NOTOC__"
    #for o in gvrlist:
    #    print o
    #    data=o.get_data()
    #    save(site, text=(template%data), pagename=data[u"Название"],filename=u"/home/drakosh/озера/%s.txt"%data[u"Название"], dry=True, comment="Заливка озер")
    
