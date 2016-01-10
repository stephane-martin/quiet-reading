# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from paste.translogger import TransLogger
from werkzeug.debug import DebuggedApplication
from werkzeug.contrib.fixers import ProxyFix
import waitress
import flask
from flask_restful import Api

from . import application
from . import login_manager
from .article import Article
from .user import load_user
from .config import QuietConfig
from .resources.hello import HelloWorld
from .resources.cleaning import Cleaning
from .resources.ui import UI
from .resources.articles import Articles
from .resources.analyzing import Analyzing
from .resources.opencalais import OpenCalais
from .resources.images import Images
from .resources.login import OauthLogin
from .resources.login import Logout



def setup_routing(flask_app):
    api = Api(flask_app)
    api.add_resource(HelloWorld, '/hello')
    api.add_resource(Cleaning, '/cleaning')
    api.add_resource(Analyzing, '/analyzing')
    api.add_resource(OpenCalais, '/opencalais')
    api.add_resource(Articles, '/articles', '/articles/', '/articles/<article_id>')
    api.add_resource(Images, '/images', '/images/<h>')
    api.add_resource(OauthLogin, '/login', '/login/', '/login/<provider_name>', '/login/<provider_name>/')
    api.add_resource(Logout, '/logout', '/logout/')
    api.add_resource(UI, '/', endpoint=b"index")


def main(flask_app=application):
    assert(isinstance(flask_app, flask.Flask))
    flask_app.load_config(QuietConfig)
    flask_app.setup()
    setup_routing(flask_app)
    login_manager.user_callback = load_user
    login_manager.login_view = b"oauthlogin"

    if flask_app.config['DEBUG']:
        app = DebuggedApplication(TransLogger(flask_app), evalex=False)
    else:
        app = flask_app
        app.wsgi_app = ProxyFix(app.wsgi_app)

    # http://docs.pylonsproject.org/projects/waitress/en/latest/arguments.html

    try:
        waitress.serve(
            app,
            host=flask_app.config['WAITRESS']['SOCKET_HOST'], port=flask_app.config['WAITRESS']['SOCKET_PORT'],
            threads=flask_app.config['WAITRESS']['N_THREADS'], trusted_proxy="127.0.0.1",
            url_prefix=flask_app.config['APPLICATION_ROOT']
        )
    finally:
        flask_app.dealloc()
