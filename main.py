#!/usr/bin/env python

# Arduino LED matrix control for the Simmons LED Gym Display
# By Isaac Evans
# ine@mit.edu
# 3/25/2011

import Matrix
import Game
import LEDCharacters
import logging
import datetime
import os
import pytz

from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from google.appengine.api.urlfetch import DownloadError

#store:
scrollDelay = 10
matrixSize = (6, 6) #pixel width by height
boardAddress = '18.96.2.200'
matrix = None

class QueueEntry(db.Model):
    text = db.StringProperty(required = True)
    phone = db.StringProperty(required = True)
    datetime = db.DateTimeProperty(required = True)
    repeat = db.IntegerProperty(required = True)

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Simmons LED Control System')

class TweetManager(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Tweet handler')
#       tweet = twitter.Api().GetUserTimeline(u.get_profile().twitter_account )[0]

class SerialDisplay(webapp.RequestHandler):
    scroller = None

##    def post(self):
##        if self.request.get('msg'):
##            text = str(self.request.get('msg')).upper()
##            memcache.set('matrix', Matrix.MatrixScroller(text, matrixSize[0], matrixSize[1]), 300)
##            self.response.out.write('ok, set to ' + text)

    def get(self):
        self.scroller = memcache.get('scroller')
        self.text = ''

        if self.scroller:
            self.text = self.scroller.getText()
            if self.request.get('arduino'):
                out = ''
                a = self.scroller.getMatrix(True)
                for c in a:
                    out += str(c)
                #for row in range(self.scroller.getWidth()):
                #    for column in range(self.scroller.getHeight()):
                #        if self.scroller.getMatrix(True)[column][row]: out += '1'
                #        else: out += '0'
                self.response.out.write(out + '<br/>')
                #push this to the arduino at
                aURL = 'http://' + boardAddress + '/' + out
                try:
                    html = urlfetch.fetch(url = aURL, deadline = 3).content
                except DownloadError:
                    self.response.out.write('<b>Arduino not responding!</b>')
                #we don't care about the response

            out = self.text + '<table border=1 style="width: 600px; height: 600px;">'
            for row in range(self.scroller.getWidth()):
                out += '<tr>'
                for column in range(self.scroller.getHeight()):
                    if self.scroller.getMatrix()[column][row]:
                        out += '<td>&nbsp;</td>'
                    else: out += '<td style="background-color:black">&nbsp;</td>'
                out += '</tr>'
            out += '</table>'
            self.response.out.write(out)

            if self.request.get('move'): #execute shift
                if self.scroller.next() == None: #terminate
                    self.scroller = None
                memcache.set('scroller', self.scroller, 300)

        else: #mo matrix available
            if memcache.get('key') != None: #todo delete old one
                db.delete(memcache.get('key'))
                memcache.set('key', None)
            #what's next on the queue?
            qe = QueueEntry.all().order('-datetime').fetch(1)
            #is it time to display it? do you hate DST?
            if len(qe) == 1 and datetime.datetime(qe[0].datetime.year, qe[0].datetime.month,
                                                  qe[0].datetime.day, qe[0].datetime.hour,
                                                  qe[0].datetime.minute, qe[0].datetime.second, 0,
                                                  pytz.timezone('US/Eastern')) > getTimeEDTorEST():
                self.scroller = Matrix.MatrixScrollRepeater(qe[0].repeat, Matrix.MatrixScroller(qe[0].text, matrixSize[0], matrixSize[1]))
                self.scroller.next()
                self.scroller.next()
                memcache.set('scroller', self.scroller, 300)
                memcache.set('phone', qe[0].phone)
                memcache.set('key', qe[0].key())
            else:
                self.response.out.write('0,'*matrixSize[0]*matrixSize[1])

def whitelist(text):
    cleaned = ''
    for c in text:
        #prevent XSS just in case <> is added to LED characters. DO NOT REMOVE.
        if c in LEDCharacters.allowedChars() and c != '>' and c != '<':
            cleaned += c
    return cleaned

def getTimeEDTorEST():
    return datetime.datetime.now(pytz.timezone('US/Eastern'))

class QueueManager(webapp.RequestHandler):
    def post(self):
        #example URL: http://simmonsled.appspot.com?phone=8124617764&date=03/30/2011&time=08:30 pm&text=a&text=b&text=c&text=done&
        texts = self.request.get_all('text')

        logging.info('text: ' + str(texts))
        text = ''
        for t in texts:
            if t != 'done': text += t
        text = text.upper().encode('ascii', 'replace')
        text = text.replace('SPACE', ' ')
        text = text.replace('PERIOD', '.')
        phone = self.request.get('phone').encode('ascii', 'replace')
        text, phone = whitelist(text), whitelist(phone)
        if self.request.get('date'):
            date = self.request.get('date').split('/')
            time = self.request.get('time').split(' ')[0].split(':')
            if self.request.get('time')[:-2] == 'pm': time[0] += 12
            date = [int(x.encode('ascii', 'replace')) for x in date]
            time = [int(x.encode('ascii', 'replace')) for x in time]
            slot = datetime.datetime(date[2], date[0], date[1], time[0], time[1], 0, 0, pytz.timezone('US/Eastern'))
        else:
            slot = getTimeEDTorEST()

        logging.info('text: ' + text + '\n' +
                     'phone: ' + phone + '\n' +
                     'slot: ' + slot.strftime("%Y-%m-%d %H:%M:%S"))

        prev = QueueEntry.all().filter('datetime >', slot).order('-datetime').fetch(1) #datetime.datetime.now()
        qe = QueueEntry(text = text,
                        phone = phone,
                        datetime = slot,
                        repeat = 1) #means, repeat x times - '1' will display the message twice
        qe.put()
        self.response.out.write('message queued!')
##       self.response.out.write(qe.text + ' <br/>')
##       self.response.out.write(qe.phone + ' <br/>')
##       self.response.out.write(qe.datetime.strftime("%Y-%m-%d %H:%M:%S") + ' <br/>')
##       if len(prev) == 1:
##            self.response.out.write('prev message at ' + prev[0].datetime + ' <br/>')

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/display', SerialDisplay),
                                          ('/queue', QueueManager)],
                                         debug=True)

    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()