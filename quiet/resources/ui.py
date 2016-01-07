# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import json
from flask import make_response, render_template, current_app, url_for, redirect
from flask_restful import Resource, reqparse, inputs
import requests

from . import make_parser, get_assets_urls


class UI(Resource):

    def get(self):
        return self._do()

    def post(self):
        return self._do()

    def _do(self):
        args = make_parser().parse_args()
        if args.target or args.h:
            subrequest_args = {}
            if args.target:
                subrequest_args['target'] = args.target
            elif args.h:
                subrequest_args['h'] = args.h
            try:
                resp = requests.post(url_for('cleaning', _external=True), json=subrequest_args, headers={
                    'Accept': 'application/json'
                })
            except requests.RequestException:
                return make_response(render_template('ui.html', assets=get_assets_urls()), 200, {'mimetype': 'text/html'})
            resp = resp.json()
            return redirect("{}#{}".format(url_for('ui'), resp['h']))

        else:
            print(get_assets_urls())
            return make_response(render_template('ui.html', assets=get_assets_urls()), 200, {'mimetype': 'text/html'})

