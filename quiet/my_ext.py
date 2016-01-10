# vim: set fileencoding=utf-8 :

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from flask import current_app

from flask import _app_ctx_stack as stack


class SQLite3(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        print("init my ext")
        app.config.setdefault('SQLITE3_DATABASE', ':memory:')
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        app.teardown_appcontext(self.teardown)

    def connect(self):
        print("make a connection")
        return 1

    def teardown(self, exception):
        print("teardown")
        ctx = stack.top
        if hasattr(ctx, 'sqlite3_db'):
            print("drop the connection")
            del ctx.sqlite3_db

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sqlite3_db'):
                ctx.sqlite3_db = self.connect()
            else:
                print("reuse")
            return ctx.sqlite3_db
