#!/usr/bin/env python
# -*- coding: utf-8-*-
# interface for CategoryIntersect script
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware
"""Class to iterate over category intersection in Wikipedia"""
from httphelp import httphelp

class CategoryIntersect:
    """Iterator over category (one or list) intersection.
    Uses toolserver to get a list."""
    def __init__(self, basecat, tagcat, tagdeep='5', \
            basedeep='5', wikilang='ru', wikifam = '.wikipedia.org'):
        self.articles = []
        if type(tagcat) == type(""):
            catlist = [tagcat]
        else:
            catlist = tagcat
        for tag in catlist:
            tag = tag.encode('utf-8', 'ignore')
            conn = httphelp()
            conn.server     = "toolserver.org"
            conn.scriptname = "/~daniel/WikiSense/CategoryIntersect.php"
            conn.parameters = { 'wikilang': wikilang,   \
                                'wikifam': wikifam,     \
                                'basecat': basecat,     \
                                'tagcat': tag,          \
                                'format': 'wiki',       \
                                'tagdeep':tagdeep,      \
                                'basedeep':basedeep}
            conn.codepage = "utf-8"
            lines = conn.lines()
            while len(lines) != 0:
                data = lines.pop(0) # this deletes item.
                if data.find(u"Database Error")>0: # check for database error
                    raise CategoryIntersectException
                d = data[data.find("[[")+2:data.find("]]")]
                if not d in self.articles:
                    self.articles += [d]
        self.articles.sort()
        if self.articles == []:
            raise CategoryIntersectException
        
    def __iter__(self):
        return self.articles.__iter__()
    def next(self): #__next__() in >3.0
        """Returns next article in intersection"""
        if len(self.articles) == 0:
            raise StopIteration
        return self.articles.pop(0)

class CategoryIntersectException(Exception):
    """just exception"""
    pass
