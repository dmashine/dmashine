#!/usr/bin/env python
# -*- coding: utf-8-*-
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware
import httplib, urllib
""" Helper class to read lines with httplib
    
"""
class httphelp:
    def __init__(self):
        pass
    def lines(self):
        self.conn = httplib.HTTPConnection(self.server)
        p = urllib.urlencode(self.parameters)
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}

        self.conn.request("POST", self.scriptname, p, headers)
        response = self.conn.getresponse()
        #print response.status, response.reason
        return [l.decode(self.codepage, "ignore") for l in response.read().splitlines()]
    def __del__(self):
        self.conn.close()
