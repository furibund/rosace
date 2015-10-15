#!/usr/bin/env python
_DEBUG = True

import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.web
import tornado.websocket
from tornado.options import define, options, parse_command_line

import json
import time
from datetime import datetime
from functools import wraps
from os import getpid
from os.path import dirname, join, realpath
from uuid import uuid4

from lib.rosace.rosace import Rosace


define('root_dir', default=dirname(realpath(__file__)), help='DOCUMENT_ROOT', type=str)
define('hostname', default='127.0.0.1', help='run on the given host', type=str)
define('port', default=9000, help='run on the given port', type=int)
define('morph_interval', default=5000, help='interval of morphing', type=int)
define('number_of_corollas', default=6, help='number of corollas', type=int)
define('number_of_petals', default=24, help='number of petals of outer corolla', type=int)



def timethis(func):
    '''
    Decorator that reports the execution time.
    From: http://chimera.labs.oreilly.com/books/1230000000393/ch09.html#_problem_144
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper



class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.redirect('./rosace')



class RosaceHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render(
            'rosace.html'
        ,   hostname=options.hostname
        ,   port=options.port
        ,   morph_interval=options.morph_interval
        )



class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
        self.id_s = str(uuid4()).replace('-', '')


    def check_origin(self, origin):
        return True


    def open(self, *args):
        self.stream.set_nodelay(True)
# - websocket management - #
        if self not in app.ws_D.values():
            app.ws_D[self.id_s] = self
        tornado.log.app_log.info('WebSocket connection opened for ID %s' % (self.id_s))
# - send first data package to new client without deleting senderData - #
        app.send_data(False)


    def on_message(self, msg_JSON):
        '''
        The message-recieved-from-client handler.
        '''
        msg_D = json.loads(msg_JSON)
        tornado.log.app_log.info("Client sent a message: %s" % (msg_D))


    def on_close(self):
        del(app.ws_D[self.id_s])



class Application(tornado.web.Application):
    def __init__(self):
        self.ws_D = {}
        self.rosace = Rosace(300, options.number_of_corollas, options.number_of_petals)
        self.senderData = {
            'datetime':     '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
        ,   'rosace':       self.rosace.repr()
        }

        self.data_sender = tornado.ioloop.PeriodicCallback(self.send_data, options.morph_interval)
        self.data_sender.start()
        tornado.log.app_log.info('data_sender started')

        self.rosemorph = tornado.ioloop.PeriodicCallback(self.morph_rosace, options.morph_interval)
        self.rosemorph.start()
        tornado.log.app_log.info('rosemorph started')

        handlers = [
            (r'/', RosaceHandler)
#       ,   (r'/rosace', RosaceHandler)
        ,   (r'/ws', WebSocketHandler)
        ]
        settings = {
            'template_path': join(options.root_dir, 'template')
        ,   'static_path': join(options.root_dir, 'static')
        ,   'xheaders': True
        }
        tornado.web.Application.__init__(self, handlers, **settings)


    @timethis
    def morph_rosace(self):
        self.rosace.morph()
        self.senderData['rosace'] = self.rosace.repr()
        tornado.log.app_log.info('Rosace morphed')


    def send_data(self, clearData=True):
        self.senderData['datetime'] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
        for ws in self.ws_D.values():
            ws.write_message(json.dumps(self.senderData))
        tornado.log.app_log.info('Message sent to %d clients' % len(self.ws_D))
        # tornado.log.app_log.info(self.senderData)
        if clearData:
            self.senderData = {}



if __name__ == '__main__':
    parse_command_line()
    app = Application()
    tornado.log.app_log.info(' *** rosace-app started on port %d with pid %d ***' % (options.port, getpid()))
    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
