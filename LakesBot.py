#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import gvr, OSMAPI
import wikipedia
from httphelp import *

template = u"""{{Озеро
 |Название                 = %(Название)s
  |Национальное название   = %(Названия)s
 |Изображение              = 
  |Подпись                 = 
  |lat_dir = N|lat_deg =  %(lat_deg)0d |lat_min = %(lat_min)0d|lat_sec = %(lat_sec)0d
  |lon_dir = E|lon_deg =  %(lon_deg)0d |lon_min = %(lon_min)0d|lon_sec = %(lon_sec)0d
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
 |Позиционная карта 1      = Россия Республика Карелия
 |Позиционная карта 2      = Россия Карелия %(county)s
 |Категория на Викискладе  = 
}}
'''%(Название)s''' — озеро в России, %(state)s, %(county)s, %(city)s. Площадь водоёма %(Площадь водоёма)s км²

Описание местоположения: %(Местоположение)s

%(Реки)s
== Данные водного реестра ==
По данным геоинформационной системы водохозяйственного районирования территории РФ, подготовленной Федеральным агентством водных ресурсов<ref name='МПР России'>{{cite web|url=http://textual.ru/gvr/index.php?card=%(card)s|title=Государственный водный реестр РФ: %(Название)s|accessdate=%(accessdate)s}}</ref>
* Код водного объекта — %(Код водного объекта)s;
* Бассейновый округ — %(Бассейновый округ)s;
* Речной бассейн — %(Речной бассейн)s;
* Речной подбассейн — %(Речной подбассейн)s;
* Код по гидрологической изученности (ГИ) — %(Код по гидрологической изученности)s;
* Номер тома по ГИ — %(Номер тома по ГИ)s;
* Выпуск по ГИ — %(Выпуск по ГИ)s.

{{tl|Непроверенное озеро}}
== Примечания == 
{{примечания}} 

== Ссылки == 
* {{Водный реестр}}
* [http://nominatim.openstreetmap.org/details.php?place_id=%(place_id)s Данные базы] [[OpenStreetMap]]

[[:Категория:Озёра Карелии]]
<br clear="all">
"""
def decdeg2dms(dd):
    # http://stackoverflow.com/questions/2579535/how-to-convert-dd-to-dms-in-python
    mnt,sec = divmod(dd*3600,60)
    deg,mnt = divmod(mnt,60)
    return deg,mnt,sec
if __name__=="__main__":
    #gvrlist = gvr.GVRList(bo="1", rb="67", hep="591",subb="86", wot="11")
    gvrlist = gvr.GVRList(bo="1", wot="11")
    a=0
    #gvrlist=[gvr.GVRObject("150490")]
    site = wikipedia.getSite()
    for gvrobj in gvrlist:
        try:
            d=gvrobj.get_data()
            name=d[u"Название"]
            osm=None
            try:
                osm=OSMAPI.search(name)
            except OSMAPI.OSMAPIException: # first name isn`t found, lets try other
                #print u"%s не найдено, перебор вариантов"%name
                for s in gvrobj.get_data()[u"Названия"].split(","):
                    try:
                        osm=OSMAPI.search(s.strip())
                        #print u"Найден вариант %s"%s
                        break
                    except OSMAPI.OSMAPIException:
                        pass
                if osm==None:
                    raise OSMAPI.OSMAPIException
            except IOError:
                print "%s ioerror, pass"%name
                pass
            d[u"state"] = ""
            d.update(osm.get_data())
            print name
            print d[u"Площадь водоёма"]
            print d[u"Водосборная площадь"]
            print d[u"state"]
            d["lat_deg"], d["lat_min"], d["lat_sec"] = decdeg2dms(float(d["lat"]))
            d["lon_deg"], d["lon_min"], d["lon_sec"] = decdeg2dms(float(d["lon"]))
            a+=1
            if d[u"Площадь водоёма"] == "0" or d[u"Площадь водоёма"] == "999":
                print "Найдена неверная площадь водоема"
                d[u"Площадь водоёма"][1] == "Н/Д"
            if d[u"Водосборная площадь"] == "0" or d[u"Водосборная площадь"] == "999":
                print "Найдена неверная Водосборная площадь"
                d[u"Площадь водосбора"][1] == "Н/Д"
            #for i in d:
            #    print "%s: %s"%(i, d[i])
            #print name
            #save(site, text=(template%d), pagename=d[u"Название"],filename=u"/home/drakosh/озера/%s.txt"%d[u"Название"], dry=True, comment="Заливка озер")
        except OSMAPI.OSMAPIException:
            pass
