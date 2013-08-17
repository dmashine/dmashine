#!/usr/bin/env python
# -*- coding: utf-8-*-
""" loads all AFI to sqlite base, collects stats
 Author Drakosh <cpsoft@gmail.com>
 License GNU GPL v3 / Beerware """

import catlib, wikipedia, sys # pywikipedia and category module
import sqlite3

QUOTE = lambda s: s.titleWithoutNamespace().replace(" ", "_").replace('"', "'")

class AllAFI:
    """module for AFI stats update"""
    def __init__(self, action):
        self.action = action
        self.site = wikipedia.getSite()
        self.afi = catlib.Category(self.site, u'Категория:Википедия:Статьи для срочного улучшения')
        self.afi_list = self.afi.articlesList()
        self.conn = sqlite3.connect('articles.db')
        self.cursor = self.conn.cursor()        
    def load_all(self):
        """Loads all articles for improvement to sqlite table"""
        # Move table creation to Cache module
        try:  # Create table
            self.cursor.execute(u'''CREATE TABLE category (name TEXT, cat TEXT)''')
            print "table created"
        except sqlite3.Error:
            #table already created.
            self.cursor.execute(u"DELETE FROM category")

        for a in self.afi_list:
            print a
            for cat in a.categories():
                self.cursor.execute(u"INSERT INTO category VALUES (\"%s\", \"%s\")" % (QUOTE(a), QUOTE(cat)))
        self.conn.commit()
        # now clear articles table from non-actual articles
        re = self.cursor.execute(u"SELECT name FROM articles;")
        AFIListQ = [QUOTE (a) for a in self.afi_list]
        for l in re.fetchall():
            if l[0] not in AFIListQ:
                print l[0]
                self.cursor.execute(u"DELETE FROM articles WHERE name = \"%s\"" % l[0])
        self.conn.commit()

    def update_stats(self):
        """prints stats to wikipedia page"""
        text = ""
        n1 = self.cursor.execute("SELECT count(DISTINCT name) FROM category;").fetchone()[0]
        n2 = self.cursor.execute("SELECT count(*) FROM articles;").fetchone()[0]
        text += u"Всего статей на КУЛ: '''%s''', статей в базе бота '''%s''' \r\n" % (n1, n2)

        re = self.cursor.execute(" SELECT cat, count(*) AS c FROM category GROUP BY cat HAVING c>10 ORDER BY c DESC;")
        text += u"== Топ категорий <ref>Категории, в которых более 10 статей на улучшении, количество статей указано в скобках</ref> == \r\n"
        for l in self.cursor.fetchall():
            text += u"* [[:Категория:%s|]]: (%s) \r\n" % l

        text += u"== Самые старые статьи <ref>Учитывается самая первая номинация КУЛ</ref> == \r\n"
        re = self.cursor.execute(u"SELECT name ,ts FROM articles ORDER BY ts limit 20;")
        for l in re.fetchall():
            text += u"* [[%s]] (%s) \r\n" % l

        re = self.cursor.execute("SELECT topic, topic, n, ts FROM updates ORDER BY n DESC;")
        text += u"== Последние обновления == \r\n"
        for l in self.cursor.fetchall():
            text += u"* [[Википедия:К улучшению/Тематические обсуждения/%s|%s]]: (Статей %s, обновлена %s) \r\n" % (l)
        text += u"== Примечания ==\r\n{{примечания}}"
            
        self.conn.close()
        P = wikipedia.Page(self.site, u"Википедия:К улучшению/Тематические обсуждения/Статистика")
        P.put(text, u"Обновление статистики", botflag = True)

    def run(self):
        """entry point"""
        if self.action == "all":
            self.load_all()
        self.update_stats()

if __name__ == "__main__":
    A = AllAFI(sys.argv[1])
    A.run()
