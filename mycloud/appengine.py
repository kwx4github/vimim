from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import algo
import urllib
import string

def myformat(key, hint, ptr):
    src = urllib.quote(key)
    a = "12345abcdefghijklmABCDEFGHIJKLM"
    b = "98760nopqrstuvwxyzNOPQRSTUVWXYZ"
    dest = src.translate(string.maketrans(a+b, b+a))
    return '%s\t%d\t%s\n' % (dest, ptr, hint.replace(" ", "_"))

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
        for k, h, v in algo.parse(keyb):
            self.response.out.write(myformat(k,h,v))

class ShuangPinAbc(webapp.RequestHandler):
    def get(self, keyb):
        self.response.headers['Content-Type'] = 'text/plain'
        algo.parse("__setmode=abc")
        algo.parse("__setgae=1")
        for k, h, v in algo.parse(keyb):
            self.response.out.write(myformat(k,h,v))

class ShuangPinMs(webapp.RequestHandler):
    def get(self, keyb):
        self.response.headers['Content-Type'] = 'text/plain'
        algo.parse("__setmode=ms")
        algo.parse("__setgae=1")
        for k, h, v in algo.parse(keyb):
            self.response.out.write(myformat(k,h,v))

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
