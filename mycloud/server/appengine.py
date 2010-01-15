from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import algo
import urllib
import string

def myrot13(input):
    a = "12345abcdefghijklmABCDEFGHIJKLM"
    b = "98760nopqrstuvwxyzNOPQRSTUVWXYZ"
    return input.translate(string.maketrans(a+b, b+a))

def mydecode(key, hint, ptr):
    src = urllib.quote(key)
    dest = '%s\t%d\t%s\n' % (src, ptr, hint.replace(" ", "_"))
    return myrot13(dest)

def myencode(key):
    return myrot13(key)

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        file = open("index.html", "r")
        self.response.out.write(file.read())
        file.close()

class QuanPin(webapp.RequestHandler):
    def get(self, keyb):
        self.response.headers['Content-Type'] = 'text/plain'
        algo.parse("__setmode=quanpin")
        algo.parse("__setgae=1")
        for k, h, v in algo.parse(myencode(keyb)):
            self.response.out.write(mydecode(k,h,v))

class ShuangPinAbc(webapp.RequestHandler):
    def get(self, keyb):
        self.response.headers['Content-Type'] = 'text/plain'
        algo.parse("__setmode=abc")
        algo.parse("__setgae=1")
        for k, h, v in algo.parse(myencode(keyb)):
            self.response.out.write(mydecode(k,h,v))

class ShuangPinMs(webapp.RequestHandler):
    def get(self, keyb):
        self.response.headers['Content-Type'] = 'text/plain'
        algo.parse("__setmode=ms")
        algo.parse("__setgae=1")
        for k, h, v in algo.parse(myencode(keyb)):
            self.response.out.write(mydecode(k,h,v))

application = webapp.WSGIApplication([
                                     ('/', MainPage),
                                     ('/qp/(.*)', QuanPin),
                                     ('/abc/(.*)', ShuangPinAbc),
                                     ('/ms/(.*)', ShuangPinMs),
                                         ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
