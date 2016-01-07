# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from flask import request, make_response, render_template, current_app
from flask_restful import Resource
import requests

from ..article import Article
from . import make_parser, what_request_wants

class Analyzing(Resource):
    def _do(self):
        pass

    def get(self):
        return self._do()

    def post(self):
        return self._do()
