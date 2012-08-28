#!/usr/bin/env python
# -*- coding: utf-8 -*-
# interface for OpenStreetmap API
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware

import urllib
from xml.dom.minidom import parseString

class OSMAPIException(Exception):
    """Just exception"""
    pass
  
class search:
    """Searches openstreetmap database"""
    def __init__(self, s):
        self._s = urllib.urlencode({"q":s.encode("UTF-8"), "format":"xml", "addressdetails":1, "type":"water", "email":"cpsoft@gmail.com"})
        query = urllib.urlopen('http://nominatim.openstreetmap.org/search?%s'%self._s)
        data = query.read()
        query.close()
        dom = parseString(data)

        xmlTag = dom.getElementsByTagName('place')
        
        self._data = {}
        self._data[u"city"] = ""
        if len(xmlTag) == 1:
            # collect all attributes from attribites and child nodes to data
            attr = xmlTag[0].attributes
            for i in range(0, attr.length):
                self._data[attr.item(i).name] = attr.item(i).value
            for c in xmlTag[0].childNodes:
                self._data[c.tagName] = c.childNodes[0].data
        if self._data == {}:
            # no data collected
            raise OSMAPIException
    def get_data(self):
        if self._data != {}:
            return self._data
        else:
            raise OSMAPIException
if __name__ == "__main__":
    a = search(u"Шотозеро")
    for d in a.get_data():
        print "%s: %s" % (d, a.get_data()[d])
