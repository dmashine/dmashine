#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import gvr, OSMAPI

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
 |Позиционная карта 1      = 
 |Позиционная карта 2      = 
 |Категория на Викискладе  = 
}}
'''%(Название)s''' — озеро в России, %(state)s, %(county)s, %(city)s. Площадь водоёма %(Площадь водоёма)s км²

Описание местоположения — %(Местоположение)s

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
    a=0
    gvrlist=[gvr.GVRObject("150490")]
    for gvrobj in gvrlist:
        try:
            name=gvrobj.get_data()[u"Название"]
            # print name
            # TODO: Собрать все варианты названия из gvrobj и последовательно искать в OSMAPI
            osm=OSMAPI.search(name)
        
            d=gvrobj.get_data()
            d.update(osm.get_data())
            d["lat_deg"], d["lat_min"], d["lat_sec"] = decdeg2dms(float(d["lat"]))
            d["lon_deg"], d["lon_min"], d["lon_sec"] = decdeg2dms(float(d["lon"]))
            a+=1
            for i in d:
                print "%s: %s"%(i, d[i])
            print a
            print template%d
        except OSMAPI.OSMAPIException:
            pass
