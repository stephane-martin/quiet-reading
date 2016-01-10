# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from flask import make_response, render_template
from flask_restful import Resource
from flask.ext.login import login_required, current_user

class Articles(Resource):

    @login_required
    def get(self, article_id=None):
        return make_response(render_template('hello.html'), 200, {'Content-Type': 'text/html; charset=utf-8'})
