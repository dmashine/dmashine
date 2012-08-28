#!/usr/bin/env python
# -*- coding: utf-8-*-
# interface for CategoryIntersect script
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware
"""Class to iterate over category intersection in Wikipedia"""
from httphelp import httphelp

class CategoryIntersect:
    """Iterator over category intersection.
    Uses toolserver to get a list."""
    def __init__(self, basecat, tagcat, tagdeep='5', \
            basedeep='5', wikilang='ru', wikifam = '.wikipedia.org'):
        conn = httphelp()
        conn.server     = "toolserver.org"
        conn.scriptname = "/~daniel/WikiSense/CategoryIntersect.php"
        conn.parameters = { 'wikilang': wikilang,   \
                            'wikifam': wikifam,     \
                            'basecat': basecat,     \
                            'tagcat': tagcat,       \
                            'format': 'wiki',       \
                            'tagdeep':tagdeep,      \
                            'basedeep':basedeep}
        conn.codepage = "utf-8"
        self.lines = conn.lines()
    def __iter__(self):
        return self
    def next(self): #__next__() in >3.0
        """Returns next article in intersection"""
        if len(self.lines) == 0:
            raise StopIteration	
        data = self.lines.pop(0) # this deletes item. Is it ok?
        if data.find(u"Database Error")>0: # check for database error	
            raise CategoryIntersectException
        return data[data.find("[[")+2:data.find("]]")] # get article name

class CategoryIntersectException(Exception):
    """just esxeption"""
    pass
