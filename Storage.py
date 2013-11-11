#!/usr/bin/env python
# -*- coding: utf-8-*-
"""Автор: http://ru.wikipedia.org/wiki/Участник:Drakosh
Лицензирование: GNU GPL v3 / Beerware.
"""

import sqlite3
from time import sleep

class Storage(object):
    """ Interface to sqlite."""
    def __new__(cls):
        """Makes it singleton"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Storage, cls).__new__(cls)
        return cls.instance

    def __init__(self, name = "articles.db"):
        self.quote = lambda s: s.replace(" ", "_").replace('"', "'")
        self.conn = sqlite3.connect(name, \
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,\
            check_same_thread = False)
        self.cursor = self.conn.cursor()
        print "Connection started %s " % self.cursor
    
    def execute(self, query):
        """Executes"""
        #print query
        while True: # returns if query done
            try:
                with L: # sqlite isn`t thread-safe so lets make it
                    r = self.cursor.execute(query)
                    self.conn.commit()
                return r
            except sqlite3.IntegrityError:
                return
            except sqlite3.ProgrammingError:
                print u"execute error, retry!"
                sleep(3)
    
    def create(self, table, col):
        """Create table with columns col"""
        c = ", ".join(["%s %s" % (_, col[_]) for _ in col])
        s = '''CREATE TABLE IF NOT EXISTS %s (%s)''' % (table, c)
        self.execute(s)
    
    def insert(self, table, values):
        """Insert a row of values to table"""
        v = u", ".join([u"\""+self.quote(u"%s" % s)+u"\"" for s in values])
        s = u"INSERT INTO %s VALUES (%s);" % (table, v)
        self.execute(s)

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
        re = self.execute(s)
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
        self.execute(s)

    def _clean(self):
        """Cleans all tables. Not used."""
        self.execute(u"DELETE FROM articles")
        self.execute(u"DELETE FROM updates")
        self.conn.commit()

    def __del__(self):
        """We can also close the connection if we are done with it.
        Just be sure any changes have been committed or they will be lost."""
        self.conn.commit()
        self.conn.close()
L = Lock()
