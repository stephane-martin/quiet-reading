# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from flask import Response, render_template
from flask_restful import Resource


class Articles(Resource):

    def get(self, article_id=None):
        return Response(render_template('hello.html'), mimetype='text/html')
