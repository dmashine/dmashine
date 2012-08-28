#!/usr/bin/env python
# -*- coding: utf-8 -*-
# interface for OpenStreetmap API
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware

"""Module for OpenStreetmap API"""

import urllib
from xml.dom.minidom import parseString

class OSMAPIException(Exception):
    """Just exception"""
    pass
  
class Search:
    """Searches openstreetmap database"""
    def __init__(self, search):
        params = urllib.urlencode({"q":search.encode("UTF-8"), \
            "format":"xml", "addressdetails":1,
            "type":"water", "email":"cpsoft@gmail.com"})
        # Change email here to yours one!
        query = urllib.urlopen('http://nominatim.openstreetmap.org/search?%s'%params)
        data = query.read()
        query.close()
        dom = parseString(data)

        xmltag = dom.getElementsByTagName('place')
        
        self._data = {}
        self._data[u"city"] = ""
        if len(xmltag) == 1:
            # collect all attributes from attribites and child nodes to data
            attr = xmltag[0].attributes
            for i in range(0, attr.length):
                self._data[attr.item(i).name] = attr.item(i).value
            for j in xmltag[0].childNodes:
                self._data[j.tagName] = j.childNodes[0].data
        if self._data == {}:
            # no data collected
            raise OSMAPIException
    def get_data(self):
        """Returns data for OSM object"""
        if self._data != {}:
            return self._data
        else:
            raise OSMAPIException
if __name__ == "__main__":
    S = Search(u"Шотозеро")
    for d in S.get_data():
        print "%s: %s" % (d, S.get_data()[d])
