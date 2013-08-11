#!/usr/bin/env python
# -*- coding: utf-8-*-
# loads all AFI to sqlite base
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware

import catlib, wikipedia, sys # pywikipedia and category module
import sqlite3

SITE = wikipedia.getSite()
AFI = catlib.Category(SITE, u'Категория:Википедия:Статьи для срочного улучшения')
conn = sqlite3.connect('articles.db')
cursor = conn.cursor()
quote = lambda s: s.titleWithoutNamespace().replace(" ", "_").replace('"', "'")

def AllAFI():
    try:  # Create table
        cursor.execute(u'''CREATE TABLE category (name TEXT, cat TEXT)''')
        print "table created"
    except sqlite3.Error:
        #table already created
        cursor.execute(u"DELETE FROM category")
    
    AFIList = AFI.articlesList()
    for a in AFIList:
        #n = quote(a)
        #cat =  ", ".join([quote(c) for c in a.categories()])
        print a
        for cat in a.categories():
            cursor.execute(u"INSERT INTO category VALUES (\"%s\", \"%s\")" % (quote(a), quote(cat)))
    conn.commit()
    # now clear articles table from non-actual articles
    re = cursor.execute(u"SELECT name FROM articles;")
    AFIListQ = [quote (a) for a in AFIList]
    for l in re.fetchall():
        if l[0] not in AFIListQ:
            print l[0]
            cursor.execute(u"DELETE FROM articles WHERE name = \"%s\"" % l[0])
    conn.commit()

if len(sys.argv) >= 2:
    AllAFI()

text = ""
n1 = cursor.execute("SELECT count(DISTINCT name) FROM category;").fetchone()[0]
n2 = cursor.execute("SELECT count(*) FROM articles;").fetchone()[0]
text += u"Всего статей на КУЛ: '''%s''', статей в базе бота '''%s''' \r\n" % (n1, n2)

re = cursor.execute(" SELECT cat, count(*) AS c FROM category GROUP BY cat HAVING c>10 ORDER BY c DESC;")
text += u"== Топ категорий <ref>Категории, в которых более 10 статей на улучшении, количество статей указано в скобках</ref> == \r\n"
for l in cursor.fetchall():
    text += u"* [[:Категория:%s|]]: (%s) \r\n" % l

text += u"== Самые старые статьи <ref>Учитывается самая первая номинация КУЛ</ref> == \r\n"
re = cursor.execute(u"SELECT name ,ts FROM articles ORDER BY ts limit 20;")
for l in re.fetchall():
    text += u"* [[%s]] (%s) \r\n" % l

re = cursor.execute("SELECT topic, topic, n, ts FROM updates ORDER BY n DESC;")
text += u"== Последние обновления == \r\n"
for l in cursor.fetchall():
    text += u"* [[Википедия:К улучшению/Тематические обсуждения/%s|%s]]: (Статей %s, обновлена %s) \r\n" % (l)
text += u"== Примечания ==\r\n{{примечания}}"
    
conn.close()
P = wikipedia.Page(SITE, u"Википедия:К улучшению/Тематические обсуждения/Статистика")
P.put(text, u"Обновление статистики", botflag = True)
