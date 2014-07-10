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
    def __init__(self, basecat, tagcat, depth='12', \
                    lang='ru', project='wikipedia'):
        self.articles = []
        if type(tagcat) == type(""):
            catlist = [tagcat]
        else:
            catlist = tagcat
        for tag in catlist: # Переделать, этот скрипт понимает несколько категорий
            tag = tag.encode('utf-8', 'ignore')
            conn = httphelp()
            conn.server = "tools.wmflabs.org"
            conn.scriptname = "/catscan2/quick_intersection.php"
            conn.parameters = {'cats': '%s\r\n%s' % (basecat, tag),  \
                               'depth': depth,                       \
                               'format': 'wiki',                     \
                               'lang': lang,                         \
                               'max': 30000,                         \
                               'ns': '0',                            \
                               'project': project,                   \
                               'start': '0',                         \
                               'redirects' : ''}
            conn.codepage = "utf-8"
            lines = conn.lines(method="GET")
            while len(lines) != 0:
                data = lines.pop(0) # this deletes item.
                if data.find(u"Database Error") > 0: # check for db error
                    # do i need this?
                    raise CategoryIntersectException(u"Database error")
                if (data.find("[[") == -1) or (data.find("]]") == -1) \
                    or (data.find("Category") > 1):
                    continue
                d = data[data.find("[[")+2:data.find("]]")]
                d = d[:d.find("|")]
                if not d in self.articles:
                    self.articles += [d]
        self.articles.sort()

        #if self.articles == []:
        #    raise CategoryIntersectException
        
    def __iter__(self):
        return self.articles.__iter__()

    def __len__(self):
        return len(self.articles)
        
    def next(self): #__next__() in >3.0
        """Returns next article in intersection"""
        if len(self.articles) == 0:
            raise StopIteration
        return self.articles.pop(0)

class CategoryIntersectException(Exception):
    """just exception"""
    pass

if __name__ == "__main__":
    # test
    ci = CategoryIntersect('Википедия:Статьи для срочного улучшения', [u'Музыка'])
    for name in ci:
        print name
