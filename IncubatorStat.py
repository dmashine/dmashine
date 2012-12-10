#!/usr/bin/env python
# -*- coding: utf-8-*-
""" Скрипт для обновления статистики инкубаторских вики
Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware."""

import httplib, urllib, wikipedia, catlib

site = wikipedia.getSite('incubator', 'incubator')
cat = catlib.Category(site, u"Category:Incubator:All_test_wikis")
for c in cat.subcategories():
    print c
