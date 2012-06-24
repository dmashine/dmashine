# interface for CategoryIntersect script
# Author Drakosh <cpsoft@gmail.com>
# License GNU GPL v3 / Beerware

import httplib, urllib
class CategoryIntersect:
  # Iterator over category intersection. uses toolserver to get a list.
  # TODO multiple categories handling
  # TODO enhace
  def __init__(self, basecat, tagcat, tagdeep='5', basedeep='5', wikilang='ru', wikifam = '.wikipedia.org'):
    self.conn = httplib.HTTPConnection("toolserver.org")
    params = urllib.urlencode({'wikilang': wikilang, 'wikifam': wikifam, 'basecat': basecat, 'tagcat': tagcat, 'format': 'wiki', 'tagdeep':tagdeep, 'basedeep':basedeep})
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}

    self.conn.request("POST", "/~daniel/WikiSense/CategoryIntersect.php", params, headers)
    response = self.conn.getresponse()
    print tagcat, response.status, response.reason
    self.lines = [l.decode("utf-8", "ignore") for l in response.read().splitlines()]
  def __iter__(self):
    return self
  def next(self): #__next__() in >3.0
    if len(self.lines) == 0:
      raise StopIteration	
    data = self.lines.pop(0)
    if data.find(u"Database Error")>0: # check for database error	
      raise CategoryIntersectException
    return data[data.find("[[")+2:data.find("]]")] # get article name
  def __del__(self):
    self.conn.close()

class CategoryIntersectException(Exception):
  pass
