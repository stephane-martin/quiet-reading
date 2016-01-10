# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from flask import Response, render_template
from flask_restful import Resource


class HelloWorld(Resource):

    def get(self):
        return Response(render_template('hello.html'), mimetype='text/html; charset=utf-8')
