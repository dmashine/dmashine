#!/usr/bin/env python
# -*- coding: utf-8-*-
"""Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware.
Для длинных списков:
        <div style="height:200px; overflow:auto; padding:3px"></div>"""

import sqlite3

class Storage(object):
    """ Interface to sqlite."""
    def __new__(cls):
        """Makes it singleton"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Storage, cls).__new__(cls)
        return cls.instance

    def __init__(self, name = "articles.db"):
        self.quote = lambda s: s.replace(" ", "_").replace('"', "'")
        self.conn = sqlite3.connect(name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, check_same_thread = False)
        self.cursor = self.conn.cursor()
        print "Connection started %s " % self.cursor
    
    def create(self, table, col):
        """Create table with columns col"""
        c = ", ".join(["%s %s" % (_, col[_]) for _ in col])
        s = '''CREATE TABLE IF NOT EXISTS %s (%s)''' % (table, c)
        self.cursor.execute(s)
        self.conn.commit()
    
    def insert(self, table, values):
        """Insert a row of values to table"""
        try:
            v = u", ".join([u"\""+self.quote(u"%s" % s)+u"\"" for s in values])
            s = u"INSERT INTO %s VALUES (%s);" % (table, v)
            self.cursor.execute(s)
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
        # А если ошибка sqlite.ProgrammingError Recursive
        # use of cursors not allowed. подождать и повторить
        # (просто заблокирована база )
    def findone(self, table, cond = None, what = None):
        """returns one row (columns what) from table, by condition cond.
            Cond is dict: col = value"""
        # bug here, when len(cond) > 1
        c = ""
        if what == None:
            w = "*"
        else:
            w = ", ".join(what)
        if cond:
            c = u" WHERE "
            for l in cond:
                c += "%s = \"%s\"" % (l, self.quote(cond[l]))

        s = u"SELECT %s FROM %s%s;" % (w, table, c)
        re = self.cursor.execute(s)
        return re.fetchone()

    def delete(self, table, cond = None):
        """Deletes rows from table, by condition cond.
            Cond is dict: col = value"""
        # bug here, when len(cond) > 1
        c = ""
        if cond:
            c = u" WHERE "
            for l in cond:
                c += "%s = \"%s\"" % (l, self.quote(cond[l]))
        s = u"DELETE FROM %s%s;" % (table, c)
        self.cursor.execute(s)

    def _clean(self):
        """Cleans all tables. Not used."""
        self.cursor.execute(u"DELETE FROM articles")
        self.cursor.execute(u"DELETE FROM updates")
        self.conn.commit()

    def __del__(self):
        """We can also close the connection if we are done with it.
        Just be sure any changes have been committed or they will be lost."""
        self.conn.commit()
        self.conn.close()
