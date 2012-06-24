#!/usr/bin/env python
# -*- coding: utf-8-*-
import httplib, urllib, re
#from threading import Thread

class request:
    def __init__():
        pass

class GVRException(Exception):
    pass

class GVRObject:
    """Represents object of GVR site."""    
    def __init__(self, card):     
        self._card = card
        self._conn = httplib.HTTPConnection("textual.ru")
        self._params = urllib.urlencode({'card': card})
        self._headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        self._data={}
        self._conn.request("POST", "/gvr/index.php", self._params, self._headers)
        response = self._conn.getresponse()
        #print self._card, response.status, response.reason
        lines = [l.decode("windows-1251") for l in response.read().splitlines()]

        for l in lines:
            if l.find('class="cardv"')>0:
                key=""
                for s in re.split('<.+?>', l):
                    if s<>"":
                        if key<>"":            
                            self._data[key]=unicode(s)
                        else:
                            key=unicode(s)
    def get_data(self):
        return self._data
    def __repr__(self):
        return u"GVRObject "+self._card+u"\r"
    def __del__(self):
        self._conn.close()
class GVRList:
    """Represents list of GVR objects.
        init parameters as in official site, may be omitted"""
    def __init__(self, bo="", rb="", subb="", hep="", wot="", name="", num="", loc="", start=0):
        # http://textual.ru/gvr/index.php?bo=1&rb=68&subb=0&hep=0&wot=11&name=&num=&loc=&s=%CF%EE%E8%F1%EA
        self.conn = httplib.HTTPConnection("textual.ru")
        self.params = urllib.urlencode({'bo': bo, "rb":rb, "subb":subb, "hep":hep, "wot": wot, "name":name, "num":num, "loc":loc, "start":start})
        self.headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        self._data=[]
        self.conn.request("POST", "/gvr/index.php", self.params, self.headers)
        response = self.conn.getresponse()
        print response.status, response.reason, start
        lines = [l.decode("windows-1251") for l in response.read().splitlines()]
        for l in lines:
            b=l.find('/gvr/index.php?card=')
            if b>0:
                self._data+=[l[b+20:l.find('&',b)]]
            if l.find(u'следующая страница результатов')>1: # results divided into pages.
                self._data+=GVRList(bo, rb, subb, hep, wot, name, num, loc, start+200).get_data()
       #self.test()
    def test(self):
        for l in self:
            print ">"+l
    def get_data(self):
        return self._data
    def __iter__(self):
        return self
    def next(self): #__next__() in >3.0
        if len(self._data) == 0:
          raise StopIteration	
        return GVRObject(self._data.pop(0))
    def __del__(self):
        self.conn.close()
if __name__=="__main__":
    #gvrobj = GVRObject("150939")
    #print gvrobj
    #print u"Название: %s"%gvrobj.get_data()[u"Название"]
    gvrlist = GVRList(bo="1", rb="67", subb="86", wot="11")
    for o in gvrlist:
        print o
        print u"Название: %s"%o.get_data()[u"Название"]
    
