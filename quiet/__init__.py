# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from paste.translogger import TransLogger
from werkzeug.debug import DebuggedApplication
from werkzeug.contrib.fixers import ProxyFix
import cherrypy

from flask import Flask
from flask_restful import Api

from .resources.hello import HelloWorld
from .resources.cleaning import Cleaning
from .resources.ui import UI
from .resources.articles import Articles
from .resources.analyzing import Analyzing
from .config import config


application = Flask('quiet', static_url_path='/static', static_folder='static', template_folder='templates')
application.redis_conn = None
api = Api(application)

# api.add_resource(Foo, '/Foo', '/Foo/<str:id>')
api.add_resource(HelloWorld, '/hello')
api.add_resource(Cleaning, '/cleaning')
api.add_resource(Analyzing, '/analyzing')
api.add_resource(Articles, '/articles', '/articles/', '/articles/<article_id>')
api.add_resource(UI, '/')


def main():
    app = application
    config.init_app(app)


    if config.EXECUTE_ENV == "DEV":
        app = DebuggedApplication(TransLogger(app), evalex=False)
    else:
        app.wsgi_app = ProxyFix(app.wsgi_app)

    cherrypy.tree.graft(app, config.APPLICATION_ROOT)
    cherrypy.config.update({
        'engine.autoreload.on': config.CHERRY['autoreload'],
        'log.screen': config.CHERRY['print_logs'],
        'server.socket_port': config.CHERRY['socket_port'],
        'server.socket_host': config.CHERRY['socket_host'],
        'server.socket_queue_size': config.CHERRY['queue_size'],
        'server.socket_timeout': config.CHERRY['socket_timeout'],
        'server.thread_pool': config.CHERRY['n_threads']
    })

    cherrypy.engine.start()
    cherrypy.engine.block()
