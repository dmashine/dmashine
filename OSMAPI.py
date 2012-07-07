#!/usr/bin/env python
# -*- coding: utf-8 -*-
# interface for OpenStreetmap API
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware

import urllib
from xml.dom.minidom import parseString

class search:
    def __init__(self, s):
        self._s=urllib.urlencode({"q":s.encode("UTF-8"), "format":"xml", "addressdetails":1, "type":"water"})
        file = urllib.urlopen('http://nominatim.openstreetmap.org/search?%s'%self._s)
        data = file.read()
        file.close()
        dom = parseString(data)

        xmlTag = dom.getElementsByTagName('place') # 
        print len(xmlTag)
        for tag in xmlTag:
            print tag.getAttribute("display_name")
            print tag.getAttribute("lat")
            print tag.getAttribute("lon")
            print tag.getElementsByTagName("administrative")[0].childNodes[0].data
            print tag.getElementsByTagName("state")[0].childNodes[0].data
            print tag.getElementsByTagName("county")[0].childNodes[0].data
            print tag.getElementsByTagName("city")[0].childNodes[0].data

if __name__=="__main__":
    s=search(u"Шотозеро")
