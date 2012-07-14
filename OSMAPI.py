#!/usr/bin/env python
# -*- coding: utf-8 -*-
# interface for OpenStreetmap API
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware

import urllib
from xml.dom.minidom import parseString

class search:
    def __init__(self, s):
        self._s=urllib.urlencode({"q":s.encode("UTF-8"), "format":"xml", "addressdetails":1, "type":"water", "email":"cpsoft@gmail.com"})
        file = urllib.urlopen('http://nominatim.openstreetmap.org/search?%s'%self._s)
        data = file.read()
        file.close()
        dom = parseString(data)

        xmlTag = dom.getElementsByTagName('place')
        
        self._data={}
        if len(xmlTag) == 1:
            # collect all attributes forom attribites and child nodes to data
            attr=xmlTag[0].attributes
            for i in range(0, attr.length):
                self._data[attr.item(i).name] = attr.item(i).value
            for c in xmlTag[0].childNodes:
                self._data[c.tagName] = c.childNodes[0].data
        else:
            if (len(xmlTag) == 0) and (s.find("-")>0 or s.find("-")>0):
                # no data found. maybe incorrect name.
                print u"Данных не найдено, включаю интеллектуальный поиск"
                s2=s.replace("-","").replace(" ","")
                self._data = search(s2).get_data()
                if self._data<>{}:
                    print u"найдено!"
    def get_data(self):
        return self._data
if __name__=="__main__":
    s=search(u"Шотозеро")
    for d in s.get_data():
        print "%s: %s"%(d, s.get_data()[d])
