#!/usr/bin/env python
# -*- coding: utf-8-*-
# loads all AFI to sqlite base
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware

import catlib, wikipedia # pywikipedia and category module
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

    for a in AFI.articlesList():
        #n = quote(a)
        #cat =  ", ".join([quote(c) for c in a.categories()])
        #print a
        for cat in a.categories():
            cursor.execute(u"INSERT INTO category VALUES (\"%s\", \"%s\")" % (quote(a), quote(cat)))
    conn.commit()


re = cursor.execute("SELECT count(*) FROM category;")
print u"Всего статей: %s" % re.fetchone()

re = cursor.execute(" SELECT cat, count(*) AS c FROM category GROUP BY cat HAVING c>10 ORDER BY c DESC;")
print u"Топ категорий"
for l in cursor.fetchall():
    print u"%s: (%s)" % l

print u"Самые старые статьи <ref>Учитывается самый первый вынос КУЛ</ref>"    
re = cursor.execute(u"SELECT name ,ts FROM articles ORDER BY ts limit 20;")
for l in re.fetchall():
    print u"%s (%s)" % l

re = cursor.execute("SELECT topic, n, ts FROM updates;")
print u"Последние обновления"
for l in cursor.fetchall():
    print u"%s: (Статей %s, обновлена %s)" % l

    
conn.close()
