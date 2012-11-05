#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""Bot to load lake info from Openstreetmap and GVR"""

import gvr, OSMAPI
import wikipedia, logging, httphelp

Template = u"""{{Озеро
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

{{Непроверенное озеро}}
{{Karelia-geo-stub}}
{{hydro-stub}}

== Примечания == 
{{примечания}} 

== Ссылки == 
* {{Водный реестр}}
* [http://nominatim.openstreetmap.org/details.php?place_id=%(place_id)s Данные базы] [[OpenStreetMap]]

[[:Категория:Озёра Карелии]]
<br clear="all">
"""
def decdeg2dms(dd):
    """" http://stackoverflow.com/questions/2579535/how-to-convert-dd-to-dms-in-python"""
    mnt, sec = divmod(dd*3600, 60)
    deg, mnt = divmod(mnt, 60)
    return deg, mnt, sec
    
def NumberOfSame(glist, OSMid):
    """refactor this"""
    r = 0
    for g in glist:
        if g["place_id"] == OSMid:
            r += 1
        return r

def LakesList():    
    """returns  list of lakes from Openstreetmap and GVR"""
    #gvrlist = gvr.GVRList(bo="1", rb="67", wot="11")
    gvrlist = gvr.GVRList(bo="1", rb="67", hep="591", subb="86", wot="11")
    #gvrlist.update(bo="1", rb="67", wot="11")
    #gvrlist=[gvr.GVRObject("150490")]
    
    r = []  
    
    for d in gvrlist:
        try:
            name = d[u"Название"]
            osm = None
            try:
                osm = OSMAPI.Search(name)
            except OSMAPI.OSMAPIException:
                # first name isn`t found, lets try other
                logging.debug(u"%s не найдено, перебор вариантов", name)
                for s in d[u"Названия"].split(","):
                    try:
                        osm = OSMAPI.Search(s.strip())
                        logging.debug(u"Найден вариант %s", s)
                        break
                    except OSMAPI.OSMAPIException:
                        pass
                if osm == None:
                    raise OSMAPI.OSMAPIException
            except IOError:
                logging.warning("%s ioerror, pass", name)

            d.update(osm.get_data())
            
            try:
                d["lat_deg"], d["lat_min"], d["lat_sec"] = decdeg2dms(float(d["lat"]))
                d["lon_deg"], d["lon_min"], d["lon_sec"] = decdeg2dms(float(d["lon"]))
            except (ValueError):
                d["lat_deg"], d["lat_min"], d["lat_sec"] = "", "", ""
                d["lon_deg"], d["lon_min"], d["lon_sec"] = "", "", ""
            
            if d[u"Площадь водоёма"] == "0" \
                or d[u"Площадь водоёма"] == "999":
                logging.warning(u"Найдена неверная площадь водоема")
                d[u"Площадь водоёма"][1] = "Н/Д"
            if d[u"Водосборная площадь"] == "0" \
                or d[u"Водосборная площадь"] == "999":
                logging.warning(u"Найдена неверная Водосборная площадь")
                d[u"Площадь водосбора"][1] = "Н/Д"
            r += [d]    
        except OSMAPI.OSMAPIException:
            pass
    # filter same OSM id. refactor this!
    r2 = []
    for dd in r: #NumberOfSame(glist, OSMid):
        #if NumberOfSame(r, dd["place_id"]) == 1:
        #    print ">%s, %s, %s<"%(dd, dd[u"state"], dd["place_id"])
        r2 += [dd]
        #else:
        #    logging.info(u"Дубль %s", dd)
    return r2

    
if __name__ == "__main__":
    site = wikipedia.getSite()
    a = 0
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    #gvrlist = gvr.GVRList(bo="1", rb="67", hep="591",subb="86", wot="11")
    ll = LakesList()
    for l in ll:
        print ">%s, %s, %s<"%(l, l[u"state"], l["place_id"])
        if l[u"state"].find(u"Карел") > 0:
            a += 1
            logging.info(u"[%s] Название %s, Регион %s OSM %s GVR %s", a, l[u"Название"], l["state"], l["place_id"], l[u"Код водного объекта"])
            httphelp.save(site, text=(Template%l), \
                 pagename=l[u"Название"], \
                 filename=u"/home/drakosh/озера/%s.txt"%l[u"Название"],\
                 dry=True, comment="Заливка озер")
