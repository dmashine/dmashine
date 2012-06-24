#!/usr/bin/env python
# -*- coding: utf-8-*-
import httplib, urllib, re
#from threading import Thread

class request:
    def __init__():
        pass

class GVRObject:
    def __init__(self, card):     
        self._card = card
        self._conn = httplib.HTTPConnection("textual.ru")
        self._params = urllib.urlencode({'card': card})
        self._headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        self._data={}
        self._conn.request("POST", "/gvr/index.php", self._params, self._headers)
        response = self._conn.getresponse()
        print self._card, response.status, response.reason
        lines = [l.decode("windows-1251") for l in response.read().splitlines()]

        for l in lines:
            if l.find('class="cardv"')>0:
                #s = re.split('<.+?>', l)
                key=""
                for s in re.split('<.+?>', l):
                    if s<>"":
                        #print s
                        if key<>"":            
                            self._data[key]=s
                        else:
                            key=s
    def test(self):
        print "GVRObject "+self._card
        for l in self._data:
            print l+": "+self._data[l]
    def __del__(self):
        self._conn.close()
class GVRList:
    def __init__(self, bo="", rb="", subb="", hep="", wot="", name="", num="", loc=""):
        #http://textual.ru/gvr/index.php?bo=1&rb=68&subb=0&hep=0&wot=11&name=&num=&loc=&s=%CF%EE%E8%F1%EA
        self.conn = httplib.HTTPConnection("textual.ru")
        self.params = urllib.urlencode({'bo': bo, "rb":rb, "subb":subb, "hep":hep, "wot": wot, "name":name, "num":num, "loc":loc})
        self.headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        self.data=[]
        self.conn.request("POST", "/gvr/index.php", self.params, self.headers)
        response = self.conn.getresponse()
        print response.status, response.reason
        lines = [l.decode("windows-1251") for l in response.read().splitlines()]
        for l in lines:
            b=l.find('/gvr/index.php?card=')
            if b>0:
                self.data+=[l[b+20:l.find('&',b)]]
       #self.test()
    def test(self):
        for l in self:
            print ">"+l
    def __iter__(self):
        return self
    def next(self): #__next__() in >3.0
        if len(self.data) == 0:
          raise StopIteration	
        return self.data.pop(0)
    def __del__(self):
        self.conn.close()
if __name__=="__main__":
    gvrobj = GVRObject("153573")
    gvrobj.test()
    gvrlist = GVRList(bo="1", rb="68", wot="11")
    for o in gvrlist:
        gvrobj = GVRObject(o)
        gvrobj.test()
    
